.. _Chromedriver: https://chromedriver.chromium.org
.. _install:

Installation
==================

Installing Persine
------------------

Installation of Persine isn't too hard, it can be installed using pip::

    pip install persine

In order to do its job, Persine will automatically install a lot of dependencies! These include:

- `Selenium <https://www.selenium.dev/>`_ to control the browser
- `BeautifulSoup <https://www.crummy.com/software/BeautifulSoup/bs4/doc/>`_ for browsing/scraping
- `pandas <https://pandas.pydata.org/>`_ for data analysis
- `pillow <https://pillow.readthedocs.io/en/stable/>`_ for processing screenshots

After you install Persine, you aren't done yet: because Persine controls a browser, you need to install both a **browser** as well as the **software that connects Python to the browser**.

Installing Chrome
-----------------

Persine uses `Google Chrome <https://www.google.com/chrome/>`_ to drive around the internet and pretend to be a user. I would love to switch to Firefox but it has `its own problems <https://firefox-source-docs.mozilla.org/testing/geckodriver/Notarization.html>`_.

You'll want to make sure it's in a normal place (for example, not just living in your "Downloads" folder).

.. _cd_section:

Installing ChromeDriver
-----------------------

You will need to install ChromeDriver_ to allow Selenium to control Chrome.  You can read `the ChromeDriver getting started page <https://chromedriver.chromium.org/getting-started>`_ but I've also included installing instructions below.

    Note that every time you update Chrome you'll need to update ChromeDriver.

Installing ChromeDriver on OS X
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The easiest way to install ChromeDriver on OS X is `using homebrew <https://formulae.brew.sh/cask/chromedriver>`_::

    brew install --cask chromedriver

Alternatively, you can follow these steps:

1. Visit the ChromeDriver_ website
2. Click the "latest stable release" link
3. Download **chromedriver_mac64.zip**
4. Unzip it, revealing a file called **chromedriver** (no extension)
5. Move this file into your PATH. I typically put it in **/usr/local/bin**.

Installing ChromeDriver on Windows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Follow the following steps to install ChromeDriver on Windows:

1. Visit the ChromeDriver_ website
2. Click the "latest stable release" link
3. Download **chromedriver_win32.zip**
4. Unzip it, revealing a file called **chromedriver.exe** (no extension)
5. Move this file into your PATH. In the spirit of anarchy I just put it in **C:\Windows**.

Installing ChromeDriver on Debian/Ubuntu
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's the easiest of them all::

    apt install chromium-chromedriver



