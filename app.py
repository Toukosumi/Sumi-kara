"""Application setup and configuration."""
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor, QFont


def create_app() -> QApplication:
    """Create and configure QApplication.

    Returns:
        Configured QApplication instance
    """
    # 必须在创建 QApplication 之前设置高DPI属性
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    # 启用高DPI图标支持
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, False)

    app = QApplication(sys.argv)

    # 设置全局字体
    app.setFont(QFont("微软雅黑 UI", 10))

    app.setApplicationName("Sumi-Kara")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SumiKara")

    # 使用 Fusion 风格 + 浅色主题
    app.setStyle("Fusion")

    # 设置浅色主题调色板
    light_palette = QPalette()
    light_palette.setColor(QPalette.Window, QColor(240, 240, 240))
    light_palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
    light_palette.setColor(QPalette.Base, QColor(255, 255, 255))
    light_palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
    light_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    light_palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
    light_palette.setColor(QPalette.Text, QColor(0, 0, 0))
    light_palette.setColor(QPalette.Button, QColor(240, 240, 240))
    light_palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
    light_palette.setColor(QPalette.BrightText, QColor(0, 0, 0))
    light_palette.setColor(QPalette.Link, QColor(0, 0, 255))
    light_palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
    light_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(light_palette)

    # 应用全局浅色样式表
    app.setStyleSheet("""
        /* 全局样式 */
        QToolTip {
            color: #000000;
            background-color: #ffffe0;
            border: 1px solid #ccc;
            padding: 4px;
            border-radius: 4px;
        }

        /* 菜单样式 */
        QMenuBar {
            background-color: #f0f0f0;
            color: #000000;
        }
        QMenuBar::item:selected {
            background-color: #d0d0d0;
        }
        QMenu {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #ccc;
        }
        QMenu::item:selected {
            background-color: #d0d0d0;
        }

        /* 滚动条样式 */
        QScrollBar:vertical {
            background: #f0f0f0;
            width: 12px;
            border: none;
        }
        QScrollBar::handle:vertical {
            background: #c0c0c0;
            min-height: 20px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical:hover {
            background: #a0a0a0;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }

        /* 输入框样式 */
        QLineEdit {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 6px 10px;
            selection-background-color: #0078d4;
        }
        QLineEdit:focus {
            border: 1px solid #0078d4;
        }
        QLineEdit:disabled {
            background-color: #f5f5f5;
            color: #999999;
        }

        /* 按钮样式 */
        QPushButton {
            background-color: #e0e0e0;
            color: #000000;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 8px 16px;
        }
        QPushButton:hover {
            background-color: #d0d0d0;
        }
        QPushButton:pressed {
            background-color: #c0c0c0;
        }
        QPushButton:disabled {
            background-color: #f0f0f0;
            color: #999999;
        }

        /* 下拉框样式 */
        QComboBox {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 6px 10px;
        }
        QComboBox:focus {
            border: 1px solid #0078d4;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid #000000;
            margin-right: 8px;
        }
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            color: #000000;
            selection-background-color: #0078d4;
            border: 1px solid #ccc;
        }

        /* 进度条样式 */
        QProgressBar {
            background-color: #e0e0e0;
            border: 1px solid #ccc;
            border-radius: 6px;
            text-align: left;
            padding-left: 4px;
        }
        QProgressBar::chunk {
            border-radius: 5px;
        }

        /* 标签样式 */
        QLabel {
            color: #000000;
        }

        /* 复选框样式 */
        QCheckBox {
            color: #000000;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border-radius: 3px;
            border: 1px solid #ccc;
            background-color: #ffffff;
        }
        QCheckBox::indicator:checked {
            background-color: #0078d4;
            border: 1px solid #0078d4;
        }

        /* 单选按钮样式 */
        QRadioButton {
            color: #000000;
        }
        QRadioButton::indicator {
            width: 16px;
            height: 16px;
            border-radius: 8px;
            border: 1px solid #ccc;
            background-color: #ffffff;
        }
        QRadioButton::indicator:checked {
            background-color: #0078d4;
            border: 1px solid #0078d4;
        }

        /* 消息框样式 */
        QMessageBox {
            background-color: #ffffff;
        }
        QMessageBox QLabel {
            color: #000000;
        }

        /* 文件对话框样式 */
        QFileDialog {
            background-color: #ffffff;
        }
    """)

    # 确保应用正确处理高DPI缩放变化
    app.setAttribute(Qt.AA_DisableHighDpiScaling, False)

    return app
