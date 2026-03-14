"""Video format parser worker - 使用 yt-dlp -F 解析视频格式."""
import os
import re
from typing import List, Optional

from PyQt5.QtCore import QThread, pyqtSignal, QProcess

from utils import logger
from utils.url_utils import (
    YOUTUBE_DOMAINS,
    BILIBILI_DOMAINS,
    is_bilibili_url,
    should_use_proxy
)


class VideoFormatInfo:
    """视频格式信息"""

    def __init__(self, format_id: str, ext: str, resolution: str, fps: str = "", filesize: str = ""):
        self.format_id = format_id
        self.ext = ext
        self.resolution = resolution
        self.fps = fps
        # 统一转换为 MB
        self.filesize = self._convert_to_mb(filesize)

    def _convert_to_mb(self, size_str: str) -> str:
        """将文件大小转换为 MB 格式"""
        if not size_str:
            return ""
        size_str = size_str.strip()
        try:
            # 处理 MiB, GiB, kiB 格式
            if 'GiB' in size_str:
                value = float(size_str.replace('GiB', '').replace('~', '').strip())
                return f"{value * 1024:.1f}M"
            elif 'MiB' in size_str:
                value = float(size_str.replace('MiB', '').replace('~', '').strip())
                return f"{value:.1f}M"
            elif 'kiB' in size_str:
                value = float(size_str.replace('kiB', '').replace('~', '').strip())
                return f"{value / 1024:.1f}M"
            # 处理旧格式 M, K, G
            size_upper = size_str.upper()
            if size_upper.endswith('G'):
                value = float(size_upper[:-1])
                return f"{value * 1024:.1f}M"
            elif size_upper.endswith('M'):
                return size_str
            elif size_upper.endswith('K'):
                value = float(size_upper[:-1])
                return f"{value / 1024:.1f}M"
        except (ValueError, AttributeError):
            pass
        return size_str

    def __repr__(self):
        return f"VideoFormatInfo(id={self.format_id}, ext={self.ext}, resolution={self.resolution}, fps={self.fps}, filesize={self.filesize})"


