"""Main window with TabBar for module switching."""
from typing import Dict

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import (
    QLabel,
    QMainWindow,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from modules.manager import module_manager
from utils import logger


class MainWindow(QMainWindow):
    """Main window with tab-based module switching."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sumi-Kara 多功能工具")
        # 默认窗口大小缩小一点
        self.resize(700, 540)
        # 最小窗口大小
        self.setMinimumSize(600, 400)
        # 允许窗口自由缩放
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 允许调整窗口大小
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint)
        self._module_widgets: Dict[str, QWidget] = {}
        self._init_ui()

    def changeEvent(self, event: QEvent):
        """处理窗口变化事件，包括屏幕分辨率变化"""
        # 处理窗口状态变化（最小化、最大化等）
        if event.type() == QEvent.WindowStateChange:
            if self.isMinimized():
                # 最小化时不隐藏，只是确保能恢复
                pass
        super().changeEvent(event)

    def showEvent(self, event):
        """处理窗口显示事件，确保最小化后能正确恢复"""
        super().showEvent(event)
        # 检查窗口是否应该显示但被隐藏了
        if self.windowState() & Qt.WindowMinimized:
            # 从最小化状态恢复
            self.restoreWindowState()
        # 激活窗口并提升到前台
        self.activateWindow()
        self.raise_()

    def restoreWindowState(self):
        """恢复窗口状态"""
        # 清除最小化状态
        if self.windowState() & Qt.WindowMinimized:
            self.setWindowState(self.windowState() & ~Qt.WindowMinimized)
        # 确保窗口可见
        self.show()
        self.activateWindow()
        self.raise_()

    def setVisible(self, visible: bool):
        """设置窗口可见性"""
        super().setVisible(visible)

    def closeEvent(self, event):
        """关闭事件"""
        # 保存窗口状态
        event.accept()

    def _init_ui(self):
        """Initialize UI components."""
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tab widget for module switching
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)

        # 设置 Tab 蓝色渐变样式
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                background-color: #f5f5f5;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                color: #333333;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x1:1, y1:0,
                    stop:0 #1976d2, stop:1 #42a5f5);
                color: #ffffff;
            }
            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1:0, y1:0, x1:1, y1:0,
                    stop:0 #1565c0, stop:1 #2196f3);
                color: #ffffff;
            }
        """)

        # 设置 Tab 字体样式
        from PyQt5.QtGui import QFont
        tab_font = QFont("微软雅黑 UI", 13)
        tab_font.setBold(True)
        self.tab_widget.setFont(tab_font)

        # Load modules
        self._load_modules()

        layout.addWidget(self.tab_widget)

    def _load_modules(self):
        """Load all registered modules into tabs."""
        modules = module_manager.get_all_modules()
        logger.info(f"Loading {len(modules)} modules into UI")

        for module in modules:
            name = module.get_name()
            # Create placeholder widget for each module
            widget = self._create_module_widget(module)
            self._module_widgets[name] = widget
            self.tab_widget.addTab(widget, name)
            logger.debug(f"Added tab: {name}")

    def _create_module_widget(self, module) -> QWidget:
        """Create widget for a module.

        Args:
            module: Module instance

        Returns:
            Widget for the module
        """
        # 优先使用模块提供的配置widget
        config_widget = module.get_config_widget(self)
        if config_widget is not None:
            return config_widget

        # 如果模块没有提供widget，使用默认占位符
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Module title
        title = QLabel(f"<h2>{module.get_name()}</h2>")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Module description
        desc = QLabel(f"<p>{module.get_description()}</p>")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: gray;")
        layout.addWidget(desc)

        # Placeholder message
        placeholder = QLabel("<h3>模块预留，尚未实现</h3>")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: #888; padding: 50px;")
        layout.addWidget(placeholder)

        # Add stretch to center content
        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def get_tab_widget(self) -> QTabWidget:
        """Get the tab widget.

        Returns:
            QTabWidget instance
        """
        return self.tab_widget
