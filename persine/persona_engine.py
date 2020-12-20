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
from .persona import Persona


class PersonaEngine:
    def __init__(
        self,
        height=1200,
        width=1600,
        screenshot_scale=0.5,
        screenshot=False,
        html=False,
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
        self.resume = resume

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

    def persona(self, name=None):
        """Returns a Persona initialized from the engine"""
        return Persona(self, name=name, resume=self.resume)

    def driver_options(self, user_data_dir=None):
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
        else:
            ext_path = os.path.join(
                os.path.dirname(__file__), "../extensions/ublock-origin.crx"
            )
            options.add_extension(ext_path)

        if user_data_dir:
            options.add_argument(f"user-data-dir={user_data_dir}")

        options.add_argument(f"--window-size={self.width},{self.height}")

        return options

    def launch(self, user_data_dir=None):
        """Launches a Chrome instance and returns a Selenium webdriver"""
        if self.custom_driver:
            return self.custom_driver

        options = self.driver_options()

        return webdriver.Chrome(options=options)

    def get_state(self, driver, url):
        """Returns a dictionary representation of the current page"""

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

            if self.html == "log" or "log" in self.html:
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
            if self.screenshot == "log" or "log" in self.screenshot:
                buffer = io.BytesIO()
                ss.save(buffer, "JPEG", optimize=optimize, quality=quality)
                state["screenshot"] = str(base64.b64encode(buffer.getvalue()))

        state = {**state, **self.bridge_data}
        self.bridge_data = None

        return state

    def take_screenshot(self, driver):
        """
        Take a screenshot of the current window. Note that the
        result is resized according to screenshot_scale.
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

        Returns a single state representation or a list of
        state representations.
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

        if "youtube" in url:
            self.bridge_data = YoutubeBridge(driver).run(url)
        else:
            raise Exception(f"Unknown url {url}")

        return self.get_state(driver, url)
