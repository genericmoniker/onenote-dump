import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from onenote_dump import pipeline
from onenote_dump.core import OneNoteCore

logger = logging.getLogger(__name__)

class OneNoteInteractor:
    def __init__(self, verbose: bool = False):
        """
        初始化 OneNote 交互器
        
        Args:
            verbose: 是否显示详细日志
        """
        self.core = OneNoteCore(verbose=verbose)
    
    def list_notebooks(self) -> List[Dict[str, Any]]:
        """列出所有笔记本"""
        return self.core.get_notebooks()
    
    def search_notes(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索笔记（待实现：需要 Microsoft Graph API 的搜索功能）
        
        Args:
            keyword: 搜索关键词
        """
        # TODO: 实现笔记搜索功能
        raise NotImplementedError("Search functionality not implemented yet")
    
    def get_recent_notes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近的笔记（待实现：需要按时间排序的API）
        
        Args:
            limit: 返回的笔记数量
        """
        # TODO: 实现最近笔记获取
        raise NotImplementedError("Recent notes functionality not implemented yet")
    
    def dump_notebook(self, 
                     notebook_name: str,
                     output_dir: str,
                     section_name: Optional[str] = None,
                     max_pages: Optional[int] = None,
                     start_page: Optional[int] = None,
                     new_session: bool = False) -> Dict[str, Any]:
        """
        导出笔记本内容到指定目录
        
        Args:
            notebook_name: 要导出的笔记本名称
            output_dir: 输出目录
            section_name: 可选，指定要导出的分区名称
            max_pages: 可选，最大导出页面数
            start_page: 可选，开始导出的页面编号
            new_session: 是否使用新的会话（忽略保存的认证令牌）
        
        Returns:
            包含导出结果的字典，包括：
            - total_pages: 导出的总页数
            - duration_seconds: 导出耗时（秒）
            - output_path: 输出目录路径
        """
        if new_session:
            self.core = OneNoteCore(verbose=self.core.verbose, new_session=True)
            
        start_time = datetime.now()
        page_count = 0
        pages_exported = 0
        
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 创建处理管道
        pipe = pipeline.Pipeline(
            self.core.session_info,
            notebook_name,
            output_path
        )
        
        try:
            # 获取并处理页面
            for page in self.core.get_notebook_pages(notebook_name, section_name):
                page_count += 1
                log_msg = f'Page {page_count}: {page["title"]}'
                
                if start_page is None or page_count >= start_page:
                    logger.info(log_msg)
                    pipe.add_page(page)
                    pages_exported += 1
                else:
                    logger.info(log_msg + " [skipped]")
                    
                if max_pages and page_count >= max_pages:
                    break
                    
        except onenote.NotebookNotFound as e:
            logger.error(str(e))
            raise
        finally:
            pipe.done()
            
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Done! Exported {pages_exported} pages in {duration:.1f} seconds")
        
        return {
            "total_pages": pages_exported,
            "duration_seconds": duration,
            "output_path": str(output_path)
        }
    
    def create_note(self, notebook_name: str, content: str):
        """
        创建新笔记（待实现：需要写入API权限）
        
        Args:
            notebook_name: 笔记本名称
            content: 笔记内容
        """
        # TODO: 实现笔记创建
        raise NotImplementedError("Create note functionality not implemented yet")
