class BaseBridge:
    """A completely useless Bridge that at least shows you
    what they're supposed to implement
    
    Args:
        driver: A Selenium WebDriver used to navigate"""


    def __init__(self, driver):
        self.driver = driver

    def get_data(self):
        """Return import data from the page, as well as
        a list of the recommendations
        
        Returns:
            dict: Representation of the page"""

        return {
            "page_type": "not implemented",
            "recommendations": []
        }

    def run(self, url):
        """Run an action/visit a URL.

        Returns:
            dict: Representation of the page"""
        self.driver.get(url)
        
        return self.get_data()