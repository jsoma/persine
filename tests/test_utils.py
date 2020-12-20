from persine import utils
import re

SOURCE = """
    <html>
    <style>
    a {
        color: red;
    }
    </style>
    <script>
    console.log('test')
    </script>
    <svg>
    <circle cx="0" cy="0"></circle>
    </svg>
    </html>
    """


def test_simplify_source():
    shrunken = utils.simplify_source(SOURCE)
    assert shrunken == "<html>\n</html>"


def test_simplify_source_options():
    shrunken = utils.simplify_source(SOURCE, tags=())
    assert re.sub(r"\s", "", shrunken) == re.sub(r"\s", "", SOURCE)
