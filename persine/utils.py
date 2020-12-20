from collections import UserList
from bs4 import BeautifulSoup
import pandas as pd


def simplify_source(source, tags=("style", "svg", "script")):
    """
    Given HTML source, deletes the specified tags to make the
    source code smaller
    """
    doc = BeautifulSoup(source, features="html.parser")
    for tag in tags:
        for element in doc.select(tag):
            element.decompose()
    return doc.decode("utf-8").strip()


class RecommendationList(UserList):
    def to_df(self):
        """Returns the object as a pandas DataFrame"""
        return pd.DataFrame(self.data)

    def to_csv(self, filename):
        """Saves the object to a CSV file"""
        self.to_df().to_csv(filename, index=False)


class HistoryList(UserList):
    def to_df(self):
        """Returns the object as a pandas DataFrame"""
        return pd.DataFrame(self.data)

    def to_csv(self, filename):
        """Saves the object to a CSV file"""
        self.to_df().to_csv(filename, index=False)
