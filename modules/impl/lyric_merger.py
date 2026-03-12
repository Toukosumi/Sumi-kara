"""Lyric merger module."""
from typing import Any, Dict

from modules.base.module_base import ModuleBase
from utils import logger


class LyricMergerModule(ModuleBase):
    """Lyric merger module - merges video and lyric."""

    def get_name(self) -> str:
        return "歌词合成"

    def get_version(self) -> str:
        return "1.0.0"

    def get_description(self) -> str:
        return "将歌词嵌入视频，制作卡拉OK效果"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("LyricMergerModule: 执行歌词合成")
        return {"status": "pending", "message": "模块预留，尚未实现"}

    def get_progress(self) -> float:
        return 0.0

    def stop(self):
        logger.info("LyricMergerModule: 停止合成")
