"""Lyric downloader module."""
from typing import Any, Dict

from modules.base.module_base import ModuleBase
from utils import logger


class LyricDownloaderModule(ModuleBase):
    """Lyric downloader module."""

    def get_name(self) -> str:
        return "歌词下载"

    def get_version(self) -> str:
        return "1.0.0"

    def get_description(self) -> str:
        return "下载歌曲歌词，支持LRC格式"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("LyricDownloaderModule: 执行歌词下载")
        return {"status": "pending", "message": "模块预留，尚未实现"}

    def get_progress(self) -> float:
        return 0.0

    def stop(self):
        logger.info("LyricDownloaderModule: 停止下载")
