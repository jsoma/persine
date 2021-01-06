import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
from urllib.parse import quote_plus
from .bridge import BaseBridge

class YoutubeBridge(BaseBridge):
    """A bridge that interacts with and scrapes YouTube"""


    def __init__(self, driver):
        self.driver = driver

    def __disable_autoplay(self):
        self.driver.execute_script(
            "document.getElementById('movie_player').setAutonavState(1);"
        )

    def __click_link(self, text, timeout=3):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, text))
            )
            self.driver.find_element_by_link_text(text).click()
        except Exception:
            pass

    def __get_player_state(self):
        # -1 – unstarted
        # 0 – ended
        # 1 – playing
        # 2 – paused
        # 3 – buffering
        # 5 – video cued
        return self.driver.execute_script(
            "return document.getElementById('movie_player').getPlayerState();"
        )

    def __play_video(self):
        self.driver.execute_script(
            """
        document.getElementById('movie_player').playVideo();
        """
        )

    def __get_player_data(self):
        return self.driver.execute_script(
            """
        return document.getElementById('movie_player').getVideoData()
        """
        )

    def __get_player_page_data(self):
        return self.driver.execute_script(
            """
            data = {};
            player = document.querySelector("#movie_player");

            try { data['is_live'] = player.getVideoData().isLive } catch(err) {};
            try { data['is_listed'] = player.getVideoData().isListed } catch(err) {};

            try { data['channel_url'] = document.querySelector('.ytd-channel-name a')['href'] } catch(err) {};
            try { data['channel_sub_count'] = document.querySelector("#owner-sub-count").innerText } catch(err) {};
            try { data['view_count'] = document.querySelector('#info #count .view-count').innerText } catch(err) {};
            try { data['view_count'] = document.querySelector('#info #count .view-count').innerText } catch(err) {};
            try { data['posted_on'] = document.querySelector('#info #date yt-formatted-string').innerText } catch(err) {};
            try { data['like_count'] = document.querySelector("yt-formatted-string[aria-label*= likes").ariaLabel } catch(err) {};
            try { data['dislike_count'] = document.querySelector("yt-formatted-string[aria-label*= dislikes").ariaLabel } catch(err) {};
            return data;
        """
        )

    def __get_video_data(self):
        data = self.__get_player_data()
        player_page_data = self.__get_player_page_data()
        video = {
            **player_page_data,
            "page_type": "video",
            "title": data.get("title", None),
            "id": data.get("video_id", None),
            "channel_name": data.get("author", None),
            "is_live": player_page_data.get("is_live", None),
            "is_listed": player_page_data.get("is_listed", None),
            "recommendations": self.__scrape_sidebar(),
            "caption_tracks": self.driver.execute_script(
                """
                 player = document.querySelector("#movie_player");
                 player.loadModule("captions");
                 return player.getOption("captions", "tracklist");
             """
            ),
        }

        return video

    def __get_page_data(self):
        return self.driver.execute_script(
            """
            try {
                return window.getPageData().data.response
            } catch(err) {
                return ytInitialData
            }
        """
        )

    def __scrape_sidebar(self):
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
            try { data['thumbnail_url'] = d.querySelector("img")['src'] } catch(err) {};
            return data;
        })
        """  # noqa: E501
        )
        recs = [
            rec for rec in recs if rec["item_type"] != "YTD-CONTINUATION-ITEM-RENDERER"
        ]

        return recs

    def __scrape_search_results(self):
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

    def __scrape_homepage(self):
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

    def __attempt_ad_skip(self, delay=6):
        time.sleep(delay)
        self.driver.find_element_by_class_name("ytp-ad-skip-button-text").click()

    def __wait_for_video_completion(self, skipahead=True):
        try:
            # Confirm it's a video page
            self.driver.find_element_by_css_selector("#movie_player")

            # Wait for the player to be ready
            while True:
                try:
                    # This will throw an exception if the player 
                    # is not initialized
                    self.__get_player_state()
                    break
                except:
                    time.sleep(1)
        except:
            pass

        try:
            # Wait for ad overlay to show up, then click the 
            # skip button.
            WebDriverWait(self.driver, 3).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "ad-showing"))
            )
            self.__attempt_ad_skip()
        except:
            # No ad
            pass

        if self.__get_player_state() != 1:
            self.__play_video()

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
        
        is_live = self.driver.execute_script(
            "return document.getElementById('movie_player').getVideoData().isLive"
        )

        if length == 0 or is_live:
            # It's live, just exit
            time.sleep(1)
            return
        else:
            # Wait until it's done
            WebDriverWait(self.driver, length + 20).until(
                lambda s: self.__get_player_state() == 0
            )
            self.__disable_autoplay()

    def __get_page_type(self):
        # TODO remove and replace
        try:
            key = list(self.__get_page_data()["contents"].keys())[0]
            types = {
                "twoColumnWatchNextResults": "video",
                "twoColumnSearchResultsRenderer": "search_results",
                "twoColumnBrowseResultsRenderer": "homepage",
            }
            return types[key]
        except:
            return "invalid"

    def get_data(self):
        page_type = self.__get_page_type()
        if page_type == "invalid":
            return { "page_type": page_type }
        elif page_type == "video":
            return self.__get_video_data()
        elif page_type == "search_results":
            return {
                "page_type": page_type,
                "term": self.driver.find_element_by_css_selector(
                    "input#search"
                ).get_attribute("value"),
                "recommendations": self.__scrape_search_results(),
            }
        elif page_type == "homepage":
            return {"page_type": page_type, "recommendations": self.__scrape_homepage()}

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
            if self.__get_page_type() == "video":
                self.__wait_for_video_completion()
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
            self.__wait_for_video_completion()
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
