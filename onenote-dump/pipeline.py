import math
import re
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path

from onenote import get_page_content
from convert import convert_page


class Pipeline:
    def __init__(
        self, onenote_session, notebook: str, out_dir: Path, max_workers=10
    ):
        self.s = onenote_session
        self.notebook = notebook
        self.filename_re = re.compile(r'[<>:\"/\\\|\?\*#]')
        self.whitespace_re = re.compile(r'\s+')
        self.notes_dir = out_dir / 'notes'
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        self.attach_dir = out_dir / 'attachments'
        self.attach_dir.mkdir(parents=True, exist_ok=True)
        self.executors = [
            ThreadPoolExecutor(math.ceil(max_workers / 3), 'PipelinePage'),
            ThreadPoolExecutor(math.floor(max_workers / 3), 'PipelineConvert'),
            ThreadPoolExecutor(math.floor(max_workers / 3), 'PipelineSave'),
        ]

    def add_page(self, page: dict):
        future = self.executors[0].submit(get_page_content, self.s, page)
        future.add_done_callback(self._submit_conversion)

    def _submit_conversion(self, future: Future):
        page, content = future.result()
        future = self.executors[1].submit(
            convert_page, page, content, self.notebook, self.s, self.attach_dir
        )
        future.add_done_callback(self._submit_save)

    def _submit_save(self, future: Future):
        page, content = future.result()
        future = self.executors[2].submit(self._save_page, page, content)
        return future.result()

    def _save_page(self, page, content):
        path = self.notes_dir / (self._filenamify(page['title']) + '.md')
        path.write_text(content, encoding='utf-8')

    def _filenamify(self, s):
        s = self.filename_re.sub(' ', s)
        s = self.whitespace_re.sub(' ', s)
        return s.strip()

    def done(self):
        for executor in self.executors:
            executor.shutdown()
