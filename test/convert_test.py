from pathlib import Path

from onenote_dump.convert import Converter

TEST_DIR = Path(__file__).parent


def create_converter(html_filename, tmp_path):
    page = {}
    content = (TEST_DIR / html_filename).read_bytes()
    notebook = "Test"
    session = object()
    attach = tmp_path

    return Converter(page, content, notebook, session, attach)


def test_headings(tmp_path):
    converter = create_converter("headings.html", tmp_path)
    out = converter.convert()

    assert "# Headings Test" in out
    assert "## Heading 1" in out
    assert "### Heading 2" in out
    assert "#### Heading 3" in out
    assert "##### Heading 4" in out
    assert "###### Heading 5" in out
    assert "**Heading 6**" in out


def test_paragraphs(tmp_path):
    converter = create_converter("paragraphs.html", tmp_path)
    out = converter.convert()

    assert "mollit anim id est laborum.\n\n" in out
    assert "\n> Many of life's failures are people" in out

    # Hmm... "Thomas Edison" shouldn't be part of the quote, but it is indistinguishable
    # in the HTML from the quote itself. The OneNote web app displays it differently,
    # though, so is there some control available in the HTML rendering through the API?
    # See Issue #6 on GitHub.
