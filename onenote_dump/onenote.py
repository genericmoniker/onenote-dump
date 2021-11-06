import logging
from datetime import timedelta

from requests import Session
from tenacity import retry, retry_if_exception, wait_exponential

BASE_URL = "https://graph.microsoft.com/v1.0/me/onenote/"

logger = logging.getLogger(__name__)


class NotebookNotFound(Exception):
    def __init__(self, name, s: Session = None):
        msg = f'Notebook "{name}" not found. ' + self._possible_notebooks(s)
        super().__init__(msg)

    @staticmethod
    def _possible_notebooks(s: Session):
        notebooks = []
        if s:
            try:
                notebooks = get_notebooks(s)
                names = [n["displayName"] for n in notebooks["value"]]
                return "Maybe:\n" + "\n".join(names) + "\n"
            except Exception:
                return "Possible notebooks unknown."


def get_notebook_pages(s: Session, notebook_display_name, section_display_name):
    notebooks = get_notebooks(s)
    notebook = find_notebook(notebooks, notebook_display_name)
    if notebook is None:
        raise NotebookNotFound(notebook_display_name, s)
    yield from get_pages(s, notebook, section_display_name)


def get_notebooks(s: Session):
    return _get_json(s, BASE_URL + "notebooks")


def find_notebook(notebooks, display_name):
    for notebook in notebooks["value"]:
        if notebook["displayName"] == display_name:
            return notebook
    return None


def get_sections(s: Session, parent, section_display_name):
    """Get sections, recursively.

    If section_display_name is provided, only that section is returned.
    """
    url = parent.get("sectionsUrl")
    if url:
        sections = _get_json(s, url)
        for section in sections["value"]:
            if section_display_name and section["displayName"] != section_display_name:
                continue
            yield section
    url = parent.get("sectionGroupsUrl")
    if url:
        section_groups = _get_json(s, url)
        for section_group in section_groups["value"]:
            yield from get_sections(s, section_group, section_display_name)


def get_pages(s: Session, notebook, section_display_name):
    for section in get_sections(s, notebook, section_display_name):
        url = section["pagesUrl"]
        while url:
            pages = _get_json(s, url)
            for page in pages["value"]:
                yield page
            url = pages.get("@odata.nextLink")


def get_page_content(s: Session, page):
    return page, _get(s, page["contentUrl"]).content


def get_attachment(s: Session, url):
    return _get(s, url).content


def _get_json(s: Session, url):
    return _get(s, url).json()


# This section of code handles rate-limiting errors.
# https://docs.microsoft.com/en-us/graph/throttling
# But note that OneNote is not listed as an API with a Retry-After header, so
# we just have to guess at how long to wait, and exponentially back off if we
# guess wrong.

MIN_RETRY_WAIT = timedelta(minutes=5).total_seconds()


def _is_too_many_requests(e: Exception):
    if hasattr(e, "response"):
        if e.response.status_code == 429:
            logger.info("Request rate limit hit. Waiting a few minutes...")
            return True
    return False


@retry(
    retry=retry_if_exception(_is_too_many_requests),
    wait=wait_exponential(min=MIN_RETRY_WAIT),
)
def _get(s: Session, url):
    r = s.get(url)
    r.raise_for_status()
    return r
