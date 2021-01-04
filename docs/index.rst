Persine
===================================

Release v\ |version|. (:ref:`Installation <install>`)

Persine is an automated tool to study and reverse-engineer algorithmic recommendation systems, like YouTube videos and Amazon products. It has a simple interface and encourages reproducible results.

-------------------

Persine is dead simple to use.

.. code-block:: python

   from persine import PersonaEngine

   engine = PersonaEngine()

   with engine.persona() as persona:
      persona.run_batch([
         "https://www.youtube.com/watch?v=hZw23sWlyG0",
         "youtube:next_up#3",
         "https://www.youtube.com/watch?v=hZw23sWlyG0"
      ])
      persona.history.to_csv("history.csv")
      persona.recommendations.to_csv("recs.csv")

In this example, we visit a YouTube video, click the "next up" video three times, and then revisit the original video. We then save the results for later analysis.

The User Guide
--------------

.. toctree::
   :maxdepth: 2

   user/install
   user/quickstart
   user/bridges-actions
   api

* :ref:`modindex`