"""Video downloader module - 使用 yt-dlp 下载视频."""
import os
from typing import Any, Dict, List, Optional

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget

from config.global_config import global_config
from modules.base.module_base import ModuleBase
from modules.impl.video_download_worker import VideoDownloadWorker
from modules.impl.video_format_parser import VideoFormatParser, VideoFormatInfo
from modules.impl.video_downloader_config import VideoDownloaderConfig
from utils import logger


class VideoDownloaderModule(QObject, ModuleBase):
    """视频下载模块 - 使用 yt-dlp"""

    # 信号定义 - 用于UI更新
    progress_updated = pyqtSignal(float, str)  # 进度(0-1), 状态消息
    download_finished = pyqtSignal(str, bool, str)  # url, 成功标志, 消息
    status_changed = pyqtSignal(str)  # 状态变化

    # 解析相关信号
    parse_started = pyqtSignal()  # 开始解析
    parse_finished = pyqtSignal(bool, str, list, list)  # 成功, 消息, 视频格式, 音频格式

    def __init__(self) -> None:
        QObject.__init__(self)
        ModuleBase.__init__(self)
        self._config_widget: Optional[QWidget] = None
        self._current_worker: Optional[VideoDownloadWorker] = None
        self._current_parser: Optional[VideoFormatParser] = None
        # 存储解析后的格式信息
        self._parsed_video_formats: List[VideoFormatInfo] = []
        self._parsed_audio_formats: List[VideoFormatInfo] = []
        self._current_url: str = ""
        self._init_default_config()

    def _init_default_config(self):
        """初始化默认配置项"""
        # 获取默认配置
        default_config = VideoDownloaderConfig.get_default_config()

        # 遍历默认配置，初始化未设置的配置项
        for key, value in default_config.items():
            if global_config.get(key) is None:
                global_config.set(key, value)

        logger.info("视频下载模块配置已初始化")

    def get_name(self) -> str:
        """获取模块名称"""
        return "视频下载"

    def get_version(self) -> str:
        """获取模块版本"""
        return "1.0.0"

    def get_description(self) -> str:
        """获取模块描述"""
        return "下载视频/音频，支持YouTube、B站等平台"

    def get_config_widget(self, parent: Optional[QWidget] = None) -> Optional[QWidget]:
        """返回配置widget

        Args:
            parent: 父窗口

        Returns:
            配置界面widget
        """
        if self._config_widget is None:
            from ui.widgets.video_download_config import VideoDownloaderConfigWidget
            self._config_widget = VideoDownloaderConfigWidget(parent, self)
        return self._config_widget

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行下载任务

        Args:
            params: 参数字典，包含 url，可选 video_format_id, audio_format_id

        Returns:
            执行结果
        """
        url = params.get("url", "").strip()
        if not url:
            return {"status": "error", "message": "URL不能为空"}

        # 检查是否已有下载任务在进行
        if self._current_worker is not None and self._current_worker.isRunning():
            return {"status": "error", "message": "已有下载任务在进行中"}

        # 获取配置
        download_path = global_config.get(
            VideoDownloaderConfig.CONFIG_KEY_DOWNLOAD_PATH,
            VideoDownloaderConfig.DEFAULT_DOWNLOAD_PATH
        )
        video_format = global_config.get(
            VideoDownloaderConfig.CONFIG_KEY_VIDEO_FORMAT,
            VideoDownloaderConfig.DEFAULT_FORMAT
        )
        yt_dlp_path = global_config.get(
            VideoDownloaderConfig.CONFIG_KEY_YT_DLP_PATH,
            VideoDownloaderConfig.DEFAULT_YT_DLP_PATH
        )
        ffmpeg_path = global_config.get(
            VideoDownloaderConfig.CONFIG_KEY_FFMPEG_PATH,
            VideoDownloaderConfig.DEFAULT_FFMPEG_PATH
        )
        proxy_enabled = global_config.get(VideoDownloaderConfig.CONFIG_KEY_PROXY_ENABLED, True)
        proxy_url = global_config.get(
            VideoDownloaderConfig.CONFIG_KEY_PROXY_URL,
            VideoDownloaderConfig.DEFAULT_PROXY_URL
        )

        # 获取用户选择的格式ID（可选）
        video_format_id = params.get("video_format_id")
        audio_format_id = params.get("audio_format_id")

        # 检查 yt-dlp.exe 是否存在
        if not os.path.exists(yt_dlp_path):
            return {"status": "error", "message": f"yt-dlp.exe 不存在: {yt_dlp_path}"}

        # 创建并启动下载worker
        self._current_worker = VideoDownloadWorker(
            url=url,
            download_path=download_path,
            video_format=video_format,
            yt_dlp_path=yt_dlp_path,
            ffmpeg_path=ffmpeg_path,
            proxy_enabled=proxy_enabled,
            proxy_url=proxy_url,
            video_format_id=video_format_id,
            audio_format_id=audio_format_id
        )

        # 连接信号
        self._current_worker.progress_updated.connect(self._on_progress_updated)
        self._current_worker.download_finished.connect(self._on_download_finished)
        self._current_worker.status_changed.connect(self._on_status_changed)

        # 启动下载
        self._current_worker.start()

        logger.info(f"开始下载: {url}")
        return {"status": "started", "message": "下载已开始"}

    def parse_formats(self, url: str) -> Dict[str, Any]:
        """解析视频可用格式

        Args:
            url: 视频URL

        Returns:
            执行结果
        """
        url = url.strip()
        if not url:
            return {"status": "error", "message": "URL不能为空"}

        # 检查是否已有解析任务在进行
        if self._current_parser is not None and self._current_parser.isRunning():
            return {"status": "error", "message": "已有解析任务在进行中"}

        # 检查是否已有下载任务在进行
        if self._current_worker is not None and self._current_worker.isRunning():
            return {"status": "error", "message": "已有下载任务在进行中"}

        # 获取配置
        yt_dlp_path = global_config.get(
            VideoDownloaderConfig.CONFIG_KEY_YT_DLP_PATH,
            VideoDownloaderConfig.DEFAULT_YT_DLP_PATH
        )
        proxy_enabled = global_config.get(VideoDownloaderConfig.CONFIG_KEY_PROXY_ENABLED, True)
        proxy_url = global_config.get(
            VideoDownloaderConfig.CONFIG_KEY_PROXY_URL,
            VideoDownloaderConfig.DEFAULT_PROXY_URL
        )

        # 检查 yt-dlp.exe 是否存在
        if not os.path.exists(yt_dlp_path):
            return {"status": "error", "message": f"yt-dlp.exe 不存在: {yt_dlp_path}"}

        # 保存当前URL
        self._current_url = url

        # 创建并启动解析worker
        self._current_parser = VideoFormatParser(
            url=url,
            yt_dlp_path=yt_dlp_path,
            proxy_enabled=proxy_enabled,
            proxy_url=proxy_url
        )

        # 连接信号
        self._current_parser.parse_started.connect(self._on_parse_started)
        self._current_parser.parse_finished.connect(self._on_parse_finished)
        self._current_parser.status_changed.connect(self._on_status_changed)

        # 启动解析
        self._current_parser.start()

        logger.info(f"开始解析: {url}")
        return {"status": "started", "message": "解析已开始"}

    def _on_parse_started(self):
        """解析开始"""
        self.parse_started.emit()

    def _on_parse_finished(self, success: bool, message: str, video_formats: list, audio_formats: list):
        """解析完成"""
        if success:
            self._parsed_video_formats = video_formats
            self._parsed_audio_formats = audio_formats
            logger.info(f"解析成功: {len(video_formats)} 视频格式, {len(audio_formats)} 音频格式")
        else:
            self._parsed_video_formats = []
            self._parsed_audio_formats = []
            logger.error(f"解析失败: {message}")

        self.parse_finished.emit(success, message, video_formats, audio_formats)
        self._current_parser = None

    def get_parsed_formats(self) -> tuple:
        """获取解析后的格式信息

        Returns:
            (视频格式列表, 音频格式列表)
        """
        return (self._parsed_video_formats, self._parsed_audio_formats)

    def get_current_url(self) -> str:
        """获取当前解析/下载的URL"""
        return self._current_url

    def _on_progress_updated(self, progress: float, message: str):
        """进度更新槽函数"""
        self.progress_updated.emit(progress, message)

    def _on_download_finished(self, url: str, success: bool, message: str):
        """下载完成槽函数"""
        self.download_finished.emit(url, success, message)
        self._current_worker = None

    def _on_status_changed(self, status: str):
        """状态变化槽函数"""
        self.status_changed.emit(status)

    def get_progress(self) -> float:
        """获取当前下载进度

        Returns:
            进度 (0.0 - 1.0)
        """
        if self._current_worker is not None and self._current_worker.isRunning():
            return self._current_worker.get_progress()
        return 0.0

    def stop(self):
        """停止当前下载或解析"""
        # 停止下载任务
        if self._current_worker is not None and self._current_worker.isRunning():
            logger.info("VideoDownloaderModule: 停止下载")
            self._current_worker.stop()
            self._current_worker.wait()
            logger.info("VideoDownloaderModule: 下载已停止")
            self._current_worker = None

        # 停止解析任务
        if self._current_parser is not None and self._current_parser.isRunning():
            logger.info("VideoDownloaderModule: 停止解析")
            self._current_parser.stop()
            self._current_parser.wait()
            logger.info("VideoDownloaderModule: 解析已停止")
            self._current_parser = None
