from datetime import datetime
import os
import shutil
import json
from .utils import HistoryList
from .utils import RecommendationList


class Persona:
    """
    The Persona represents a single user. If it is
    given a name, it is associated with an individual
    Chrome profile.

    Args:
        engine (PersonaEngine): The engine to associate with this persona
        name (str): The name to be given to this profile. If not named, an
            empty profile is used.
        history_path (str): Path to the JSON file that holds this persona's
            action/browsing history
        user_data_dir (str): If specified, load the Chrome profile from this
            folder
        resume (boolean): Whether this persona should resume a previous persona
            with the same name. If False, the previous Chrome profile is deleted.
        overwrite (boolean): Whether to prompt the user when overwriting a previous
            persona's Chrome profile (see resume)
    """
    def __init__(
        self,
        engine,
        name=None,
        history_path=None,
        user_data_dir=None,
        resume=False,
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
        Deletes all previous data for that Chrome profile, including history file and user_data_dir
        """
        if self.user_data_dir:
            if not self.overwrite:
                response = input(f"Delete folder {self.user_data_dir}? [y/n]")
                if not response.lower().startswith("y"):
                    raise Exception("Don't want to delete")
            shutil.rmtree(self.user_data_dir, ignore_errors=True)
        if self.history_path:
            try:
                os.remove(self.history_path)
            except Exception:
                pass

    def __enter__(self):
        """
        Launches the browser for use in a context manager
        """
        self.launch()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Quits the browser when exiting a context manager
        """
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
        return [self.run(url) for url in urls]


    def run(self, url, notes=None):
        """
        Runs a single command and updates the history
        Args:
            url (str): The action to run or URL to visit
            notes (dict): Additional information to include in the history row
        Returns:
            Union[dict, list(dict)]: A single state representation. Will return
                a list of state representations if it's a multi-step command.
                For example, youtube:next_up#30 to hit 'next up' 30 times
        """
        if self.driver is None:
            self.launch()

        state = self.engine.run(self.driver, url)

        if isinstance(state, list):
            for s in state:
                self.update_history(s, notes)
        else:
            self.update_history(state, notes)
        
        return self.history[-1]

    def update_history(self, state, notes=None):
        """Updates history/recommendations lists with the given state"""
        same_page = [
            "youtube:like",
            "youtube:dislike",
            "youtube:subscribe",
            "youtube:unsubscribe",
        ]

        new_state = state.copy()
        if notes is not None:
            for key, value in notes.items():
                if key in new_state:
                    raise Exception(f"key {key} already exists in state")
                new_state[key] = value

        self.history.append(new_state)
        if "recommendations" in new_state and new_state["action"] not in same_page:
            for rec in state["recommendations"]:
                self.recommendations.append({
                    **rec,
                    'action_key': new_state['key']
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
