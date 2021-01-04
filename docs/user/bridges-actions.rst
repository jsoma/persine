Bridges and actions
===================

**Bridges** are site-specific scrapers that tell Persine what to click and what to scrape. In order for Persine to successfully understand a site, it needs a bridge for that site.

When you visit a URL, the bridge for that domain is used to processed the page. Bridges are also in charge of site-specific commands such as ``youtube:like``.

.. note::

    If you'd like an action to repeat multiple times you can append ``#[NUMBER]`` to the action name. For example, ``youtube:next_up#50`` will watch the next fifty "next up" videos.

YouTube
-------

The :class:`~persine.bridges.YoutubeBridge` is a general-purpose YouTube scraper. Can pull recommendations from the homepage, search results, and video pages.

.. _youtube_actions:

Actions
~~~~~~~

======================== ===========
**Action**               **Description**
------------------------ -----------
``youtube:homepage``     Visit youtube.com
``youtube:search?QUERY`` Search YouTube for the specified term
``youtube:next_up``      When on a video page, click the "next up" video
``youtube:like``         Click the like button
``youtube:dislike``      Click the dislike button
``youtube:subscribe``    Click the subscribe button
``youtube:unsubscribe``  Click the unsubscribe button
``youtube:sign_in``      Begin the signin process – you'll need to complete the process manually, but Persine will resume as soon as it notices you're logged in
======================== ===========

Amazon
------

The :class:`~persine.bridges.AmazonBridge` is still in development, but here's what it can do so far.

.. _amazon_actions:

Actions
~~~~~~~

======================== ===========
**Action**               **Description**
------------------------ -----------
``amazon:homepage``      Visit amazon.com
``amazon:search?QUERY``  Search Amazon for the specified term
``amazon:asin?ASIN``     Visit the page for a given ASIN
======================== ===========

Adding new bridges
------------------

Bridges are easy to add! Take a look at the `Amazon one <https://github.com/jsoma/persine/blob/main/persine/bridges/amazon.py>`_ as an example – all you really need to implement to build your own is ``.run`` that returns data from the page. It's easy to scrape using Selenium or by running JavaScript on the page itself and returning the results.