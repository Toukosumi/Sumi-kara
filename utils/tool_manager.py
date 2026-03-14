"""Tool manager module - 管理 ffmpeg 和 yt-dlp 工具的下载和路径."""
import os
import shutil
import urllib.request
import zipfile
import subprocess
import socket
import sys

from utils import logger

# Windows 下隐藏子进程窗口
if sys.platform == "win32":
    CREATE_NO_WINDOW = 0x08000000
else:
    CREATE_NO_WINDOW = 0


# 网络超时和重试配置
DOWNLOAD_TIMEOUT = 60  # 超时时间（秒）
MAX_RETRIES = 3  # 最大重试次数


class ToolManager:
    """工具管理器 - 管理 ffmpeg 和 yt-dlp"""

    # 工具存放目录名称
    TOOLS_DIR = "tools"
    YT_DLP_DIR = "yt-dlp"
    FFMPEG_DIR = "ffmpeg"

    # yt-dlp 下载地址
    YT_DLP_URL = "https://github.com/yt-dlp/yt-dlp/releases/download/2023.12.30/yt-dlp.exe"

    # ffmpeg 下载地址 (GitHub releases)
    FFMPEG_URL = "https://github.com/GyanD/codexffmpeg/releases/download/6.1/ffmpeg-6.1-essentials.zip"

    @classmethod
    def get_tools_dir(cls) -> str:
        """获取工具根目录

        Returns:
            工具根目录路径
        """
        from utils.path_utils import get_app_data_dir
        app_data = get_app_data_dir()
        if not app_data:
            # 开发环境下使用项目根目录下的 tools
            return "./tools"
        return os.path.join(app_data, cls.TOOLS_DIR).replace("\\", "/")

    @classmethod
    def get_yt_dlp_dir(cls) -> str:
        """获取 yt-dlp 工具目录

        Returns:
            yt-dlp 目录路径
        """
        return os.path.join(cls.get_tools_dir(), cls.YT_DLP_DIR).replace("\\", "/")

    @classmethod
    def get_ffmpeg_dir(cls) -> str:
        """获取 ffmpeg 工具目录

        Returns:
            ffmpeg 目录路径
        """
        return os.path.join(cls.get_tools_dir(), cls.FFMPEG_DIR).replace("\\", "/")

    @classmethod
    def get_bundled_tools_dir(cls) -> str:
        """获取打包的工具目录（resources 目录）

        Returns:
            打包的工具目录路径
        """
        import sys
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, "resources").replace("\\", "/")

    @classmethod
    def get_bundled_ffmpeg_dir(cls) -> str:
        """获取打包的 ffmpeg 目录（开发环境）

        Returns:
            打包的 ffmpeg 目录路径
        """
        return os.path.join(cls.get_bundled_tools_dir(), "ffmpeg").replace("\\", "/")

    @classmethod
    def get_bundled_yt_dlp_path(cls) -> str:
        """获取打包的 yt-dlp 路径

        Returns:
            打包的 yt-dlp.exe 路径
        """
        bundled_dir = cls.get_bundled_tools_dir()
        yt_dlp_path = os.path.join(bundled_dir, "yt-dlp.exe").replace("\\", "/")
        if os.path.isfile(yt_dlp_path):
            return yt_dlp_path
        return ""

    @classmethod
    def _copy_bundled_ffmpeg(cls) -> bool:
        """复制打包的 ffmpeg 到运行时目录

        Returns:
            是否复制成功
        """
        bundled_dir = cls.get_bundled_ffmpeg_dir()
        target_dir = cls.get_ffmpeg_dir()

        # 检查打包资源是否存在
        if not os.path.isdir(bundled_dir):
            logger.warning(f"打包的 ffmpeg 目录不存在: {bundled_dir}")
            return False

        ffmpeg_exe = os.path.join(bundled_dir, "ffmpeg.exe")
        if not os.path.isfile(ffmpeg_exe):
            logger.warning(f"打包的 ffmpeg.exe 不存在: {ffmpeg_exe}")
            return False

        # 复制所有文件
        os.makedirs(target_dir, exist_ok=True)
        for file in os.listdir(bundled_dir):
            src = os.path.join(bundled_dir, file)
            dst = os.path.join(target_dir, file)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
                logger.info(f"已复制: {file}")

        return os.path.isfile(cls.get_ffmpeg_path())

    @classmethod
    def get_yt_dlp_path(cls) -> str:
        """获取 yt-dlp 可执行文件路径

        Returns:
            yt-dlp.exe 路径，如果不存在返回空字符串
        """
        yt_dlp_path = os.path.join(cls.get_yt_dlp_dir(), "yt-dlp.exe").replace("\\", "/")
        if os.path.isfile(yt_dlp_path):
            return yt_dlp_path
        return ""

    @classmethod
    def get_ffmpeg_path(cls) -> str:
        """获取 ffmpeg 可执行文件路径

        Returns:
            ffmpeg.exe 路径，如果不存在返回空字符串
        """
        ffmpeg_path = os.path.join(cls.get_ffmpeg_dir(), "ffmpeg.exe").replace("\\", "/")
        if os.path.isfile(ffmpeg_path):
            return ffmpeg_path
        return ""

    @classmethod
    def get_ffprobe_path(cls) -> str:
        """获取 ffprobe 可执行文件路径

        Returns:
            ffprobe.exe 路径，如果不存在返回空字符串
        """
        ffprobe_path = os.path.join(cls.get_ffmpeg_dir(), "ffprobe.exe").replace("\\", "/")
        if os.path.isfile(ffprobe_path):
            return ffprobe_path
        return ""

    @classmethod
    def check_tools_exist(cls) -> dict:
        """检查工具是否存在

        Returns:
            包含检查结果的字典
        """
        yt_dlp_exists = bool(cls.get_yt_dlp_path())
        ffmpeg_exists = bool(cls.get_ffmpeg_path())

        return {
            "yt_dlp_exists": yt_dlp_exists,
            "yt_dlp_path": cls.get_yt_dlp_path() if yt_dlp_exists else "",
            "ffmpeg_exists": ffmpeg_exists,
            "ffmpeg_path": cls.get_ffmpeg_path() if ffmpeg_exists else "",
            "all_exist": yt_dlp_exists and ffmpeg_exists
        }

    @classmethod
    def _ensure_tools_dir(cls):
        """确保工具目录存在"""
        tools_dir = cls.get_tools_dir()
        os.makedirs(tools_dir, exist_ok=True)
        os.makedirs(cls.get_yt_dlp_dir(), exist_ok=True)
        os.makedirs(cls.get_ffmpeg_dir(), exist_ok=True)
        logger.info(f"工具目录已创建: {tools_dir}")

    @classmethod
    def download_yt_dlp(cls, progress_callback=None) -> bool:
        """下载 yt-dlp

        Args:
            progress_callback: 进度回调函数，参数为 (downloaded, total)

        Returns:
            是否下载成功
        """
        cls._ensure_tools_dir()
        yt_dlp_path = os.path.join(cls.get_yt_dlp_dir(), "yt-dlp.exe").replace("\\", "/")
        logger.info(f"开始下载 yt-dlp 到: {yt_dlp_path}")

        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                # 下载文件
                def report_progress(block_num, block_size, total_size):
                    if progress_callback and total_size > 0:
                        downloaded = block_num * block_size
                        progress_callback(downloaded, total_size)

                # 设置超时并下载
                socket.setdefaulttimeout(DOWNLOAD_TIMEOUT)
                urllib.request.urlretrieve(cls.YT_DLP_URL, yt_dlp_path, report_progress)

                # 验证下载成功
                if os.path.isfile(yt_dlp_path):
                    logger.info(f"yt-dlp 下载成功: {yt_dlp_path}")
                    return True

                logger.error("yt-dlp 下载失败: 文件未找到")
                return False

            except Exception as e:
                last_error = e
                logger.warning(f"yt-dlp 下载尝试 {attempt + 1}/{MAX_RETRIES} 失败: {e}")
                if attempt < MAX_RETRIES - 1:
                    import time
                    time.sleep(2 ** attempt)  # 指数退避

        logger.error(f"yt-dlp 下载失败，已重试 {MAX_RETRIES} 次: {last_error}")
        return False

    @classmethod
    def download_ffmpeg(cls, progress_callback=None) -> bool:
        """下载 ffmpeg（优先使用打包的版本）

        Args:
            progress_callback: 进度回调函数，参数为 (downloaded, total)

        Returns:
            是否下载成功
        """
        # 先尝试使用打包的 ffmpeg
        if cls._copy_bundled_ffmpeg():
            logger.info("已使用打包的 ffmpeg")
            return True

        # 没有打包的则下载
        import tempfile

        cls._ensure_tools_dir()
        temp_dir = tempfile.mkdtemp()

        try:
            zip_path = os.path.join(temp_dir, "ffmpeg.zip").replace("\\", "/")
            logger.info(f"开始下载 ffmpeg...")

            last_error = None
            for attempt in range(MAX_RETRIES):
                try:
                    # 下载 zip 文件
                    def report_progress(block_num, block_size, total_size):
                        if progress_callback and total_size > 0:
                            downloaded = block_num * block_size
                            progress_callback(downloaded, total_size)

                    # 设置超时并下载
                    socket.setdefaulttimeout(DOWNLOAD_TIMEOUT)
                    urllib.request.urlretrieve(cls.FFMPEG_URL, zip_path, report_progress)

                    # 解压 zip 文件
                    logger.info("正在解压 ffmpeg...")
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)

                    # 找到解压后的 ffmpeg 目录
                    ffmpeg_bin_dir = None
                    for root, dirs, files in os.walk(temp_dir):
                        if 'ffmpeg.exe' in files:
                            ffmpeg_bin_dir = root
                            break

                    if not ffmpeg_bin_dir:
                        logger.error("ffmpeg 解压失败: 未找到 ffmpeg.exe")
                        continue

                    # 复制 ffmpeg 相关文件到目标目录
                    target_dir = cls.get_ffmpeg_dir()
                    for file in os.listdir(ffmpeg_bin_dir):
                        if file.endswith('.exe'):
                            src = os.path.join(ffmpeg_bin_dir, file).replace("\\", "/")
                            dst = os.path.join(target_dir, file).replace("\\", "/")
                            shutil.copy2(src, dst)
                            logger.info(f"已复制: {file}")

                    # 验证下载成功
                    if os.path.isfile(cls.get_ffmpeg_path()):
                        logger.info(f"ffmpeg 下载成功")
                        return True

                    logger.error("ffmpeg 下载失败: 文件未找到")
                    return False

                except Exception as e:
                    last_error = e
                    logger.warning(f"ffmpeg 下载尝试 {attempt + 1}/{MAX_RETRIES} 失败: {e}")
                    if attempt < MAX_RETRIES - 1:
                        import time
                        time.sleep(2 ** attempt)  # 指数退避

            logger.error(f"ffmpeg 下载失败，已重试 {MAX_RETRIES} 次: {last_error}")
            return False

        finally:
            # 清理临时目录
            shutil.rmtree(temp_dir, ignore_errors=True)

    @classmethod
    def get_tool_paths(cls) -> dict:
        """获取工具路径（优先从配置获取，如果配置为空则自动获取）

        Returns:
            包含工具路径的字典
        """
        from config.global_config import global_config

        # 优先使用配置中的路径
        yt_dlp_config = global_config.get("yt_dlp_path", "")
        ffmpeg_config = global_config.get("ffmpeg_path", "")

        # 如果配置路径有效，使用配置路径
        if yt_dlp_config and os.path.isfile(yt_dlp_config):
            yt_dlp_path = yt_dlp_config
        else:
            # 否则使用 tool_manager 自动获取
            yt_dlp_path = cls.get_yt_dlp_path()

        if ffmpeg_config and os.path.isfile(ffmpeg_config):
            ffmpeg_path = ffmpeg_config
        else:
            # 否则使用 tool_manager 自动获取
            ffmpeg_path = cls.get_ffmpeg_path()

        return {
            "yt_dlp_path": yt_dlp_path,
            "ffmpeg_path": ffmpeg_path
        }

    @classmethod
    def detect_yt_dlp(cls, custom_path: str = None) -> tuple:
        """检测 yt-dlp 是否可用

        检测顺序：自定义路径 -> 配置路径 -> 打包资源 -> 系统 PATH -> 内置 tools 目录

        Args:
            custom_path: 自定义检测路径

        Returns:
            tuple: (是否可用, 路径, 版本信息)
        """
        from config.global_config import global_config

        # 1. 首先检测自定义路径
        if custom_path and os.path.isfile(custom_path):
            if cls._check_yt_dlp_executable(custom_path):
                version = cls._get_yt_dlp_version(custom_path)
                return (True, custom_path, version)

        # 2. 检测配置路径
        config_path = global_config.get("yt_dlp_path", "")
        if config_path and os.path.isfile(config_path):
            if cls._check_yt_dlp_executable(config_path):
                version = cls._get_yt_dlp_version(config_path)
                return (True, config_path, version)

        # 3. 检测打包资源（优先）
        bundled_path = cls.get_bundled_yt_dlp_path()
        if bundled_path and os.path.isfile(bundled_path):
            if cls._check_yt_dlp_executable(bundled_path):
                version = cls._get_yt_dlp_version(bundled_path)
                return (True, bundled_path, version)

        # 4. 检测系统 PATH 中的 yt-dlp
        system_path = shutil.which("yt-dlp")
        if system_path and cls._check_yt_dlp_executable(system_path):
            version = cls._get_yt_dlp_version(system_path)
            return (True, system_path, version)

        # 5. 检测内置 tools 目录
        built_in_path = cls.get_yt_dlp_path()
        if built_in_path and os.path.isfile(built_in_path):
            if cls._check_yt_dlp_executable(built_in_path):
                version = cls._get_yt_dlp_version(built_in_path)
                return (True, built_in_path, version)

        return (False, "", "未安装")

    @classmethod
    def detect_yt_dlp_fast(cls) -> tuple:
        """快速检测 yt-dlp（只检测打包资源和内置目录）

        用于页面加载时的自动检测，避免检测系统 PATH 浪费时间

        Returns:
            tuple: (是否可用, 路径, 版本信息)
        """
        # 1. 检测打包资源（优先）
        bundled_path = cls.get_bundled_yt_dlp_path()
        if bundled_path and os.path.isfile(bundled_path):
            version = cls._get_yt_dlp_version_fast(bundled_path)
            if version:
                return (True, bundled_path, version)

        # 2. 检测内置 tools 目录
        built_in_path = cls.get_yt_dlp_path()
        if built_in_path and os.path.isfile(built_in_path):
            version = cls._get_yt_dlp_version_fast(built_in_path)
            if version:
                return (True, built_in_path, version)

        return (False, "", "未安装")

    @classmethod
    def detect_ffmpeg_fast(cls) -> tuple:
        """快速检测 ffmpeg（只检测打包资源和内置目录）

        用于页面加载时的自动检测，避免检测系统 PATH 浪费时间

        Returns:
            tuple: (是否可用, 路径, 版本信息)
        """
        # 1. 检测打包资源（优先）
        bundled_dir = cls.get_bundled_ffmpeg_dir()
        bundled_path = os.path.join(bundled_dir, "ffmpeg.exe").replace("\\", "/")
        if bundled_path and os.path.isfile(bundled_path):
            version = cls._get_ffmpeg_version_fast(bundled_path)
            if version:
                return (True, bundled_path, version)

        # 2. 检测内置 tools 目录
        built_in_path = cls.get_ffmpeg_path()
        if built_in_path and os.path.isfile(built_in_path):
            version = cls._get_ffmpeg_version_fast(built_in_path)
            if version:
                return (True, built_in_path, version)

        return (False, "", "未安装")

    @classmethod
    def _check_yt_dlp_executable(cls, path: str) -> bool:
        """检查 yt-dlp 是否可执行

        Args:
            path: yt-dlp 路径

        Returns:
            是否可执行
        """
        try:
            result = subprocess.run(
                [path, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=CREATE_NO_WINDOW
            )
            return result.returncode == 0
        except Exception:
            return False

    @classmethod
    def _get_yt_dlp_version(cls, path: str) -> str:
        """获取 yt-dlp 版本

        Args:
            path: yt-dlp 路径

        Returns:
            版本号
        """
        try:
            result = subprocess.run(
                [path, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "未知版本"

    @classmethod
    def _get_yt_dlp_version_fast(cls, path: str) -> str:
        """快速获取 yt-dlp 版本（使用较短超时）

        Args:
            path: yt-dlp 路径

        Returns:
            版本号，如果失败返回空字符串
        """
        try:
            result = subprocess.run(
                [path, "--version"],
                capture_output=True,
                text=True,
                timeout=2,
                creationflags=CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return ""

    @classmethod
    def detect_ffmpeg(cls, custom_path: str = None) -> tuple:
        """检测 ffmpeg 是否可用

        检测顺序：自定义路径 -> 配置路径 -> 打包资源 -> 系统 PATH -> 内置 tools 目录

        Args:
            custom_path: 自定义检测路径

        Returns:
            tuple: (是否可用, 路径, 版本信息)
        """
        from config.global_config import global_config

        # 1. 首先检测自定义路径
        if custom_path and os.path.isfile(custom_path):
            if cls._check_ffmpeg_executable(custom_path):
                version = cls._get_ffmpeg_version(custom_path)
                return (True, custom_path, version)

        # 2. 检测配置路径
        config_path = global_config.get("ffmpeg_path", "")
        if config_path and os.path.isfile(config_path):
            if cls._check_ffmpeg_executable(config_path):
                version = cls._get_ffmpeg_version(config_path)
                return (True, config_path, version)

        # 3. 检测打包资源（优先）
        bundled_dir = cls.get_bundled_ffmpeg_dir()
        bundled_path = os.path.join(bundled_dir, "ffmpeg.exe").replace("\\", "/")
        if bundled_path and os.path.isfile(bundled_path):
            if cls._check_ffmpeg_executable(bundled_path):
                version = cls._get_ffmpeg_version(bundled_path)
                return (True, bundled_path, version)

        # 4. 检测系统 PATH 中的 ffmpeg
        system_path = shutil.which("ffmpeg")
        if system_path and cls._check_ffmpeg_executable(system_path):
            version = cls._get_ffmpeg_version(system_path)
            return (True, system_path, version)

        # 5. 检测内置 tools 目录
        built_in_path = cls.get_ffmpeg_path()
        if built_in_path and os.path.isfile(built_in_path):
            if cls._check_ffmpeg_executable(built_in_path):
                version = cls._get_ffmpeg_version(built_in_path)
                return (True, built_in_path, version)

        return (False, "", "未安装")

    @classmethod
    def _check_ffmpeg_executable(cls, path: str) -> bool:
        """检查 ffmpeg 是否可执行

        Args:
            path: ffmpeg 路径

        Returns:
            是否可执行
        """
        try:
            result = subprocess.run(
                [path, "-version"],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=CREATE_NO_WINDOW
            )
            return result.returncode == 0
        except Exception:
            return False

    @classmethod
    def _get_ffmpeg_version(cls, path: str) -> str:
        """获取 ffmpeg 版本

        Args:
            path: ffmpeg 路径

        Returns:
            版本号
        """
        try:
            result = subprocess.run(
                [path, "-version"],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                # 提取第一行版本信息
                first_line = result.stdout.strip().split('\n')[0]
                return first_line
        except Exception:
            pass
        return "未知版本"

    @classmethod
    def _get_ffmpeg_version_fast(cls, path: str) -> str:
        """快速获取 ffmpeg 版本（使用较短超时）

        Args:
            path: ffmpeg 路径

        Returns:
            版本号，如果失败返回空字符串
        """
        try:
            result = subprocess.run(
                [path, "-version"],
                capture_output=True,
                text=True,
                timeout=2,
                creationflags=CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                # 提取第一行版本信息
                first_line = result.stdout.strip().split('\n')[0]
                return first_line
        except Exception:
            pass
        return ""

    @classmethod
    def check_yt_dlp_update(cls, yt_dlp_path: str = None) -> tuple:
        """检查 yt-dlp 是否有新版本

        Args:
            yt_dlp_path: 可选的 yt-dlp 路径，默认使用检测到的路径

        Returns:
            tuple: (是否有新版本, 当前版本, 最新版本)
        """
        import urllib.request
        import json

        # 获取当前版本
        current_version = ""
        if yt_dlp_path:
            current_version = cls._get_yt_dlp_version(yt_dlp_path)
        else:
            _, path, current_version = cls.detect_yt_dlp()
            if not path:
                return (False, current_version, "无法获取当前版本")

        # 获取最新版本
        try:
            # 使用 GitHub API 获取最新版本
            url = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
            req = urllib.request.Request(url, headers={"User-Agent": "Python"})
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode())
                latest_version = data.get("tag_name", "").lstrip("v")

                if latest_version and current_version:
                    # 比较版本（简单比较）
                    return (latest_version != current_version, current_version, latest_version)
        except Exception as e:
            logger.warning(f"检查 yt-dlp 更新失败: {e}")

        return (False, current_version, current_version)

    @classmethod
    def update_yt_dlp(cls, target_path: str = None, progress_callback=None) -> bool:
        """更新 yt-dlp 到最新版本

        Args:
            target_path: 目标路径，默认更新到内置 tools 目录
            progress_callback: 进度回调函数

        Returns:
            是否更新成功
        """
        import urllib.request
        import json

        # 获取最新下载链接
        try:
            url = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
            req = urllib.request.Request(url, headers={"User-Agent": "Python"})
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode())
                latest_version = data.get("tag_name", "").lstrip("v")

                # 查找 Windows 可执行文件
                download_url = None
                for asset in data.get("assets", []):
                    if asset.get("name", "").endswith(".exe"):
                        download_url = asset.get("browser_download_url")
                        break

                if not download_url:
                    logger.error("未找到 yt-dlp Windows 可执行文件")
                    return False

                logger.info(f"准备下载 yt-dlp {latest_version}")

                # 确定目标路径
                if not target_path:
                    cls._ensure_tools_dir()
                    target_path = os.path.join(cls.get_yt_dlp_dir(), "yt-dlp.exe").replace("\\", "/")

                # 下载文件
                last_error = None
                for attempt in range(MAX_RETRIES):
                    try:
                        def report_progress(block_num, block_size, total_size):
                            if progress_callback and total_size > 0:
                                downloaded = block_num * block_size
                                progress_callback(downloaded, total_size)

                        socket.setdefaulttimeout(DOWNLOAD_TIMEOUT)
                        urllib.request.urlretrieve(download_url, target_path, report_progress)

                        if os.path.isfile(target_path):
                            logger.info(f"yt-dlp 更新成功: {target_path}")
                            return True

                    except Exception as e:
                        last_error = e
                        logger.warning(f"yt-dlp 更新尝试 {attempt + 1}/{MAX_RETRIES} 失败: {e}")
                        if attempt < MAX_RETRIES - 1:
                            import time
                            time.sleep(2 ** attempt)

                logger.error(f"yt-dlp 更新失败: {last_error}")
                return False

        except Exception as e:
            logger.error(f"获取 yt-dlp 最新版本信息失败: {e}")
            return False
