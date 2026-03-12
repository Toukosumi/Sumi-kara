"""Video download worker - 使用 QProcess 调用 yt-dlp.exe."""
import os
import re
from typing import Optional
from urllib.parse import urlparse

from PyQt5.QtCore import QThread, pyqtSignal, QProcess

from utils import logger


class VideoDownloadWorker(QThread):
    """视频下载工作线程 - 使用QProcess调用yt-dlp"""

    # 信号定义
    progress_updated = pyqtSignal(float, str)  # 进度(0-1), 状态消息
    download_finished = pyqtSignal(str, bool, str)  # url, 成功标志, 消息
    status_changed = pyqtSignal(str)  # 状态变化

    # YouTube 域名列表
    YOUTUBE_DOMAINS = ['youtube.com', 'youtu.be', 'youtube-nocookie.com']

    def __init__(
        self,
        url: str,
        download_path: str,
        video_format: str,
        yt_dlp_path: str,
        ffmpeg_path: str,
        proxy_enabled: bool = False,
        proxy_url: str = "",
        video_format_id: Optional[str] = None,
        audio_format_id: Optional[str] = None
    ):
        """初始化下载工作线程

        Args:
            url: 视频URL
            download_path: 保存路径
            video_format: 视频格式 (mp4/mp3/webm/mkv/best)
            yt_dlp_path: yt-dlp.exe 路径
            ffmpeg_path: ffmpeg.exe 路径
            proxy_enabled: 是否启用代理
            proxy_url: 代理地址
            video_format_id: 指定的视频格式ID（可选）
            指定的音频格式ID（可选）
 audio_format_id:        """
        super().__init__()
        self._url = url
        self._download_path = download_path
        self._video_format = video_format
        self._yt_dlp_path = yt_dlp_path
        self._ffmpeg_path = ffmpeg_path
        self._proxy_enabled = proxy_enabled
        self._proxy_url = proxy_url
        self._video_format_id = video_format_id
        self._audio_format_id = audio_format_id
        self._process: Optional[QProcess] = None
        self._current_filename = ""
        self._progress = 0.0
        self._stop_flag = False

    def run(self):
        """主线程函数 - 执行下载"""
        self.status_changed.emit("正在初始化下载...")

        # 确保下载目录存在
        os.makedirs(self._download_path, exist_ok=True)

        # 检查 yt-dlp.exe 是否存在
        if not os.path.exists(self._yt_dlp_path):
            error_msg = f"yt-dlp.exe 不存在: {self._yt_dlp_path}"
            logger.error(error_msg)
            self.download_finished.emit(self._url, False, error_msg)
            return

        # 构建 yt-dlp 命令参数
        args = self._build_arguments()

        logger.info(f"开始下载: {self._url}")
        logger.info(f"yt-dlp路径: {self._yt_dlp_path}")
        logger.info(f"保存路径: {self._download_path}")
        logger.info(f"视频格式: {self._video_format}")
        logger.info(f"代理启用: {self._proxy_enabled}, URL: {self._proxy_url}")
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

        # 等待进程完成（无限等待）
        self._process.waitForFinished(-1)

    def _build_arguments(self) -> list:
        """构建 yt-dlp 命令行参数

        Returns:
            参数列表
        """
        args = [
            "--no-playlist",           # 不下载播放列表
            "--no-warnings",           # 不显示警告
            "--no-color",              # 不使用颜色
            "--progress",              # 显示进度
            "--newline",               # 换行输出
            "-o", os.path.join(self._download_path, "%(title)s.%(ext)s"),
        ]

        # 如果用户指定了格式ID，使用指定格式
        if self._video_format_id or self._audio_format_id:
            # 指定的格式下载
            if self._video_format_id and self._audio_format_id:
                # 同时指定视频和音频格式，需要合并
                format_str = f"{self._video_format_id}+{self._audio_format_id}"
                args.extend(["-f", format_str])
                # 自动检测输出格式
                args.extend(["--merge-output-format", "mkv"])
            elif self._video_format_id:
                # 只指定视频格式
                args.extend(["-f", self._video_format_id])
            elif self._audio_format_id:
                # 只指定音频格式，提取音频
                args.extend(["-f", self._audio_format_id, "-x"])
        else:
            # 根据格式添加参数（原有逻辑）
            if self._video_format == "mp3":
                args.extend([
                    "-x",                           # 提取音频
                    "--audio-format", "mp3",
                    "--audio-quality", "0",         # 最高质量
                ])
            elif self._video_format == "mp4":
                args.extend([
                    "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                    "--merge-output-format", "mp4",
                ])
            elif self._video_format == "webm":
                args.extend([
                    "-f", "bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best",
                    "--merge-output-format", "webm",
                ])
            elif self._video_format == "mkv":
                args.extend([
                    "-f", "bestvideo+bestaudio/best",
                    "--merge-output-format", "mkv",
                ])
            elif self._video_format == "bestvideo+bestaudio":
                args.extend(["-f", "bestvideo+bestaudio/best"])

        # 添加 ffmpeg 路径（如果存在）
        if os.path.exists(self._ffmpeg_path):
            args.extend(["--ffmpeg-location", os.path.dirname(self._ffmpeg_path)])

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

    # B站域名列表
    BILIBILI_DOMAINS = ['bilibili.com', 'b23.tv']

    def _should_use_proxy(self, url: str) -> bool:
        """判断 URL 是否需要使用代理

        Args:
            url: 视频URL

        Returns:
            是否需要代理
        """
        if not self._proxy_enabled:
            return False

        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            # 移除端口号
            if ':' in domain:
                domain = domain.split(':')[0]

            # 检查是否匹配 YouTube 域名
            for yt_domain in self.YOUTUBE_DOMAINS:
                if yt_domain in domain or domain.endswith(yt_domain):
                    return True

            return False
        except Exception as e:
            logger.warning(f"解析URL域名失败: {url}, 错误: {e}")
            return False

    def _is_bilibili_url(self, url: str) -> bool:
        """判断是否是B站URL

        Args:
            url: 视频URL

        Returns:
            是否是B站
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if ':' in domain:
                domain = domain.split(':')[0]
            for bili_domain in self.BILIBILI_DOMAINS:
                if bili_domain in domain or domain.endswith(bili_domain):
                    return True
            return False
        except:
            return False

    def _handle_output(self):
        """处理进程输出 - 解析进度"""
        if self._process is None:
            return

        # 读取所有输出，尝试多种编码
        raw_output = bytes(self._process.readAllStandardOutput())
        try:
            output = raw_output.decode("utf-8", errors="ignore")
        except:
            try:
                output = raw_output.decode("gbk", errors="ignore")
            except:
                output = raw_output.decode("utf-8", errors="replace")

        for line in output.splitlines():
            if self._stop_flag:
                break

            line = line.strip()
            if not line:
                continue

            # 解析进度 - yt-dlp 格式: [download] 45.3% of 100.00MiB at 2.50MiB/s ETA 00:30
            progress_match = re.search(r"(\d+\.?\d*)%", line)
            if progress_match:
                progress = float(progress_match.group(1)) / 100.0
                self._progress = progress
                self.progress_updated.emit(progress, line)
                continue

            # 解析文件名 - [download] Destination: video.mp4
            dest_match = re.search(r"Destination:\s+(.+)", line)
            if dest_match:
                self._current_filename = dest_match.group(1)
                self.status_changed.emit(f"正在下载: {self._current_filename}")
                continue

            # 解析下载完成 - [download] video.mp4 has already been downloaded
            if "has already been downloaded" in line:
                self._progress = 1.0
                self.progress_updated.emit(1.0, "已完成 (文件已存在)")
                continue

            # 解析合并格式 - [download] Merging formats into 'video.mp4'
            if "Merging formats into" in line:
                self.status_changed.emit("正在合并音视频...")
                continue

            # 解析完成 - [download] Finished downloading
            if "Finished downloading" in line:
                self._progress = 1.0
                self.progress_updated.emit(1.0, "下载完成")
                continue

    def _handle_finished(self, exit_code: int):
        """处理进程结束

        Args:
            exit_code: 退出代码
        """
        if self._stop_flag:
            self.download_finished.emit(self._url, False, "用户取消")
            return

        if exit_code == 0:
            filename = self._current_filename or "未知文件"
            self.download_finished.emit(self._url, True, filename)
            logger.info(f"下载成功: {self._url} -> {filename}")
        else:
            error_msg = f"下载失败，退出代码: {exit_code}"
            self.download_finished.emit(self._url, False, error_msg)
            logger.error(f"下载失败: {self._url}, 退出代码: {exit_code}")

    def _handle_error(self, error: QProcess.FailedStartError):
        """处理进程启动错误

        Args:
            error: 错误类型
        """
        error_msg = f"启动 yt-dlp 失败: {error}"
        self.download_finished.emit(self._url, False, error_msg)
        logger.error(error_msg)

    def get_progress(self) -> float:
        """获取当前下载进度

        Returns:
            进度 (0.0 - 1.0)
        """
        return self._progress

    def stop(self):
        """停止下载"""
        logger.info("正在停止下载...")
        self._stop_flag = True

        if self._process is not None:
            if self._process.state() == QProcess.Running:
                # 先尝试正常终止
                self._process.terminate()
                # 等待3秒让进程退出
                if not self._process.waitForFinished(3000):
                    # 如果还没退出，强制杀死
                    self._process.kill()
                    logger.info("已强制终止下载进程")

        logger.info("下载已停止")
