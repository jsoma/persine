.. _api:

API Documentation
===================

Persine is built on a triumvirate of pieces:

1. The :class:`~persine.PersonaEngine`, which more or less stores the settings for everything you'd like to do, and serves as the entry point for all of your adventures.
2. :class:`~persine.Persona`, which are the users that interact with websites. Each persona is attached to a Chrome profile, so browsing history, cookies, etc can all carry over to subsequent sessions. (Note that by default sessions do *not* carry information over)
3. :mod:`~persine.bridges`, which are the interfaces between Persine and the data on the website. They're the scrapers that pull the recommendations off of the page, and the tools that enables you to write shortcuts like ``youtube:search?kittens``

PersonaEngine
-------------

.. autoclass:: persine.PersonaEngine
   :members:
   :undoc-members:
   :show-inheritance:

Persona
-------------

.. autoclass:: persine.Persona
   :members:
   :undoc-members:
   :show-inheritance:

Bridges
-------

.. automodule:: persine.bridges
   :imported-members:
   :members:
   :undoc-members:
   :show-inheritance:
