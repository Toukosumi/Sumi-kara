"""Video downloader configuration widget."""
from typing import Optional, List

from PyQt5.QtCore import Qt, pyqtSlot, QEvent
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QProgressBar,
    QFileDialog, QMessageBox, QCheckBox, QGroupBox,
    QSizePolicy, QFrame, QApplication
)

from config.global_config import global_config
from modules.impl.video_downloader import VideoDownloaderModule
from modules.impl.video_downloader_config import VideoDownloaderConfig
from modules.impl.video_format_parser import VideoFormatInfo
from ui.components import ThemeColors
from utils import logger


class VideoDownloaderConfigWidget(QWidget):
    """视频下载配置界面"""

    # 支持的视频格式（默认选项 - 只保留最高质量MP4）
    VIDEO_FORMATS = [
        ("mp4", "默认"),
    ]

    # 支持的音频格式（默认选项 - 只保留最高音质）
    AUDIO_FORMATS = [
        ("m4a", "默认"),
    ]

    def __init__(self, parent: QWidget, module: VideoDownloaderModule):
        """初始化配置界面

        Args:
            parent: 父窗口
            module: 视频下载模块实例
        """
        super().__init__(parent)
        self._module = module
        # 存储解析后的格式
        self._parsed_video_formats: List[VideoFormatInfo] = []
        self._parsed_audio_formats: List[VideoFormatInfo] = []
        # 设置字体大小
        self.setFontSize(12)
        # 允许组件自由缩放
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._init_ui()
        self._load_config()
        self._connect_signals()

    def changeEvent(self, event: QEvent):
        """处理窗口变化事件"""
        if event.type() == QEvent.Polish:
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.updateGeometry()
        super().changeEvent(event)

    def showEvent(self, event):
        """每次显示时重新加载配置"""
        super().showEvent(event)
        self._load_config()

    def setFontSize(self, size: int):
        """设置字体大小"""
        from PyQt5.QtGui import QFont
        font = QFont("微软雅黑 UI", size)
        font.setBold(True)
        self.setFont(font)

    def _get_resolution_extra_spaces(self, resolution: str) -> str:
        """根据分辨率位数返回额外空格

        Args:
            resolution: 分辨率字符串，格式如 "1920×1080"

        Returns:
            额外空格字符串
        """
        if not resolution or '×' not in resolution:
            return ""
        try:
            parts = resolution.split('×')
            if len(parts) != 2:
                return ""
            width = parts[0].strip()
            # 三位数乘三位数 (如 640×360)，多加4个空格
            if len(width) == 3:
                return "    "
            # 四位数乘三位数 (如 1920×1080)，多加3个空格
            elif len(width) == 4:
                return "   "
        except:
            pass
        return ""

    # ===== 样式定义 =====
    CARD_STYLE = f"""
        QFrame {{
            background-color: {ThemeColors.LIGHT_CARD};
            border-radius: 8px;
            padding: 12px;
            border: 1px solid {ThemeColors.LIGHT_BORDER};
        }}
    """

    LABEL_TITLE_STYLE = f"""
        QLabel {{
            color: {ThemeColors.TEXT_COLOR};
            font-size: 13px;
            font-weight: bold;
        }}
    """

    LABEL_STYLE = f"""
        QLabel {{
            color: {ThemeColors.TEXT_SECONDARY};
            font-size: 12px;
        }}
    """

    # 解析按钮 - 紫色渐变
    PARSE_BUTTON_STYLE = f"""
        QPushButton {{
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            background: qlineargradient(x1:0, y1:0, x1:1, y1:0,
                stop:0 {ThemeColors.PRIMARY_PURPLE}, stop:1 {ThemeColors.PRIMARY_PURPLE_END});
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x1:1, y1:0,
                stop:0 {ThemeColors.PRIMARY_PURPLE}dd, stop:1 {ThemeColors.PRIMARY_PURPLE_END}dd);
        }}
        QPushButton:pressed {{
            background: qlineargradient(x1:0, y1:0, x1:1, y1:0,
                stop:0 {ThemeColors.PRIMARY_PURPLE}aa, stop:1 {ThemeColors.PRIMARY_PURPLE_END}aa);
        }}
        QPushButton:disabled {{
            background: #cccccc;
            color: #999999;
        }}
    """

    # 下载按钮 - 绿色渐变
    DOWNLOAD_BUTTON_STYLE = f"""
        QPushButton {{
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            background: qlineargradient(x1:0, y1:0, x1:1, y1:0,
                stop:0 {ThemeColors.PRIMARY_GREEN}, stop:1 {ThemeColors.PRIMARY_GREEN_END});
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x1:1, y1:0,
                stop:0 {ThemeColors.PRIMARY_GREEN}dd, stop:1 {ThemeColors.PRIMARY_GREEN_END}dd);
        }}
        QPushButton:pressed {{
            background: qlineargradient(x1:0, y1:0, x1:1, y1:0,
                stop:0 {ThemeColors.PRIMARY_GREEN}aa, stop:1 {ThemeColors.PRIMARY_GREEN_END}aa);
        }}
        QPushButton:disabled {{
            background: #cccccc;
            color: #999999;
        }}
    """

    # 辅助按钮 - 灰色
    SECONDARY_BUTTON_STYLE = f"""
        QPushButton {{
            color: {ThemeColors.TEXT_COLOR};
            font-weight: bold;
            border: 1px solid {ThemeColors.LIGHT_BORDER};
            border-radius: 4px;
            padding: 8px 16px;
            background-color: {ThemeColors.LIGHT_CARD};
        }}
        QPushButton:hover {{
            background-color: {ThemeColors.LIGHT_BG};
        }}
        QPushButton:pressed {{
            background-color: {ThemeColors.LIGHT_BORDER};
        }}
    """

    # 解析进度条 - 蓝色渐变
    PARSE_PROGRESS_STYLE = f"""
        QProgressBar {{
            border: none;
            border-radius: 6px;
            background-color: {ThemeColors.LIGHT_BORDER};
            text-align: left;
            padding-left: 0px;
        }}
        QProgressBar::chunk {{
            border-radius: 6px;
            background: qlineargradient(x1:0, y1:0, x1:1, y1:0,
                stop:0 {ThemeColors.PRIMARY_BLUE}, stop:1 {ThemeColors.PRIMARY_BLUE_END});
        }}
    """

    # 下载进度条 - 绿色渐变
    DOWNLOAD_PROGRESS_STYLE = f"""
        QProgressBar {{
            border: none;
            border-radius: 6px;
            background-color: {ThemeColors.LIGHT_BORDER};
            text-align: left;
            padding-left: 0px;
        }}
        QProgressBar::chunk {{
            border-radius: 6px;
            background: qlineargradient(x1:0, y1:0, x1:1, y1:0,
                stop:0 {ThemeColors.PRIMARY_GREEN}, stop:1 {ThemeColors.PRIMARY_GREEN_END});
        }}
    """

    def _create_card_frame(self) -> QFrame:
        """创建带背景的卡片 QFrame"""
        frame = QFrame()
        frame.setStyleSheet(self.CARD_STYLE)
        return frame

    def _init_ui(self):
        """初始化UI组件"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # ===== URL 输入区域 - 左右排列 =====
        url_frame = self._create_card_frame()
        url_frame_layout = QHBoxLayout(url_frame)
        url_frame_layout.setContentsMargins(8, 8, 8, 8)
        url_frame_layout.setSpacing(10)

        url_label = QLabel("视频地址:")
        url_label.setStyleSheet(self.LABEL_TITLE_STYLE)
        url_label.setMinimumWidth(70)
        url_frame_layout.addWidget(url_label)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("输入视频地址 (YouTube, B站等)")
        self.url_input.setMinimumHeight(38)
        url_frame_layout.addWidget(self.url_input, 1)

        self.paste_button = QPushButton("粘贴")
        self.paste_button.setMinimumWidth(70)
        self.paste_button.setStyleSheet(self.SECONDARY_BUTTON_STYLE)
        url_frame_layout.addWidget(self.paste_button)

        layout.addWidget(url_frame)

        # ===== 保存路径区域 - 左右排列 =====
        path_frame = self._create_card_frame()
        path_frame_layout = QHBoxLayout(path_frame)
        path_frame_layout.setContentsMargins(8, 8, 8, 8)
        path_frame_layout.setSpacing(10)

        path_label = QLabel("保存路径:")
        path_label.setStyleSheet(self.LABEL_TITLE_STYLE)
        path_label.setMinimumWidth(70)
        path_frame_layout.addWidget(path_label)

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("选择下载保存目录")
        self.path_input.setMinimumHeight(38)
        path_frame_layout.addWidget(self.path_input, 1)

        self.path_button = QPushButton("浏览")
        self.path_button.setMinimumWidth(70)
        self.path_button.setStyleSheet(self.SECONDARY_BUTTON_STYLE)
        path_frame_layout.addWidget(self.path_button)

        layout.addWidget(path_frame)

        # ===== 开始解析按钮 - 紫色渐变，纵向居中 =====
        self.parse_button = QPushButton("开始解析")
        self.parse_button.setMinimumHeight(44)
        self.parse_button.setStyleSheet(self.PARSE_BUTTON_STYLE)
        layout.addWidget(self.parse_button)

        # ===== 解析进度条 =====
        self.parse_progress = QProgressBar()
        self.parse_progress.setVisible(False)
        self.parse_progress.setMinimumHeight(32)
        self.parse_progress.setMaximumHeight(32)
        self.parse_progress.setTextVisible(True)
        self.parse_progress.setFormat("正在解析...")
        self.parse_progress.setStyleSheet(self.PARSE_PROGRESS_STYLE)
        # 使用不确定模式（动画效果）
        self.parse_progress.setMinimum(0)
        self.parse_progress.setMaximum(0)
        layout.addWidget(self.parse_progress)

        # ===== 分隔线 =====
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background-color: {ThemeColors.LIGHT_BORDER}; min-height: 1px;")
        layout.addWidget(separator)

        # ===== 格式选择区域 - 左右排列 =====
        format_frame = self._create_card_frame()
        format_frame_layout = QHBoxLayout(format_frame)
        format_frame_layout.setContentsMargins(12, 12, 12, 12)
        format_frame_layout.setSpacing(20)

        # 视频格式部分
        video_layout = QHBoxLayout()
        video_layout.setSpacing(8)
        video_label = QLabel("视频:")
        video_label.setStyleSheet(self.LABEL_TITLE_STYLE)
        video_layout.addWidget(video_label)
        self.format_combo = QComboBox()
        self.format_combo.setMinimumWidth(200)
        self.format_combo.setMinimumHeight(32)
        for value, text in self.VIDEO_FORMATS:
            self.format_combo.addItem(text, value)
        video_layout.addWidget(self.format_combo)
        video_layout.addStretch(1)
        format_frame_layout.addLayout(video_layout, 1)

        # 音频格式部分
        audio_layout = QHBoxLayout()
        audio_layout.setSpacing(8)
        audio_label = QLabel("音频:")
        audio_label.setStyleSheet(self.LABEL_TITLE_STYLE)
        audio_layout.addWidget(audio_label)
        self.audio_format_combo = QComboBox()
        self.audio_format_combo.setMinimumWidth(200)
        self.audio_format_combo.setMinimumHeight(32)
        for value, text in self.AUDIO_FORMATS:
            self.audio_format_combo.addItem(text, value)
        audio_layout.addWidget(self.audio_format_combo)
        audio_layout.addStretch(1)
        format_frame_layout.addLayout(audio_layout, 1)

        layout.addWidget(format_frame)

        # ===== 开始下载按钮 - 绿色渐变，纵向居中 =====
        self.download_button = QPushButton("开始下载")
        self.download_button.setMinimumHeight(44)
        self.download_button.setStyleSheet(self.DOWNLOAD_BUTTON_STYLE)
        layout.addWidget(self.download_button)

        # ===== 下载进度条 - 绿色渐变 =====
        self.download_progress = QProgressBar()
        self.download_progress.setVisible(False)
        self.download_progress.setMaximumHeight(20)
        self.download_progress.setTextVisible(True)
        self.download_progress.setFormat("下载进度: %p%")
        self.download_progress.setStyleSheet(self.DOWNLOAD_PROGRESS_STYLE)
        layout.addWidget(self.download_progress)

        # ===== 下载状态标签 =====
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-family: 'Microsoft YaHei UI', 'Segoe UI'; font-size: 12px; color: #6c757d;")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

        # 设置布局
        self.setLayout(layout)

    def _load_config(self):
        """加载保存的配置"""
        # 强制重新加载配置文件，确保获取最新值
        global_config._load()

        # 加载下载路径，使用新的 get_default_download_path 方法
        download_path = VideoDownloaderConfig.get_default_download_path()
        self.path_input.setText(download_path)

        # 打印日志便于调试
        logger.info(f"加载保存路径: {download_path}")

        # 加载视频格式
        video_format = global_config.get(
            VideoDownloaderConfig.CONFIG_KEY_VIDEO_FORMAT,
            VideoDownloaderConfig.DEFAULT_FORMAT
        )
        for i in range(self.format_combo.count()):
            if self.format_combo.itemData(i) == video_format:
                self.format_combo.setCurrentIndex(i)
                break

        # 加载音频格式
        audio_format = global_config.get(
            VideoDownloaderConfig.CONFIG_KEY_AUDIO_FORMAT,
            VideoDownloaderConfig.DEFAULT_AUDIO_FORMAT
        )
        for i in range(self.audio_format_combo.count()):
            if self.audio_format_combo.itemData(i) == audio_format:
                self.audio_format_combo.setCurrentIndex(i)
                break

    def _save_config(self):
        """保存配置到文件"""
        global_config.set(VideoDownloaderConfig.CONFIG_KEY_DOWNLOAD_PATH, self.path_input.text())
        global_config.set(VideoDownloaderConfig.CONFIG_KEY_VIDEO_FORMAT, self.format_combo.currentData())
        global_config.set(VideoDownloaderConfig.CONFIG_KEY_AUDIO_FORMAT, self.audio_format_combo.currentData())

    def _connect_signals(self):
        """连接信号槽"""
        self.parse_button.clicked.connect(self._on_parse_clicked)
        self.download_button.clicked.connect(self._on_download_clicked)
        self.path_button.clicked.connect(self._on_select_path)
        self.paste_button.clicked.connect(self._on_paste_clicked)

        # 连接模块信号
        self._module.parse_started.connect(self._on_parse_started)
        self._module.parse_finished.connect(self._on_parse_finished)
        self._module.progress_updated.connect(self._on_progress_updated)
        self._module.download_finished.connect(self._on_download_finished)

    @pyqtSlot()
    def _on_paste_clicked(self):
        """粘贴按钮点击处理"""
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.url_input.setText(text)

    @pyqtSlot()
    def _on_parse_clicked(self):
        """解析按钮点击处理"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "提示", "请输入视频地址")
            return

        # 保存配置
        self._save_config()

        # 执行解析
        result = self._module.parse_formats(url)

        if result.get("status") == "error":
            QMessageBox.critical(self, "错误", result.get("message", "未知错误"))
            return

        # 更新UI状态
        self.parse_button.setEnabled(False)
        self.parse_progress.setVisible(True)
        self.parse_progress.setValue(0)
        self.url_input.setEnabled(False)
        # 强制刷新 UI
        self.repaint()

    @pyqtSlot()
    def _on_parse_started(self):
        """解析开始"""
        logger.info("开始解析视频格式...")
        self.parse_progress.setVisible(True)
        # 强制刷新 UI
        self.repaint()

    @pyqtSlot(bool, str, list, list)
    def _on_parse_finished(self, success: bool, message: str, video_formats: list, audio_formats: list):
        """解析完成"""
        # 隐藏解析进度条
        self.parse_progress.setVisible(False)

        # 更新UI状态
        self.parse_button.setEnabled(True)
        self.url_input.setEnabled(True)

        if not success:
            pass
            QMessageBox.warning(self, "解析失败", message)
            return

        # 保存解析结果
        self._parsed_video_formats = video_formats
        self._parsed_audio_formats = audio_formats

        # 更新下拉框
        self._update_format_combos()

        QMessageBox.information(self, "解析成功",
            f"解析成功！\n视频格式: {len(video_formats)} 个\n音频格式: {len(audio_formats)} 个\n\n请选择需要的格式后点击下载")

    def _update_format_combos(self):
        """更新格式下拉框，添加解析到的格式"""
        # 添加分隔符和解析到的格式到视频格式下拉框
        current_video_value = self.format_combo.currentData()

        # 清除现有选项，保留默认选项
        self.format_combo.clear()
        for value, text in self.VIDEO_FORMATS:
            self.format_combo.addItem(text, value)

        # 添加解析到的格式
        if self._parsed_video_formats:
            self.format_combo.addItem("格式    分辨率         帧率     文件大小", "")
            for fmt in self._parsed_video_formats:
                # 根据分辨率位数添加额外空格
                extra_spaces = self._get_resolution_extra_spaces(fmt.resolution)
                # 显示格式: 分辨率 (格式) 文件大小
                display_text = f"{fmt.ext.upper():<6}{fmt.resolution:<12}{extra_spaces}{fmt.fps:<8}{fmt.filesize}"
                self.format_combo.addItem(display_text, fmt.format_id)

        # 恢复之前的选择
        for i in range(self.format_combo.count()):
            if self.format_combo.itemData(i) == current_video_value:
                self.format_combo.setCurrentIndex(i)
                break

        # 同样处理音频格式
        current_audio_index = self.audio_format_combo.currentIndex()
        current_audio_value = self.audio_format_combo.currentData()

        self.audio_format_combo.clear()
        for value, text in self.AUDIO_FORMATS:
            self.audio_format_combo.addItem(text, value)

        if self._parsed_audio_formats:
            self.audio_format_combo.addItem("格式    文件大小", "")
            for fmt in self._parsed_audio_formats:
                # 显示格式: 格式 文件大小
                display_text = f"{fmt.ext.lower():<3}    {fmt.filesize}"
                self.audio_format_combo.addItem(display_text, fmt.format_id)

        # 恢复之前的选择
        for i in range(self.audio_format_combo.count()):
            if self.audio_format_combo.itemData(i) == current_audio_value:
                self.audio_format_combo.setCurrentIndex(i)
                break

    @pyqtSlot()
    def _on_download_clicked(self):
        """下载按钮点击处理"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "提示", "请输入视频地址")
            return

        # 验证路径
        download_path = self.path_input.text().strip()
        if not download_path:
            QMessageBox.warning(self, "提示", "请选择保存路径")
            return

        # 保存配置
        self._save_config()

        # 获取用户选择的格式ID
        video_format_id = self.format_combo.currentData()
        audio_format_id = self.audio_format_combo.currentData()

        # 检查是否选择了解析到的格式
        if video_format_id and video_format_id in [fmt.format_id for fmt in self._parsed_video_formats]:
            logger.info(f"使用解析的视频格式: {video_format_id}")
        else:
            video_format_id = None

        if audio_format_id and audio_format_id in [fmt.format_id for fmt in self._parsed_audio_formats]:
            logger.info(f"使用解析的音频格式: {audio_format_id}")
        else:
            audio_format_id = None

        # 执行下载
        params = {
            "url": url,
            "video_format_id": video_format_id,
            "audio_format_id": audio_format_id
        }
        result = self._module.execute(params)

        if result.get("status") == "error":
            QMessageBox.critical(self, "错误", result.get("message", "未知错误"))
            return

        # 更新UI状态
        self.download_button.setEnabled(False)
        self.parse_button.setEnabled(False)
        self.url_input.setEnabled(False)

        # 显示下载进度条
        self.download_progress.setVisible(True)
        self.download_progress.setValue(0)
        # 强制刷新 UI
        self.repaint()

    @pyqtSlot()
    def _on_select_path(self):
        """选择保存路径"""
        directory = QFileDialog.getExistingDirectory(
            self, "选择保存目录", self.path_input.text()
        )
        if directory:
            self.path_input.setText(directory)
            global_config.set(VideoDownloaderConfig.CONFIG_KEY_DOWNLOAD_PATH, directory)

    @pyqtSlot(float, str)
    def _on_progress_updated(self, progress: float, message: str):
        """进度更新"""
        self._update_download_progress(progress, message)

    def _update_download_progress(self, progress: float, message: str):
        """更新下载进度显示"""
        if not self.download_progress.isVisible():
            self.download_progress.setVisible(True)
            # 强制刷新布局
            self.repaint()

        # 更新进度条值 (0-100)
        self.download_progress.setValue(int(progress * 100))

        # 强制刷新 UI
        self.repaint()

    @pyqtSlot(str, bool, str)
    def _on_download_finished(self, url: str, success: bool, message: str):
        """下载完成"""
        # 隐藏进度条
        self.download_progress.setVisible(False)
        self.download_progress.setValue(0)

        # 更新UI状态
        self.download_button.setEnabled(True)
        self.parse_button.setEnabled(True)
        self.url_input.setEnabled(True)

        if success:
            QMessageBox.information(self, "下载完成", "已下载完成")
        else:
            QMessageBox.warning(self, "下载失败", message)

