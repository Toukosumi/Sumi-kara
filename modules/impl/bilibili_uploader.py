"""Bilibili uploader module."""
from typing import Any, Dict

from modules.base.module_base import ModuleBase
from utils import logger


class BilibiliUploaderModule(ModuleBase):
    """Bilibili (B站) video uploader module."""

    def get_name(self) -> str:
        return "B站上传"

    def get_version(self) -> str:
        return "1.0.0"

    def get_description(self) -> str:
        return "自动上传视频到Bilibili"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("BilibiliUploaderModule: 执行B站上传")
        return {"status": "pending", "message": "模块预留，尚未实现"}

    def get_progress(self) -> float:
        return 0.0

    def stop(self):
        logger.info("BilibiliUploaderModule: 停止上传")
