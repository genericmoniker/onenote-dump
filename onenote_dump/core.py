from typing import Optional, List, Dict, Any, Generator
import logging
from pathlib import Path
from requests import Session

from onenote_dump import onenote_auth, onenote, log

logger = logging.getLogger(__name__)

class OneNoteCore:
    """OneNote API 核心操作类"""
    
    def __init__(self, verbose: bool = False, new_session: bool = False):
        """
        初始化 OneNote 核心操作类
        
        Args:
            verbose: 是否显示详细日志
            new_session: 是否使用新会话
        """
        # 设置日志级别
        log_level = logging.DEBUG if verbose else logging.INFO
        log.setup_logging(log_level)
        
        # 初始化会话
        self.session = onenote_auth.get_session(new_session)
        
    def get_notebooks(self) -> List[Dict[str, Any]]:
        """获取所有笔记本"""
        notebooks = onenote.get_notebooks(self.session)
        return notebooks["value"] if isinstance(notebooks, dict) else notebooks
    
    def get_notebook_pages(self, 
                          notebook_name: str, 
                          section_name: Optional[str] = None) -> Generator[Dict[str, Any], None, None]:
        """
        获取笔记本中的所有页面
        
        Args:
            notebook_name: 笔记本名称
            section_name: 可选的分区名称
        
        Yields:
            页面信息
        """
        return onenote.get_notebook_pages(self.session, notebook_name, section_name)
    
    def get_page_content(self, page: Dict[str, Any]) -> tuple:
        """
        获取页面内容
        
        Args:
            page: 页面信息字典
        
        Returns:
            (page, content) 元组
        """
        return onenote.get_page_content(self.session, page)
    
    @property
    def session_info(self) -> Session:
        """获取当前会话"""
        return self.session
