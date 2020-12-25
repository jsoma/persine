import pytest

from persine import Persona
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from unittest.mock import Mock


@pytest.fixture
def engine():
    def launch_chrome(user_data_dir):
        options = Options()
        options.add_argument("--headless")
        return webdriver.Chrome(options=options)

    eng = Mock()
    eng.data_dir = "/tmp/data_dir"
    eng.history_path = "/tmp/history.json"
    eng.launch = launch_chrome

    return eng


def test_context(engine):
    with Persona(engine=engine) as persona:
        assert persona.driver is not None

    assert persona.driver is None


def test_history(engine):
    persona = Persona(engine=engine)

    assert len(persona.history) == 0
    persona.update_history(
        {
            "key": "test-key-1",
            "url": "sample",
            "action": "test:sample",
            "recommendations": [{"number": 1}, {"number": 2}, {"number": 3}],
        }
    )
    persona.update_history(
        {
            "key": "test-key-2",
            "url": "sample2",
            "action": "test:sample",
            "recommendations": [{"number": 3}, {"number": 2}, {"number": 1}],
        }
    )
    assert len(persona.history) == 2
    assert len(persona.recommendations) == 6


def test_startup_shutdown(engine):
    persona = Persona(engine=engine)
    assert persona.driver is None
    persona.launch()
    assert persona.driver is not None
    persona.quit()
    assert persona.driver is None
