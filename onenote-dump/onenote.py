from requests import Session

BASE_URL = 'https://graph.microsoft.com/v1.0/me/onenote/'


def get_notebook_pages(s: Session, notebook_display_name):
    notebooks = get_notebooks(s)
    notebook = find_notebook(notebooks, notebook_display_name)
    yield from get_pages(s, notebook)


def get_notebooks(s: Session):
    return _get(s, BASE_URL + 'notebooks')


def find_notebook(notebooks, display_name):
    for notebook in notebooks['value']:
        if notebook['displayName'] == display_name:
            return notebook
    return None


def get_section_groups(s: Session, notebook):
    return _get(notebook['sectionGroupsUrl'])


def get_sections(s: Session, section_group):
    return _get(section_group['sectionsUrl'])


def get_pages(s: Session, notebook):
    sections = _get(s, notebook['sectionsUrl'])
    for section in sections['value']:
        pages = _get(s, section['pagesUrl'])
        for page in pages['value']:
            yield page


def get_page_content(s: Session, page):
    return page, s.get(page['contentUrl']).content


def _get(s: Session, url):
    r = s.get(url)
    r.raise_for_status()
    return r.json()
