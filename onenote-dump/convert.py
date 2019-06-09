"""Convert OneNote HTML to Markdown.

Inspired by:
https://github.com/matthewwithanm/python-markdownify/blob/develop/markdownify/__init__.py

TODO:
* Metadata
* Download images
* Download attachment files
* Link to other notebook page
* Try to figure out the language of code blocks (guesslang)

"""
import re
import tempfile
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Tag


class Converter:
    def __init__(self, page, content):
        self.page = page
        self.content = content
        self.space_re = re.compile(r'[ \t]')
        self.lines_re = re.compile(r'([\r\n] *){3,}')
        self.in_code_block = False

    def convert(self):
        result = ''  # TODO: metadata
        root = BeautifulSoup(self.content, 'html.parser')
        result += self.handle_element(root)
        result = self.clean_up(result)
        return result

    def clean_up(self, result):
        # result = result.lstrip()
        # result = self.space_re.sub(' ', result)
        # result = self.lines_re.sub('\n\n', result)
        return result

    def handle_element(self, element):
        content = ''
        for child in element.children:
            if isinstance(child, NavigableString):
                content += self.handle_text(child)
            else:
                content += self.handle_element(child)
        if isinstance(element, Tag):
            content = self.handle_tag(element, content)
        return content

    def handle_text(self, text):
        return text.strip()

    def handle_tag(self, tag, content):
        handler = getattr(self, f'handle_{tag.name}', None)
        if handler:
            return handler(tag, content)
        return content

    def handle_title(self, tag, content):
        return f'# {content}\n\n'

    def handle_h1(self, tag, content):
        # Note: We're deliberately "demoting" headings to the next lower tag so
        # that the title acts as h1.
        return f'## {content}\n\n'

    def handle_h2(self, tag, content):
        return f'### {content}\n\n'

    def handle_h3(self, tag, content):
        return f'#### {content}\n\n'

    def handle_h4(self, tag, content):
        return f'##### {content}\n\n'

    def handle_h5(self, tag, content):
        return f'###### {content}\n\n'

    def handle_h6(self, tag, content):
        return f'**{content}**\n\n'

    def handle_p(self, tag, content):
        result = ''
        if self.is_code_block(tag):
            if not self.in_code_block:
                self.in_code_block = True
                result += '```\n'
        if self.in_code_block:
            result += f'{content}\n'
            if not self.is_code_block(next_sibling_tag(tag)):
                self.in_code_block = False
                result += '```\n\n'
        else:
            result = f'{content}\n\n'
        return result

    def handle_a(self, tag, content):
        href = tag.get('href')
        title = tag.get('title')
        title = title.replace('"', r'\"') if title else ''
        title = f' "{title}"' if title else ''
        return f' [{content}]({href}{title}) ' if href else content or ''

    def handle_b(self, tag, content):
        return f'**{content}**'

    handle_strong = handle_b

    def handle_i(self, tag, content):
        return f'*{content}*'

    handle_em = handle_i

    def handle_br(self, tag, content):
        return ' \n'

    def handle_li(self, tag, content):
        depth = self.li_depth(tag)
        parent = tag.parent
        if parent.name == 'ol':
            bullet = f'{self.index_in_parent(tag) + 1}.'
        else:
            bullet = '*'
        return f'{" " * 4 * depth}{bullet} {content or ""}\n'

    def handle_tr(self, tag, content):
        result = f'|{content}\n'
        if self.index_in_parent(tag) == 0:
            cell_count = self.child_count(tag, 'td')
            result += f'|{"---|" * cell_count}\n'
        return result

    def handle_td(self, tag, content):
        return f'{content}|'

    @staticmethod
    def is_code_block(tag):
        return (
            tag
            and tag.name == 'p'
            and tag.get('style')
            and 'Consolas' in tag.get('style')
        )

    @staticmethod
    def li_depth(tag):
        assert tag.name == 'li'
        depth = -1
        while tag:
            if tag.name == 'li':
                depth += 1
            tag = tag.parent
        return depth

    @staticmethod
    def index_in_parent(tag):
        """Index of this tag among all sibling tags of the same name."""
        all_items = tag.parent.find_all(tag.name, recursive=False)
        return all_items.index(tag)

    @staticmethod
    def child_count(tag, child_name):
        return len(tag.find_all(child_name, recursive=False))


def next_sibling_tag(element):
    element = element.next_sibling
    while element and not isinstance(element, Tag):
        element = element.next_sibling
    return element


def convert_page(page, content):
    (Path(r'D:\Temp') / (page['title'] + '.html')).write_bytes(content)
    return page, Converter(page, content).convert()


if __name__ == '__main__':
    p_in = Path(__file__).parent.parent / 'test/test.html'
    content = p_in.read_bytes()
    p_out = Path(tempfile.gettempdir()) / 'test.md'
    p_out.write_bytes(convert_page({'title': 'Test'}, content)[1].encode())
    print(p_out)
