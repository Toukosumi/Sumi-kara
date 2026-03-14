"""Sumi-Kara main entry point."""
import sys

from app import create_app
from modules.impl.lyric_downloader import LyricDownloaderModule
from modules.impl.lyric_merger import LyricMergerModule
from modules.impl.video_downloader import VideoDownloaderModule
from modules.impl.settings import SettingsModule
from modules.manager import module_manager
from ui.main_window import MainWindow
from utils import logger


def register_modules():
    """Register all available modules."""
    modules = [
        VideoDownloaderModule(),
        LyricDownloaderModule(),
        LyricMergerModule(),
        SettingsModule(),
    ]

    for module in modules:
        module_manager.register(module)

    logger.info(f"Registered {len(modules)} modules")


def main():
    """Main entry point."""
    logger.info("=" * 50)
    logger.info("Sumi-Kara starting...")
    logger.info("=" * 50)

    # Register modules
    register_modules()

    # Create application (必须在任何 Qt widget 之前创建)
    app = create_app()

    # Create and show main window
    window = MainWindow()

    # 设置窗口居中显示
    from PyQt5.QtWidgets import QDesktopWidget
    try:
        screen = QDesktopWidget().screenGeometry()
        window_geometry = window.geometry()
        x = (screen.width() - window_geometry.width()) // 2
        y = (screen.height() - window_geometry.height()) // 2
        window.move(x, y)
    except Exception as e:
        logger.warning(f"窗口居中设置失败: {e}")

    window.show()
    window.raise_()  # 提升窗口到前台
    window.activateWindow()  # 激活窗口

    logger.info("Main window displayed")

    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
