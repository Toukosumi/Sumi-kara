"""VideoDownloader 模块配置类 - 统一管理视频下载模块的默认配置."""
import os
from typing import Any, Dict, Optional


class VideoDownloaderConfig:
    """视频下载模块配置类"""

    # 配置项键名
    CONFIG_KEY_DOWNLOAD_PATH = "video_download_path"
    CONFIG_KEY_VIDEO_FORMAT = "video_download_format"
    CONFIG_KEY_AUDIO_FORMAT = "video_audio_format"
    CONFIG_KEY_YT_DLP_PATH = "yt_dlp_path"
    CONFIG_KEY_FFMPEG_PATH = "ffmpeg_path"
    CONFIG_KEY_PROXY_ENABLED = "video_proxy_enabled"
    CONFIG_KEY_PROXY_URL = "video_proxy_url"

    # 默认配置值
    DEFAULT_YT_DLP_PATH = r"D:\Learning\Subtitles\FFmpeg\bin\yt-dlp.exe"
    DEFAULT_FFMPEG_PATH = r"D:\Learning\Subtitles\FFmpeg\bin\ffmpeg.exe"
    DEFAULT_FORMAT = "mp4"
    DEFAULT_AUDIO_FORMAT = "mp3"
    DEFAULT_DOWNLOAD_PATH = "./downloads"
    DEFAULT_PROXY_URL = "http://127.0.0.1:7890"

    # 支持的视频格式
    SUPPORTED_VIDEO_FORMATS = ["mp4", "mkv", "webm", "avi"]
    # 支持的音频格式
    SUPPORTED_AUDIO_FORMATS = ["mp3", "m4a", "wav", "flac"]

    @classmethod
    def get_default_config(cls) -> Dict[str, Any]:
        """获取默认配置字典

        Returns:
            默认配置字典
        """
        return {
            cls.CONFIG_KEY_DOWNLOAD_PATH: cls.DEFAULT_DOWNLOAD_PATH,
            cls.CONFIG_KEY_VIDEO_FORMAT: cls.DEFAULT_FORMAT,
            cls.CONFIG_KEY_AUDIO_FORMAT: cls.DEFAULT_AUDIO_FORMAT,
            cls.CONFIG_KEY_YT_DLP_PATH: cls.DEFAULT_YT_DLP_PATH,
            cls.CONFIG_KEY_FFMPEG_PATH: cls.DEFAULT_FFMPEG_PATH,
            cls.CONFIG_KEY_PROXY_ENABLED: True,
            cls.CONFIG_KEY_PROXY_URL: cls.DEFAULT_PROXY_URL,
        }

    @classmethod
    def validate_yt_dlp_path(cls, path: str) -> bool:
        """验证 yt-dlp 路径是否有效

        Args:
            path: yt-dlp 可执行文件路径

        Returns:
            路径是否有效
        """
        return os.path.isfile(path) and path.endswith('.exe')

    @classmethod
    def validate_ffmpeg_path(cls, path: str) -> bool:
        """验证 ffmpeg 路径是否有效

        Args:
            path: ffmpeg 可执行文件路径

        Returns:
            路径是否有效
        """
        return os.path.isfile(path) and path.endswith('.exe')

    @classmethod
    def validate_download_path(cls, path: str) -> bool:
        """验证下载路径是否有效

        Args:
            path: 下载保存路径

        Returns:
            路径是否有效（目录存在或可创建）
        """
        if os.path.exists(path):
            return os.path.isdir(path)
        # 尝试创建目录
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except (OSError, PermissionError):
            return False

    @classmethod
    def validate_format(cls, format_str: str, is_audio: bool = False) -> bool:
        """验证格式是否支持

        Args:
            format_str: 格式字符串
            is_audio: 是否为音频格式

        Returns:
            格式是否支持
        """
        if is_audio:
            return format_str.lower() in cls.SUPPORTED_AUDIO_FORMATS
        return format_str.lower() in cls.SUPPORTED_VIDEO_FORMATS