class VideoFormatParser(QThread):
    """视频格式解析工作线程 - 使用 yt-dlp -F 获取可用格式"""

    # 信号定义
    parse_started = pyqtSignal()  # 开始解析
    parse_finished = pyqtSignal(bool, str, list, list)  # 成功标志, 消息, 视频格式列表, 音频格式列表
    status_changed = pyqtSignal(str)  # 状态变化

    def __init__(
        self,
        url: str,
        yt_dlp_path: str,
        proxy_enabled: bool = False,
        proxy_url: str = ""
    ):
        """初始化格式解析工作线程

        Args:
            url: 视频URL
            yt_dlp_path: yt-dlp.exe 路径
            proxy_enabled: 是否启用代理
            proxy_url: 代理地址
        """
        super().__init__()
        self._url = url
        self._yt_dlp_path = yt_dlp_path
        self._proxy_enabled = proxy_enabled
        self._proxy_url = proxy_url
        self._process: Optional[QProcess] = None
        self._stop_flag = False
        self._video_formats: List[VideoFormatInfo] = []
        self._audio_formats: List[VideoFormatInfo] = []

    def run(self):
        """主线程函数 - 执行格式解析"""
        self.parse_started.emit()
        self.status_changed.emit("正在解析视频格式...")

        # 检查 yt-dlp.exe 是否存在
        if not os.path.exists(self._yt_dlp_path):
            error_msg = f"yt-dlp.exe 不存在: {self._yt_dlp_path}"
            logger.error(error_msg)
            self.parse_finished.emit(False, error_msg, [], [])
            return

        # 构建 yt-dlp -F 命令参数
        args = self._build_arguments()

        logger.info(f"开始解析: {self._url}")
        logger.info(f"yt-dlp路径: {self._yt_dlp_path}")
        logger.info(f"参数: {' '.join(args)}")

        # 创建 QProcess
        self._process = QProcess(self)
        # 合并 stdout 和 stderr
        self._process.setProcessChannelMode(QProcess.MergedChannels)

        # 连接信号
        self._process.readyReadStandardOutput.connect(self._handle_output)
        self._process.finished.connect(lambda code: self._handle_finished(code))
        self._process.errorOccurred.connect(self._handle_error)

        # 启动进程
        self._process.start(self._yt_dlp_path, args)

        # 等待进程完成
        self._process.waitForFinished(-1)

    def _build_arguments(self) -> list:
        """构建 yt-dlp -F 命令行参数

        Returns:
            参数列表
        """
        args = [
            "-F",                      # 列出所有可用格式
            "--no-playlist",           # 不解析播放列表
            "--no-warnings",          # 不显示警告
            "--no-color",             # 不使用颜色
        ]

        # 添加 ffmpeg 路径（如果存在）- 使用 tool_manager 获取
        from utils.tool_manager import ToolManager
        tool_paths = ToolManager.get_tool_paths()
        ffmpeg_path = tool_paths.get("ffmpeg_path", "")
        if ffmpeg_path and os.path.exists(ffmpeg_path):
            args.extend(["--ffmpeg-location", os.path.dirname(ffmpeg_path)])

        # B站特殊处理：跳过证书检查
        if self._is_bilibili_url(self._url):
            args.append("--no-check-certificate")

        # 判断是否需要使用代理
        if self._should_use_proxy(self._url):
            proxy = self._proxy_url if self._proxy_url else "http://127.0.0.1:7890"
            args.extend(["--proxy", proxy])
            logger.info(f"URL {self._url} 将使用代理: {proxy}")

        # 添加 URL
        args.append(self._url)

        return args

    def _should_use_proxy(self, url: str) -> bool:
        """判断 URL 是否需要使用代理"""
        return should_use_proxy(url, self._proxy_enabled)

    def _is_bilibili_url(self, url: str) -> bool:
        """判断是否是B站URL"""
        return is_bilibili_url(url)

    def _handle_output(self):
        """处理进程输出 - 解析格式信息"""
        if self._process is None:
            return

        raw_output = bytes(self._process.readAllStandardOutput())
        try:
            output = raw_output.decode("utf-8", errors="ignore")
        except:
            try:
                output = raw_output.decode("gbk", errors="ignore")
            except:
                output = raw_output.decode("utf-8", errors="replace")

        # 解析格式信息
        self._parse_format_info(output)

    def _parse_format_info(self, output: str):
        """解析 yt-dlp -F 输出

        Args:
            output: yt-dlp 输出内容
        """
        self._video_formats = []
        self._audio_formats = []

        lines = output.splitlines()
        in_format_section = False

        for line in lines:
            line = line.strip()

            # 检测格式信息开始
            if "ID" in line and "EXT" in line and "RESOLUTION" in line:
                in_format_section = True
                continue

            if not in_format_section or not line:
                continue

            # 跳过包含 ~ 的行（预估大小）
            if '~' in line:
                continue

            # 解析格式行: 137 mp4 1920x1080 60 3.5M 1.36M
            # 格式: format_id extension resolution fps bitrate filesize
            parts = line.split()
            if len(parts) < 5:
                continue

            format_id = parts[0]
            ext = parts[1]

            # 判断是视频还是音频
            is_video = False
            is_audio = False

            # 检查是否有 video only 或 audio only 标记
            if "video only" in line.lower():
                is_video = True
            elif "audio only" in line.lower():
                is_audio = True
            elif len(parts) >= 3:
                # 根据分辨率判断 (格式: widthxheight 或 1920x1080)
                resolution = parts[2]
                if 'x' in resolution:
                    is_video = True
                elif resolution == "audio":
                    is_audio = True

            # 提取分辨率、fps和文件大小
            resolution = ""
            fps = ""
            filesize = ""

            if is_video:
                # 查找分辨率 (格式: WIDTHxHEIGHT)
                for part in parts:
                    if 'x' in part and part[0].isdigit():
                        resolution = part
                        break

                # 查找fps - 在分辨率后面的数字
                for i, part in enumerate(parts):
                    if part == resolution and i + 1 < len(parts):
                        # 下一个可能是fps
                        next_part = parts[i + 1]
                        if next_part.isdigit():
                            fps = next_part + "fps"
                        break

                # 查找文件大小 - 优先找包含 ~ 的值（约等于），其次找 MiB/GiB 结尾的精确值
                filesize = ""
                for part in parts:
                    # 优先匹配 ~ 开头的文件大小（约等于）
                    if part.startswith('~') and ('MiB' in part or 'GiB' in part or 'kiB' in part):
                        filesize = part.replace('~', '')
                        break
                # 如果没找到，再找精确的文件大小
                if not filesize:
                    for part in parts:
                        if part.endswith('MiB') or part.endswith('GiB') or part.endswith('kiB'):
                            filesize = part
                            break

                if resolution:
                    self._video_formats.append(VideoFormatInfo(format_id, ext, resolution, fps, filesize))

            elif is_audio:
                # 查找文件大小 - 同上逻辑
                filesize = ""
                for part in parts:
                    if part.startswith('~') and ('MiB' in part or 'GiB' in part or 'kiB' in part):
                        filesize = part.replace('~', '')
                        break
                if not filesize:
                    for part in parts:
                        if part.endswith('MiB') or part.endswith('GiB') or part.endswith('kiB'):
                            filesize = part
                            break

                self._audio_formats.append(VideoFormatInfo(format_id, ext, "", "", filesize))

        logger.info(f"解析到 {len(self._video_formats)} 个视频格式, {len(self._audio_formats)} 个音频格式")

    def _handle_finished(self, exit_code: int):
        """处理进程结束"""
        if self._stop_flag:
            self.parse_finished.emit(False, "用户取消", [], [])
            return

        if exit_code == 0:
            self.parse_finished.emit(True, "解析成功", self._video_formats, self._audio_formats)
            logger.info(f"格式解析成功: {len(self._video_formats)} 视频, {len(self._audio_formats)} 音频")
        else:
            self.parse_finished.emit(False, f"解析失败，退出代码: {exit_code}", [], [])
            logger.error(f"格式解析失败: {exit_code}")

    def _handle_error(self, error: QProcess.FailedStartError):
        """处理进程启动错误"""
        error_msg = f"启动 yt-dlp 失败: {error}"
        self.parse_finished.emit(False, error_msg, [], [])
        logger.error(error_msg)

    def stop(self):
        """停止解析"""
        self._stop_flag = True
        if self._process is not None and self._process.state() == QProcess.Running:
            self._process.terminate()
            self._process.waitForFinished(3000)

    def get_video_formats(self) -> List[VideoFormatInfo]:
        """获取视频格式列表"""
        return self._video_formats

    def get_audio_formats(self) -> List[VideoFormatInfo]:
        """获取音频格式列表"""
        return self._audio_formats
