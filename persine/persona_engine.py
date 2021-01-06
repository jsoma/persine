import os
from selenium import webdriver
from datetime import datetime
import base64
import zlib
import io
from PIL import Image
from urllib.parse import urlparse, urldefrag

from .utils import simplify_source
from .bridges import YoutubeBridge
from .bridges import AmazonBridge
from .persona import Persona


class PersonaEngine:
    """PersonaEngine is used to generate personas. You can think of it as a place
        to store all of your settings.

    Args:
        height (int): Height of the browser window
        weight (int): Width of the browser window
        screenshot_scale (float): Scaling factor for saved screenshots
        screenshot (Union[str, list]): Whether screenshots are saved, and whether they go to history or to disk
        html (Union[str, list]): Whether HTML is saved, and whether it goes to history or to disk
        compress_html (boolean): Whether HTML should be compressed or not before saving to the history
        cache_dir (str): Where to save on-disk screenshots and HTML files
        data_dir (str): Root directory where persona data (Chrome profiles) are stored
        headless (boolean): Whether to start the browser in headless mode
        driver: WebDriver to use instead of starting a new one
        resume (boolean): Whether to pick up where the previous run left off.
    """

    def __init__(
        self,
        height=1200,
        width=1600,
        screenshot_scale=0.5,
        screenshot=None,
        html=None,
        compress_html=True,
        cache_dir=None,
        data_dir=None,
        headless=False,
        driver=None,
        resume=False,
    ):
        # Settings
        self.height = height
        self.width = width
        self.screenshot_scale = screenshot_scale
        self.screenshot = screenshot
        self.html = html
        self.compress_html = compress_html
        self.url_before_action = None
        self.headless = headless
        self.resume = False

        if data_dir is not None:
            self.data_dir = data_dir
        else:
            self.data_dir = os.path.join(os.getcwd(), "persona_data")
        os.makedirs(self.data_dir, exist_ok=True)

        if cache_dir is not None:
            self.cache_dir = cache_dir
        else:
            self.cache_dir = os.path.join(self.data_dir, "cache")
        os.makedirs(self.cache_dir, exist_ok=True)

        self.custom_driver = driver

    def persona(self, name=None, resume=False):
        """Initializes a persona with the given name.
        
        Returns:
            Persona: The persona initialized by the engine.
        """
        return Persona(self, name=name, resume=resume)

    def get_driver_options(self, user_data_dir=None):
        """Create the options necessary to start the appropriate
        webdriver.Chrome instance

        Returns:
            webdriver.ChromeOptions"""

        options = webdriver.ChromeOptions()

        default_args = [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--autoplay-policy=no-user-gesture-required",
        ]

        for arg in default_args:
            options.add_argument(arg)

        # If not headless, add ublock
        if self.headless:
            options.add_argument("--headless")
            options.add_argument("--mute-audio")
        else:
            # TODO this should be an option. Also, maybe no ad blocking?
            ext_path = os.path.join(
                os.path.dirname(__file__), "../extensions/ublock-origin.crx"
            )
            options.add_extension(ext_path)

        if user_data_dir:
            options.add_argument(f"user-data-dir={user_data_dir}")

        options.add_argument(f"--window-size={self.width},{self.height}")

        return options

    def launch(self, user_data_dir=None):
        """Launches a Chrome instance.
        
        Returns:
            webdriver.Chrome"""
        if self.custom_driver:
            return self.custom_driver

        options = self.get_driver_options()

        return webdriver.Chrome(options=options)

    def get_state(self, driver, url):
        """
        Get the current state of the page.

        Returns:
            dict: A representation of the current page (key, action, url, etc)
        """

        # Give everything a unique key
        key = datetime.now().strftime("%Y-%m-%d-%H.%M.%S.%f")[:-3]
        state = {
            "key": key,
            "action": url,
            "page_title": driver.title,
            "url": driver.current_url,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "url_before_action": self.url_before_action,
        }

        # Remove style tags which are like 2/3 of YouTube
        html = simplify_source(driver.page_source)

        if self.html:
            if self.html == "file" or "file" in self.html:
                source_filepath = os.path.join(self.cache_dir, f"{key}.html")
                with open(source_filepath, "w") as outfile:
                    outfile.write(html)

            if self.html == "history" or "history" in self.html:
                if self.compress_html:
                    compressed = zlib.compress(html.encode("utf-8"))
                    state["page_source"] = base64.b64encode(compressed).decode(
                        "utf-8"
                    )  # noqa: E501
                else:
                    state["page_source"] = html

        if self.screenshot:
            quality = 80
            optimize = True
            ss = self.take_screenshot(driver).convert("RGB")

            # Save to file
            if self.screenshot == "file" or "file" in self.screenshot:
                ss_filepath = os.path.join(self.cache_dir, f"{key}.jpg")
                ss.save(
                    ss_filepath, "JPEG", optimize=optimize, quality=quality
                )  # noqa: E501

            # Save to state
            if self.screenshot == "history" or "history" in self.screenshot:
                buffer = io.BytesIO()
                ss.save(buffer, "JPEG", optimize=optimize, quality=quality)
                state["screenshot"] = str(base64.b64encode(buffer.getvalue()))

        state = {**state, **self.bridge_data}
        self.bridge_data = None

        return state

    def take_screenshot(self, driver):
        """
        Take a screenshot of the current window.
        
        Returns:
            Image: The resized screenshot
        """
        screenshot = Image.open(io.BytesIO(driver.get_screenshot_as_png()))
        size = (
            int(screenshot.size[0] * self.screenshot_scale),
            int(screenshot.size[1] * self.screenshot_scale),
        )
        resized = screenshot.resize(size)
        return resized

    def run(self, driver, url):
        """
        Runs a command through the appropriate bridge.

        Returns:
            Union[dict, list(dict)]: A single state representation. Will return a
            list of state representations if it's a multi-step command.
            For example, youtube:next_up#30 to hit 'next up' 30 times
        """
        if "chrome-search" not in driver.current_url and not driver.current_url.startswith("data"):
            self.url_before_action = driver.current_url

        parsed = urlparse(url)

        if parsed.scheme not in ["http", "https"] and parsed.fragment:
            # Repetition, e.g. youtube:up_next#10
            iterations = int(parsed.fragment) if parsed.fragment else 1
            command = urldefrag(url).url
            states = [self.run(driver, command) for _ in range(iterations)]
            return states

        if "youtu" in url:
            self.bridge_data = YoutubeBridge(driver).run(url)
        elif "amazon" in url:
            self.bridge_data = AmazonBridge(driver).run(url)
        else:
            raise Exception(f"Unknown url {url}")

        return self.get_state(driver, url)
