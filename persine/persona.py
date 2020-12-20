from datetime import datetime
import os
import shutil
import json
from .utils import HistoryList
from .utils import RecommendationList


class Persona:
    def __init__(
        self,
        engine,
        name=None,
        history_path=None,
        user_data_dir=None,
        resume=True,
        overwrite=False,
    ):
        self.engine = engine
        self.history = HistoryList([])
        self.recommendations = RecommendationList([])
        self.name = name
        self.driver = None
        session_key = datetime.now().strftime("%Y-%m-%d-%H.%M.%S.%f")[:-3]
        self.overwrite = overwrite

        if name is not None and user_data_dir is None:
            self.user_data_dir = os.path.join(self.engine.data_dir, "personas", name)  # noqa: E501
        else:
            self.user_data_dir = user_data_dir

        if history_path is not None:
            self.history_path = history_path
        elif name is None and history_path is None:
            self.history_path = os.path.join(
                self.engine.data_dir, f"{session_key}.json"
            )
        elif history_path is None:
            self.history_path = os.path.join(self.engine.data_dir, f"{name}.json")  # noqa: E501

        if not resume:
            self.clear()

        self.load_history()

    def clear(self):
        """
        Deletes all pervious data, including history file and user_data_dir
        """
        if self.user_data_dir:
            if not self.overwrite:
                response = input(f"Delete folder {self.user_data_dir}? [y/n]")
                if not response.lower().startswith("y"):
                    raise Exception("Don't want to delete")
            shutil.rmtree(self.user_data_dir)
        if self.history_path:
            try:
                os.remove(self.history_path)
            except Exception:
                pass

    def __enter__(self):
        self.launch()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()

    def launch(self):
        """Launches a browser through PersonaEngine"""
        self.driver = self.engine.launch(user_data_dir=self.user_data_dir)

    def quit(self):
        """Quits the browser"""
        self.driver.quit()
        self.driver = None

    def run_batch(self, urls):
        """Run a series of commands"""
        for url in urls:
            self.run(url)

    def run(self, url):
        """Runs a single command and updates the history"""
        if self.driver is None:
            self.launch()
        state = self.engine.run(self.driver, url)

        if isinstance(state, list):
            for s in state:
                self.update_history(s)
        else:
            self.update_history(state)

    def update_history(self, state):
        """Updates history/recommendations lists with the given state"""
        same_page = [
            "youtube:like",
            "youtube:dislike",
            "youtube:subscribe",
            "youtube:unsubscribe",
        ]

        self.history.append(state)
        if "recommendations" in state and state["action"] not in same_page:
            for rec in state["recommendations"]:
                self.recommendations.append({
                    **rec,
                    'action_key': state['key']
                })
        self.save_history()

    def save_history(self):
        """Saves the browsing/command history to a file"""
        os.makedirs(os.path.dirname(self.history_path), exist_ok=True)

        with open(self.history_path, "w") as f:
            json.dump(list(self.history), f)

    def load_history(self):
        """Loads the browsing/command history from a file"""
        try:
            with open(self.history_path, "r") as f:
                for visit in json.load(f):
                    self.update_history(visit)
        except FileNotFoundError:
            self.history = HistoryList([])
