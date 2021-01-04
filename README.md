# Persine, the Persona Engine

Persine is an **automated tool to study and reverse-engineer algorithmic recommendation systems**. It has a simple interface and encourages reproducible results. You tell Persine to drive around YouTube and it gives back a spreadsheet of what else YouTube suggests you watch!

> Persine => **Pers**[ona Eng]**ine**

### For example!

People have suggested that if you watch a few lightly political videos, YouTube starts suggesting more and more extreme content – _but does it really?_

The theory is difficult to test since it involves a lot of boring clicking and YouTube already knows what you usually watch. **Persine to the rescue!**

1. Persine starts a new fresh-as-snow Chrome
2. You provide a list of videos to watch and buttons to click (like, dislike, "next up" etc)
3. As it watches and clicks more and more, YouTube customizes and customizes
4. When you're all done, Persine will save your winding path and the video/playlist/channel recommendations to nice neat CSV files.

Beyond analysis, these files can be used to repeat the experiment again later, seeing if recommendations change by time, location, user history, etc.

If you didn't quite get enough data, don't worry – you can resume your exploration later, picking up right where you left off. Since each "persona" is based on Chrome profiles, all your cookies and history will be safely stored until your next run.

### An actual example

See Persine in action [on Google Colab](https://colab.research.google.com/drive/1eAbfwV9mL34LVVIzW4AgwZt5NZJ21LwT?usp=sharing). Includes a few examples for analysis, too.

## Installation

```
pip install persine
```

Persine will automatically install Selenium and BeautifulSoup for browsing/scraping, pandas for data analysis, and pillow for processing screenshots.

You will need to install [chromedriver](https://chromedriver.chromium.org/) to allow Selenium to control Chrome. **Persine won't work without it!**

* **Installing chromedriver on OS X:** I hear you can install it [using homebrew](https://formulae.brew.sh/cask/chromedriver), but I've never done it! You can also follow the link above and click the "latest stable release" link, then download `chromedriver_mac64.zip`. Unzip it, then move the `chromedriver` file into your `PATH`. I typically put it in `/usr/local/bin`.
* **Installing chromedriver on Windows:** Follow the link above, click the "latest stable release" link. Download `chromedriver_win32.zip`, unzip it, and move `chromedriver.exe` into your `PATH` (in the spirit of anarchy I just put it in `C:\Windows`).
* **Installing chromedriver on Debian/Ubuntu:** Just run `apt install chromium-chromedriver` and it'll work.

## Quickstart

In this example, we start a new session by visiting a YouTube video and clicking the "next up" video three times to see where it leads us. We then save the results for later analysis.

```python
from persine import PersonaEngine

engine = PersonaEngine(headless=False)

with engine.persona() as persona:
    persona.run("https://www.youtube.com/watch?v=hZw23sWlyG0")
    persona.run("youtube:next_up#3")
    persona.history.to_csv("history.csv")
    persona.recommendations.to_csv("recs.csv")
```

We turn off headless mode because it's fun to watch!
