"""Path utility module for handling application data directories."""
import os
import shutil

from utils import logger


def get_app_data_dir() -> str:
    """Get the application data root directory.

    Uses Windows standard AppData/Roaming directory:
    C:\\Users\\用户名\\AppData\\Roaming\\Sumi-Kara

    Returns:
        The application data directory path, or empty string if not configured.
    """
    from config.global_config import global_config

    # 优先使用配置中保存的路径
    file_path = global_config.get("file_path", "")
    if file_path:
        return file_path

    # 首次运行：自动设置为 Windows AppData/Roaming 目录
    if global_config.get("is_first_run", True):
        # 获取 Windows APPDATA 路径
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            # 使用标准 Windows 目录结构
            default_path = os.path.join(appdata, "Sumi-Kara").replace("\\", "/")
        else:
            # 备用：使用用户文档目录
            user_documents = os.path.expanduser("~/Documents")
            default_path = os.path.join(user_documents, "Sumi-Kara").replace("\\", "/")

        # 创建目录
        if not os.path.exists(default_path):
            os.makedirs(default_path, exist_ok=True)

        # 清除首次运行标志
        global_config.set("is_first_run", False)
        # 保存路径到配置
        global_config.set("file_path", default_path)

        logger.info(f"首次运行，数据目录: {default_path}")
        return default_path

    return file_path


def migrate_to_new_path(new_path: str) -> bool:
    """迁移数据到新目录

    Args:
        new_path: 目标路径

    Returns:
        是否迁移成功
    """
    from config.global_config import global_config

    # 获取当前路径
    current_path = global_config.get("file_path", "")
    if not current_path:
        current_path = os.getcwd()

    # 如果新路径和当前路径相同，无需迁移
    if os.path.normpath(new_path) == os.path.normpath(current_path):
        return True

    # 创建目标目录
    if not os.path.exists(new_path):
        os.makedirs(new_path, exist_ok=True)

    # 迁移目录
    dirs_to_migrate = ["config", "tools", "logs", "downloads"]
    migrate_results = []

    for dir_name in dirs_to_migrate:
        source_dir = os.path.join(current_path, dir_name)
        target_dir = os.path.join(new_path, dir_name)

        if os.path.exists(source_dir) and os.path.isdir(source_dir):
            # 如果目标目录不存在，创建它
            if not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)

            # 迁移文件
            for item in os.listdir(source_dir):
                source_item = os.path.join(source_dir, item)
                target_item = os.path.join(target_dir, item)

                # 如果目标已存在，跳过
                if os.path.exists(target_item):
                    continue

                try:
                    shutil.move(source_item, target_item)
                    migrate_results.append(f"{dir_name}/{item}")
                except Exception as e:
                    logger.error(f"迁移失败: {source_item} - {e}")

    # 更新配置
    global_config.set("file_path", new_path.replace("\\", "/"))

    # 更新 ffmpeg_path 和 yt_dlp_path
    ffmpeg_path = global_config.get("ffmpeg_path", "")
    if ffmpeg_path and current_path in ffmpeg_path:
        global_config.set("ffmpeg_path", ffmpeg_path.replace(current_path, new_path).replace("\\", "/"))

    yt_dlp_path = global_config.get("yt_dlp_path", "")
    if yt_dlp_path and current_path in yt_dlp_path:
        global_config.set("yt_dlp_path", yt_dlp_path.replace(current_path, new_path).replace("\\", "/"))

    logger.info(f"迁移完成，共迁移 {len(migrate_results)} 个文件")
    return True


def get_log_dir() -> str:
    """Get the log directory.

    Returns:
        The log directory path ({app_data}/logs).
    """
    app_data = get_app_data_dir()
    if not app_data:
        # Fallback to ./logs if not configured (for development)
        return "./logs"
    return os.path.join(app_data, "logs").replace("\\", "/")


def get_config_dir() -> str:
    """Get the config directory.

    Returns:
        The config directory path ({app_data}/config).
    """
    app_data = get_app_data_dir()
    if not app_data:
        # Fallback to ./config if not configured (for development)
        return "./config"
    return os.path.join(app_data, "config").replace("\\", "/")


def get_download_dir() -> str:
    """Get the download directory.

    Returns:
        The download directory path ({app_data}/downloads).
    """
    app_data = get_app_data_dir()
    if not app_data:
        # Fallback to ./downloads if not configured (for development)
        return "./downloads"
    return os.path.join(app_data, "downloads").replace("\\", "/")


def is_first_run() -> bool:
    """Check if this is the first run (file_path not configured).

    Returns:
        True if first run, False otherwise.
    """
    from config.global_config import global_config
    file_path = global_config.get("file_path", "")
    return not file_path or file_path.strip() == ""


def get_app_dir() -> str:
    """获取主程序目录

    返回: %APPDATA%/Sumi-Kara
    """
    appdata = os.environ.get("APPDATA", "")
    if appdata:
        return os.path.join(appdata, "Sumi-Kara").replace("\\", "/")
    # 备用
    user_documents = os.path.expanduser("~/Documents")
    return os.path.join(user_documents, "Sumi-Kara").replace("\\", "/")


def get_tools_dir() -> str:
    """获取工具目录

    返回: {app_dir}/tools
    """
    return os.path.join(get_app_dir(), "tools").replace("\\", "/")


def get_bundled_tools_dir() -> str:
    """获取打包的工具目录（开发环境和打包后都可用）

    返回: resources 目录路径
    """
    import sys
    if getattr(sys, 'frozen', False):
        # 打包后：sys._MEIPASS 是临时解压目录
        base_path = sys._MEIPASS
    else:
        # 开发环境：项目根目录
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, "resources").replace("\\", "/")
