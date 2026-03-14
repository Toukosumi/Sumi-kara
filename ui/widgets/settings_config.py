"""Settings configuration widget."""
import os

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QScrollArea, QWidget, QGroupBox, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from ui.components import (
    TitleLabel, ContentLabel, StyledComboBox, PrimaryButton,
    StyledLineEdit, SecondaryButton, SuccessButton, InfoButton, FormRow
)
from config.global_config import global_config
from utils import logger
from utils.tool_manager import ToolManager


class SettingsConfigWidget(QWidget):
    """Settings configuration widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        # 页面加载时自动检测工具状态（后台执行）
        self._start_auto_detect()

    def _start_auto_detect(self):
        """启动自动检测（使用快速检测模式）"""
        # 显示检测中状态
        self.ytdlp_status_label.setText("检测中...")
        self.ytdlp_status_label.setStyleSheet("color: #888; font-weight: bold;")
        self.ffmpeg_status_label.setText("检测中...")
        self.ffmpeg_status_label.setStyleSheet("color: #888; font-weight: bold;")

        # 使用快速检测（只检测打包资源和内置目录）
        self._auto_ytdlp_worker = YtDlpFastDetectWorker()
        self._auto_ytdlp_worker.finished.connect(self._on_auto_yt_dlp_detected)
        self._auto_ytdlp_worker.start()

        self._auto_ffmpeg_worker = FFmpegFastDetectWorker()
        self._auto_ffmpeg_worker.finished.connect(self._on_auto_ffmpeg_detected)
        self._auto_ffmpeg_worker.start()

    def _on_auto_yt_dlp_detected(self, available, path, version):
        """自动检测 yt-dlp 完成回调"""
        if available:
            self.ytdlp_status_label.setText(f"可用 ({version})")
            self.ytdlp_status_label.setStyleSheet("color: #11998e; font-weight: bold;")

    def _on_auto_ffmpeg_detected(self, available, path, version):
        """自动检测 ffmpeg 完成回调"""
        if available:
            self.ffmpeg_status_label.setText("可用")
            self.ffmpeg_status_label.setStyleSheet("color: #11998e; font-weight: bold;")

    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = TitleLabel("应用程序设置")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Scroll area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)

        # ===== 文件路径设置 =====
        file_path_group = self._create_file_path_settings()
        scroll_layout.addWidget(file_path_group)

        # ===== 常规设置 =====
        general_group = self._create_general_settings()
        scroll_layout.addWidget(general_group)

        scroll_layout.addStretch()

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

    def _create_file_path_settings(self) -> QGroupBox:
        """Create file path settings group."""
        group = QGroupBox("文件路径")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QVBoxLayout(group)
        layout.setSpacing(12)

        # File path input - 使用 FormRow 组件
        path_row = FormRow("主目录:", "📁", label_width=80)
        self.file_path_input = StyledLineEdit()
        self.file_path_input.setPlaceholderText("请选择数据存放主目录")
        # 显示当前配置的目录，如果是空字符串则使用默认值
        from utils.path_utils import get_app_data_dir
        default_path = get_app_data_dir()
        current_path = global_config.get("file_path", "") or default_path
        self.file_path_input.setText(current_path)

        # 将"浏览"按钮改为"迁移"按钮
        migrate_btn = SecondaryButton("迁移")
        migrate_btn.clicked.connect(self._migrate_file_path)

        path_row.set_control(self.file_path_input)
        path_row.add_button(migrate_btn)
        layout.addWidget(path_row)

        # Hint text
        hint_label = ContentLabel("提示：日志、配置、下载等文件都将存放在此目录下，建议选择英文目录路径")
        hint_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(hint_label)

        return group

    def _migrate_file_path(self):
        """迁移数据到新目录"""
        # 1. 弹出目录选择框
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择新目录",
            self.file_path_input.text() or "D:/Sumi-Kara",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        if not directory:
            return

        # 转换为正斜杠
        new_path = directory.replace("\\", "/")

        # 2. 获取当前路径
        current_path = global_config.get("file_path", "")

        # 如果新路径和当前路径相同，无需迁移
        if os.path.normpath(new_path) == os.path.normpath(current_path):
            QMessageBox.information(self, "提示", "目标路径与当前路径相同，无需迁移。")
            return

        # 3. 确认迁移
        reply = QMessageBox.question(
            self,
            "确认迁移",
            f"是否将数据从当前目录迁移到:\n{new_path}?\n\n注意：原目录中的文件将移动到新目录。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # 4. 执行迁移
        from utils.path_utils import migrate_to_new_path
        success = migrate_to_new_path(new_path)

        if success:
            # 5. 更新界面显示
            self.file_path_input.setText(new_path)

            # 更新 ffmpeg 和 yt-dlp 路径显示
            self.ytdlp_path_input.setText(global_config.get("yt_dlp_path", ""))
            self.ffmpeg_path_input.setText(global_config.get("ffmpeg_path", ""))

            QMessageBox.information(self, "迁移完成", f"数据已成功迁移到:\n{new_path}")
        else:
            QMessageBox.warning(self, "迁移失败", "数据迁移过程中出现错误，请检查日志。")

    def _create_general_settings(self) -> QGroupBox:
        """Create general settings group."""
        group = QGroupBox("常规设置")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QVBoxLayout(group)
        layout.setSpacing(12)

        # ===== yt-dlp 检测行 =====
        ytdlp_row = FormRow("yt-dlp:", "🔧", label_width=80)

        # 路径输入框
        self.ytdlp_path_input = StyledLineEdit()
        self.ytdlp_path_input.setPlaceholderText("点击检测或手动输入路径")
        self.ytdlp_path_input.setText(global_config.get("yt_dlp_path", ""))

        # 检测按钮
        self.ytdlp_detect_btn = InfoButton("检测")
        self.ytdlp_detect_btn.clicked.connect(self._detect_yt_dlp)

        # 更新按钮
        self.ytdlp_update_btn = SuccessButton("更新")
        self.ytdlp_update_btn.clicked.connect(self._update_yt_dlp)

        # 状态标签
        self.ytdlp_status_label = ContentLabel("未检测")
        self.ytdlp_status_label.setStyleSheet("color: #888; font-weight: bold;")

        ytdlp_row.set_control(self.ytdlp_path_input)
        ytdlp_row.add_button(self.ytdlp_detect_btn)
        ytdlp_row.add_button(self.ytdlp_update_btn)
        ytdlp_row.add_button(self.ytdlp_status_label)
        layout.addWidget(ytdlp_row)

        # ===== FFmpeg 检测行 =====
        ffmpeg_row = FormRow("FFmpeg:", "🎬", label_width=80)

        # 路径输入框
        self.ffmpeg_path_input = StyledLineEdit()
        self.ffmpeg_path_input.setPlaceholderText("点击检测或手动输入路径")
        self.ffmpeg_path_input.setText(global_config.get("ffmpeg_path", ""))

        # 检测按钮
        self.ffmpeg_detect_btn = InfoButton("检测")
        self.ffmpeg_detect_btn.clicked.connect(self._detect_ffmpeg)

        # 下载按钮
        self.ffmpeg_download_btn = SuccessButton("下载")
        self.ffmpeg_download_btn.clicked.connect(self._download_ffmpeg)

        # 状态标签
        self.ffmpeg_status_label = ContentLabel("未检测")
        self.ffmpeg_status_label.setStyleSheet("color: #888; font-weight: bold;")

        ffmpeg_row.set_control(self.ffmpeg_path_input)
        ffmpeg_row.add_button(self.ffmpeg_detect_btn)
        ffmpeg_row.add_button(self.ffmpeg_download_btn)
        ffmpeg_row.add_button(self.ffmpeg_status_label)
        layout.addWidget(ffmpeg_row)

        # ===== 自动检查更新 =====
        update_row = FormRow("自动检查更新:", "🔄", label_width=130)
        self.auto_update_combo = StyledComboBox()
        self.auto_update_combo.setFixedWidth(80)  # 加宽以适应
        self.auto_update_combo.addItems(["开启", "关闭"])
        auto_update = global_config.get("auto_check_update", True)
        self.auto_update_combo.setCurrentIndex(0 if auto_update else 1)

        update_row.set_control(self.auto_update_combo, stretch=0)
        layout.addWidget(update_row)

        # Save button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        save_btn = PrimaryButton("保存设置")
        save_btn.clicked.connect(self._save_settings)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        return group

    def _detect_yt_dlp(self):
        """检测 yt-dlp 是否可用"""
        # 禁用按钮，显示加载状态
        self.ytdlp_detect_btn.setEnabled(False)
        self.ytdlp_status_label.setText("检测中...")
        self.ytdlp_status_label.setStyleSheet("color: #888; font-weight: bold;")

        # 启动后台线程
        custom_path = self.ytdlp_path_input.text().strip()
        self._detect_worker = YtDlpDetectWorker(custom_path)
        self._detect_worker.finished.connect(self._on_yt_dlp_detect_finished)
        self._detect_worker.error.connect(self._on_yt_dlp_detect_error)
        self._detect_worker.start()

    def _on_yt_dlp_detect_finished(self, available, path, version):
        """yt-dlp 检测完成回调"""
        self.ytdlp_detect_btn.setEnabled(True)

        if available:
            self.ytdlp_path_input.setText(path)
            self.ytdlp_status_label.setText(f"可用 ({version})")
            self.ytdlp_status_label.setStyleSheet("color: #11998e; font-weight: bold;")
            logger.info(f"yt-dlp 检测成功: {path} ({version})")

            # 自动保存到配置
            global_config.set("yt_dlp_path", path)
        else:
            self.ytdlp_status_label.setText("不可用，点击更新下载")
            self.ytdlp_status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            logger.warning("yt-dlp 未检测到")

    def _on_yt_dlp_detect_error(self, error_msg):
        """yt-dlp 检测错误回调"""
        self.ytdlp_detect_btn.setEnabled(True)
        self.ytdlp_status_label.setText("检测失败")
        self.ytdlp_status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
        QMessageBox.warning(self, "错误", f"检测 yt-dlp 时出错: {error_msg}")

    def _detect_ffmpeg(self):
        """检测 ffmpeg 是否可用"""
        # 禁用按钮，显示加载状态
        self.ffmpeg_detect_btn.setEnabled(False)
        self.ffmpeg_status_label.setText("检测中...")
        self.ffmpeg_status_label.setStyleSheet("color: #888; font-weight: bold;")

        # 启动后台线程
        custom_path = self.ffmpeg_path_input.text().strip()
        self._detect_worker = FFmpegDetectWorker(custom_path)
        self._detect_worker.finished.connect(self._on_ffmpeg_detect_finished)
        self._detect_worker.error.connect(self._on_ffmpeg_detect_error)
        self._detect_worker.start()

    def _on_ffmpeg_detect_finished(self, available, path, version):
        """ffmpeg 检测完成回调"""
        self.ffmpeg_detect_btn.setEnabled(True)

        if available:
            self.ffmpeg_path_input.setText(path)
            self.ffmpeg_status_label.setText(f"可用")
            self.ffmpeg_status_label.setStyleSheet("color: #11998e; font-weight: bold;")
            logger.info(f"ffmpeg 检测成功: {path}")

            # 自动保存到配置
            global_config.set("ffmpeg_path", path)
        else:
            self.ffmpeg_status_label.setText("不可用，点击下载")
            self.ffmpeg_status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            logger.warning("ffmpeg 未检测到")

    def _on_ffmpeg_detect_error(self, error_msg):
        """ffmpeg 检测错误回调"""
        self.ffmpeg_detect_btn.setEnabled(True)
        self.ffmpeg_status_label.setText("检测失败")
        self.ffmpeg_status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
        QMessageBox.warning(self, "错误", f"检测 ffmpeg 时出错: {error_msg}")

    def _update_yt_dlp(self):
        """更新 yt-dlp 到最新版本"""
        target_path = self.ytdlp_path_input.text().strip()
        if not target_path:
            # 使用默认路径
            ToolManager._ensure_tools_dir()
            target_path = ToolManager.get_yt_dlp_path()

        # 禁用按钮防止重复点击
        self.ytdlp_update_btn.setEnabled(False)
        self.ytdlp_detect_btn.setEnabled(False)
        self.ytdlp_status_label.setText("更新中...")

        # 创建工作线程
        self._update_worker = YtDlpUpdateWorker(target_path)
        self._update_worker.finished.connect(self._on_yt_dlp_update_finished)
        self._update_worker.error.connect(self._on_yt_dlp_update_error)
        self._update_worker.start()

    def _on_yt_dlp_update_finished(self, success, message):
        """yt-dlp 更新完成回调"""
        self.ytdlp_update_btn.setEnabled(True)
        self.ytdlp_detect_btn.setEnabled(True)

        if success:
            QMessageBox.information(self, "提示", message)
            # 重新检测
            self._detect_yt_dlp()
        else:
            self.ytdlp_status_label.setText("更新失败")
            self.ytdlp_status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            QMessageBox.warning(self, "错误", message)

    def _on_yt_dlp_update_error(self, error_msg):
        """yt-dlp 更新错误回调"""
        self.ytdlp_update_btn.setEnabled(True)
        self.ytdlp_detect_btn.setEnabled(True)
        self.ytdlp_status_label.setText("更新失败")
        self.ytdlp_status_label.setStyleSheet("color: #dc3545; font-weight bold;")
        QMessageBox.warning(self, "错误", error_msg)

    def _download_ffmpeg(self):
        """下载 ffmpeg"""
        from PyQt5.QtWidgets import QProgressDialog

        progress = QProgressDialog("正在下载 ffmpeg...", "取消", 0, 100, self)
        progress.setWindowTitle("下载")
        progress.setWindowModality(Qt.WindowModal)
        progress.setAutoClose(True)

        def update_progress(downloaded, total):
            if total > 0:
                percent = int(downloaded * 100 / total)
                progress.setValue(percent)

        progress.show()

        # 下载 ffmpeg
        success = ToolManager.download_ffmpeg(progress_callback=update_progress)

        progress.close()

        if success:
            QMessageBox.information(self, "提示", "ffmpeg 下载成功！")
            self._detect_ffmpeg()
        else:
            QMessageBox.warning(self, "错误", "ffmpeg 下载失败，请检查网络连接")

    def _save_settings(self):
        """Save settings to config."""
        try:
            # Update config
            global_config.set("file_path", self.file_path_input.text())
            global_config.set("auto_check_update", self.auto_update_combo.currentIndex() == 0)

            # 保存工具路径
            ytdlp_path = self.ytdlp_path_input.text().strip()
            ffmpeg_path = self.ffmpeg_path_input.text().strip()

            # 检测路径是否有效，如果无效则不保存
            if ytdlp_path and ToolManager._check_yt_dlp_executable(ytdlp_path):
                global_config.set("yt_dlp_path", ytdlp_path)
            else:
                global_config.set("yt_dlp_path", "")

            if ffmpeg_path and ToolManager._check_ffmpeg_executable(ffmpeg_path):
                global_config.set("ffmpeg_path", ffmpeg_path)
            else:
                global_config.set("ffmpeg_path", "")

            logger.info("设置已保存")
            self._show_save_success()
        except Exception as e:
            logger.error(f"保存设置失败: {e}")

    def _show_save_success(self):
        """Show save success message."""
        QMessageBox.information(self, "提示", "设置已保存！")


class YtDlpUpdateWorker(QThread):
    """yt-dlp 更新工作线程"""
    finished = pyqtSignal(bool, str)
    error = pyqtSignal(str)

    def __init__(self, target_path):
        super().__init__()
        self.target_path = target_path

    def run(self):
        try:
            success = ToolManager.update_yt_dlp(
                self.target_path,
                progress_callback=None
            )
            if success:
                self.finished.emit(True, "yt-dlp 更新成功！")
            else:
                self.finished.emit(False, "yt-dlp 更新失败")
        except Exception as e:
            self.error.emit(str(e))


class YtDlpDetectWorker(QThread):
    """yt-dlp 检测工作线程"""
    finished = pyqtSignal(bool, str, str)  # available, path, version
    error = pyqtSignal(str)

    def __init__(self, custom_path):
        super().__init__()
        self.custom_path = custom_path

    def run(self):
        try:
            available, path, version = ToolManager.detect_yt_dlp(self.custom_path)
            self.finished.emit(available, path, version)
        except Exception as e:
            self.error.emit(str(e))


class FFmpegDetectWorker(QThread):
    """ffmpeg 检测工作线程"""
    finished = pyqtSignal(bool, str, str)  # available, path, version
    error = pyqtSignal(str)

    def __init__(self, custom_path):
        super().__init__()
        self.custom_path = custom_path

    def run(self):
        try:
            available, path, version = ToolManager.detect_ffmpeg(self.custom_path)
            self.finished.emit(available, path, version)
        except Exception as e:
            self.error.emit(str(e))


class YtDlpFastDetectWorker(QThread):
    """yt-dlp 快速检测工作线程（只检测打包资源和内置目录）"""
    finished = pyqtSignal(bool, str, str)  # available, path, version

    def run(self):
        try:
            available, path, version = ToolManager.detect_yt_dlp_fast()
            self.finished.emit(available, path, version)
        except Exception:
            self.finished.emit(False, "", "检测失败")


class FFmpegFastDetectWorker(QThread):
    """ffmpeg 快速检测工作线程（只检测打包资源和内置目录）"""
    finished = pyqtSignal(bool, str, str)  # available, path, version

    def run(self):
        try:
            available, path, version = ToolManager.detect_ffmpeg_fast()
            self.finished.emit(available, path, version)
        except Exception:
            self.finished.emit(False, "", "检测失败")
