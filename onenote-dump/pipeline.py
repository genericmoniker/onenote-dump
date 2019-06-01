import math
from concurrent.futures import Future, ThreadPoolExecutor

from onenote import get_page_content
from convert import convert_page


class Pipeline:

    def __init__(self, onenote_session, out_dir, max_workers=10):
        self.s = onenote_session
        self.out_dir = out_dir
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
        future = self.executors[1].submit(convert_page, page, content)
        future.add_done_callback(self._submit_save)

    def _submit_save(self, future: Future):
        page, content = future.result()
        future = self.executors[2].submit(self._save_page, page, content)
        return future.result()

    def _save_page(self, page, content):
        path = self.out_dir / (page['title'] + '.md')
        path.write_text(content)

    def done(self):
        for executor in self.executors:
            executor.shutdown()
