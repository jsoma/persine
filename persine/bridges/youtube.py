import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
from urllib.parse import quote_plus


class YoutubeBridge:
    def __init__(self, driver):
        self.driver = driver

    def disable_autoplay(self):
        self.driver.execute_script(
            "document.getElementById('movie_player').setAutonavState(1);"
        )

    def click_link(self, text, timeout=3):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, text))
            )
            self.driver.find_element_by_link_text(text).click()
        except Exception:
            pass

    def get_player_state(self):
        # -1 – unstarted
        # 0 – ended
        # 1 – playing
        # 2 – paused
        # 3 – buffering
        # 5 – video cued
        return self.driver.execute_script(
            "return document.getElementById('movie_player').getPlayerState();"
        )

    def play_video(self):
        self.driver.execute_script(
            """
        document.getElementById('movie_player').playVideo();
        """
        )

    def get_player_data(self):
        return self.driver.execute_script(
            """
        return document.getElementById('movie_player').getVideoData()
        """
        )

    def get_player_page_data(self):
        return self.driver.execute_script(
            """
            data = {};
            try { data['channel_url'] = document.querySelector('.ytd-channel-name a')['href'] } catch(err) {};
            try { data['channel_sub_count'] = document.querySelector("#owner-sub-count").innerText } catch(err) {};
            try { data['view_count'] = document.querySelector('#info #count .view-count').innerText } catch(err) {};
            try { data['view_count'] = document.querySelector('#info #count .view-count').innerText } catch(err) {};
            try { data['posted_on'] = document.querySelector('#info #date yt-formatted-string').innerText } catch(err) {};
            try { data['like_count'] = document.querySelector("yt-formatted-string[aria-label*= likes").ariaLabel } catch(err) {};
            try { data['dislike_count'] = document.querySelector("yt-formatted-string[aria-label*= likes").ariaLabel } catch(err) {};
            return data;
        """
        )

    def get_video_data(self):
        data = self.get_player_data()
        player_page_data = self.get_player_page_data()
        video = {
            **player_page_data,
            "page_type": "video",
            "title": data["title"],
            "id": data["video_id"],
            "channel_name": data["author"],
            "recommendations": self.scrape_sidebar(),
            "caption_tracks": self.driver.execute_script(
                """
                 player = document.querySelector("#movie_player");
                 player.loadModule("captions");
                 return player.getOption("captions", "tracklist");
             """
            ),
        }

        return video

    def get_page_data(self):
        return self.driver.execute_script(
            """
            try {
                return window.getPageData().data.response
            } catch(err) {
                return ytInitialData
            }
        """
        )

    def scrape_sidebar(self):
        recs = self.driver.execute_script(
            """
        return [...document.querySelectorAll("#items.ytd-watch-next-secondary-results-renderer > *")].map((d, i) => {
            data = {};
            try { data['item_type'] = d.tagName; } catch(err) {};
            try { data['position'] = i + 1; } catch(err) {};
            try { data['title'] = d.querySelector("h3").innerText } catch(err) {};
            try { data['url'] = d.querySelector("a.yt-simple-endpoint")['href'] } catch(err) {};
            try { data['channel_name'] = d.querySelector(".ytd-channel-name").innerText } catch(err) {};
            try { data['metadata'] = d.querySelector("#metadata-line").innerText } catch(err) {};
            try { data['duration_text'] = d.querySelector("span.ytd-thumbnail-overlay-time-status-renderer").innerText.trim() } catch(err) {};
            return data;
        })
        """  # noqa: E501
        )
        recs = [
            rec for rec in recs if rec["item_type"] != "YTD-CONTINUATION-ITEM-RENDERER"
        ]

        return recs

    def scrape_search_results(self):
        recs = self.driver.execute_script(
            """
        return [...document.querySelectorAll("#contents.ytd-item-section-renderer > *")].map((d, i) => {
            data = {};
            try { data['item_type'] = d.tagName; } catch(err) {};
            try { data['position'] = i + 1; } catch(err) {};
            try { data['thumbnail_url'] = d.querySelector("img")['src'] } catch(err) {};
            try { data['title'] = d.querySelector("h3").innerText } catch(err) {};
            try { data['url'] = d.querySelector("a.yt-simple-endpoint")['href'] } catch(err) {};
            try { data['channel_name'] = d.querySelector(".ytd-channel-name a").innerText } catch(err) {};
            try { data['channel_url'] = d.querySelector(".ytd-channel-name a")['href'] } catch(err) {};
            try { data['metadata'] = d.querySelector("#metadata-line").innerText } catch(err) {};
            try { data['metadata'] = d.querySelector(".movie-metadata-list").innerText } catch(err) {};
            try { data['duration_text'] = d.querySelector("span.ytd-thumbnail-overlay-time-status-renderer").innerText } catch(err) {};
            try { data['description'] = d.querySelector("#description-text ").innerText } catch(err) {};
            return data;
        })
        """  # noqa: E501
        )
        recs = [
            rec
            for rec in recs
            if rec["item_type"] != "YTD-HORIZONTAL-CARD-LIST-RENDERER"
        ]
        return recs

    def scrape_homepage(self):
        return self.driver.execute_script(
            """
        return [...document.querySelectorAll("#contents.ytd-rich-grid-renderer > ytd-rich-item-renderer")].map((d, i) => {
            data = {};
            try { data['item_type'] = d.tagName; } catch(err) {};
            try { data['position'] = i + 1; } catch(err) {};
            try { data['thumbnail_url'] = d.querySelector("img")['src'] } catch(err) {};
            try { data['title'] = d.querySelector("h3").innerText } catch(err) {};
            try { data['url'] = d.querySelector("a.yt-simple-endpoint")['href'] } catch(err) {};
            try { data['channel_name'] = d.querySelector(".ytd-channel-name a").innerText } catch(err) {};
            try { data['channel_url'] = d.querySelector(".ytd-channel-name a")['href'] } catch(err) {};
            try { data['metadata'] = d.querySelector("#metadata-line").innerText } catch(err) {};
            try { data['metadata'] = d.querySelector(".movie-metadata-list").innerText } catch(err) {};
            try { data['duration_text'] = d.querySelector("span.ytd-thumbnail-overlay-time-status-renderer").innerText } catch(err) {};
            try { data['description'] = d.querySelector("#description-text ").innerText } catch(err) {};
            return data;
        })
        """  # noqa: E501
        )

    def wait_for_video_completion(self, skipahead=True):
        try:
            self.get_player_state()
        except Exception:
            time.sleep(5)
            self.click_link("Skip Ad")

        try:
            self.get_player_state()
        except Exception:
            time.sleep(15)
            self.click_link("Skip Ad")

        if self.get_player_state() != 1:
            self.play_video()

        if skipahead:
            time.sleep(1)
            self.driver.execute_script(
                """
                let player = document.getElementById('movie_player');
                player.seekTo(player.getDuration() - 2);
                player.playVideo()
            """
            )

        # In case we do get stuck behind an ad, we'll wait for a long time
        length = self.driver.execute_script(
            "return document.getElementById('movie_player').getDuration()"
        )
        WebDriverWait(self.driver, length + 20).until(
            lambda s: self.get_player_state() == 0
        )
        self.disable_autoplay()

    def page_type(self):
        # TODO remove and replace
        key = list(self.get_page_data()["contents"].keys())[0]
        types = {
            "twoColumnWatchNextResults": "video",
            "twoColumnSearchResultsRenderer": "search_results",
            "twoColumnBrowseResultsRenderer": "homepage",
        }
        return types[key]

    def get_data(self):
        page_type = self.page_type()
        if page_type == "video":
            return self.get_video_data()
        elif page_type == "search_results":
            return {
                "page_type": page_type,
                "term": self.driver.find_element_by_css_selector(
                    "input#search"
                ).get_attribute("value"),
                "recommendations": self.scrape_search_results(),
            }
        elif page_type == "homepage":
            return {"page_type": page_type, "recommendations": self.scrape_homepage()}

    def run(self, url):
        parsed = urlparse(url)

        # Remove popups that might get in the way of clicking
        try:
            self.driver.execute_script(
                """
                document.querySelectorAll('.ytd-popup-container').forEach(d=> d.remove());
            """  # noqa: E501
            )
        except Exception:
            pass

        # Execute the command
        if parsed.scheme in ["http", "https"]:
            self.driver.get(url)
            if self.page_type() == "video":
                self.wait_for_video_completion()
        elif parsed.path == "homepage":
            self.driver.get("https://www.youtube.com/")
        elif parsed.path == "search":
            self.driver.get(
                f"https://www.youtube.com/results?search_query={quote_plus(parsed.query)}"  # noqa: E501
            )
        elif parsed.path == "next_up":
            self.driver.find_element_by_css_selector(
                "ytd-compact-autoplay-renderer h3"
            ).click()
            self.wait_for_video_completion()
        elif parsed.path == "like":
            self.driver.find_element_by_xpath(
                '//button[starts-with(@aria-label, "Like")]'
            ).click()
        elif parsed.path == "dislike":
            self.driver.find_element_by_xpath(
                '//button[starts-with(@aria-label, "Dislike")]'
            ).click()
        elif parsed.path == "subscribe":
            self.driver.find_element_by_xpath(
                '//button[starts-with(@aria-label, "Subscribe to")]'
            ).click()
        elif parsed.path == "unsubscribe":
            self.driver.find_element_by_xpath(
                '//button[starts-with(@aria-label, "Unsubscribe from")]'
            ).click()
            time.sleep(0.25)
            self.driver.find_element_by_xpath(
                '//button[starts-with(@aria-label, "Unsubscribe")]'
            ).click()
        elif parsed.path == "sign_in":
            try:
                self.driver.find_element_by_xpath('//*[@aria-label="Sign in"]').click()
            except Exception:
                pass

            print("Please sign in manually, I'll wait up to 10 minutes")

            WebDriverWait(self.driver, 10 * 60).until(
                EC.visibility_of_element_located((By.ID, "avatar-btn"))
            )
        else:
            raise Exception(f"unknown URL {url}")

        return self.get_data()
