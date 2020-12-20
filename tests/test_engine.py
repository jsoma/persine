from persine import PersonaEngine


def test_engine_persona():
    engine = PersonaEngine(resume=True)
    p = engine.persona("daisy")
    assert p.name == "daisy"


def test_engine_launch():
    engine = PersonaEngine()
    driver = engine.launch()
    assert driver is not None
    driver.quit()
