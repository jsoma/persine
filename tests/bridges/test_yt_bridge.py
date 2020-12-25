import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from persine.bridges.youtube import YoutubeBridge


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--mute-audio")
    # options.add_extension("ublock-origin.crx")
    options.add_argument("--autoplay-policy=no-user-gesture-required")
    return webdriver.Chrome(options=options)


def test_player_data(driver):
    bridge = YoutubeBridge(driver)
    driver.get("https://www.youtube.com/watch?v=1kIQT7uUiME")
    res = bridge.get_player_data()

    comps = {
        "title": "Land of Talk - Some Are Lakes [Official Music Video]",
        "video_id": "1kIQT7uUiME",
        "author": "Saddle Creek",
    }
    for key, value in comps.items():
        assert comps[key] == res[key]


def test_video_data(driver):
    bridge = YoutubeBridge(driver)
    bridge.run("https://www.youtube.com/watch?v=1kIQT7uUiME")
    res = bridge.get_video_data()

    comps = {
        "page_type": "video",
        "title": "Land of Talk - Some Are Lakes [Official Music Video]",
        "id": "1kIQT7uUiME",
        "channel_name": "Saddle Creek",
        "channel_url": "https://www.youtube.com/channel/UCW7MRMCxD5dbOU7TQaCAMLQ",  # noqa: E501
    }
    for key, value in comps.items():
        assert comps[key] == res[key]

    assert len(res["recommendations"]) > 0


def test_recommendation_scraper(driver):
    bridge = YoutubeBridge(driver)
    bridge.run("https://www.youtube.com/watch?v=1kIQT7uUiME")

    recs = bridge.scrape_sidebar()
    assert len(recs) > 5
    for rec in recs:
        assert rec["item_type"] is not None
        assert rec["title"] is not None
        assert rec["url"] is not None


def test_likes_v_dislikes(driver):
    bridge = YoutubeBridge(driver)
    bridge.run("https://www.youtube.com/watch?v=1kIQT7uUiME")

    data = bridge.get_player_page_data()
    assert data['dislike_count'] != data['like_count']


def test_homepage_scraper(driver):
    bridge = YoutubeBridge(driver)
    bridge.run("https://www.youtube.com/")

    recs = bridge.scrape_homepage()

    assert len(recs) > 5
    for rec in recs:
        assert rec["item_type"] is not None
        assert rec["title"] is not None
        assert rec["url"] is not None


def test_search_results(driver):
    bridge = YoutubeBridge(driver)
    bridge.run("youtube:search?lofi")

    recs = bridge.scrape_search_results()

    assert len(recs) > 5
    for rec in recs:
        assert rec["item_type"] is not None
        assert rec["title"] is not None
        assert rec["url"] is not None
