"""Global configuration management."""
import json
import os
from typing import Any, Dict

from utils import logger


class GlobalConfig:
    """Global configuration manager with module-level support."""

    # 基础默认配置
    BASE_DEFAULT_CONFIG: Dict[str, Any] = {
        "file_path": "",  # 首次运行时会自动设置为 %APPDATA%/Sumi-Kara
        "is_first_run": True,
        "download_path": "./downloads",
        "proxy": "",
        "youtube_api_key": "",
        "bilibili_cookies": "",
        "max_concurrent_downloads": 3,
        "max_workers": 3,
        "auto_check_update": True,
        "log_level": "INFO",
        "ffmpeg_path": "",
        "yt_dlp_path": ""
    }

    # 模块级默认配置
    MODULE_DEFAULT_CONFIGS: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register_module_defaults(cls, module_name: str, defaults: Dict[str, Any]):
        """注册模块的默认配置

        Args:
            module_name: 模块名称
            defaults: 模块的默认配置字典
        """
        cls.MODULE_DEFAULT_CONFIGS[module_name] = defaults
        logger.debug(f"Registered default config for module: {module_name}")

    @classmethod
    def get_module_default(cls, module_name: str, key: str, default: Any = None) -> Any:
        """获取模块的默认配置值

        Args:
            module_name: 模块名称
            key: 配置键名
            default: 默认值

        Returns:
            配置值
        """
        module_defaults = cls.MODULE_DEFAULT_CONFIGS.get(module_name, {})
        return module_defaults.get(key, default)

    def __init__(self, config_path: str = None):
        # 自动确定配置文件路径
        if config_path is None:
            config_path = self._get_default_config_path()
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self._load()

    @classmethod
    def _get_default_config_path(cls) -> str:
        """获取默认配置文件路径

        统一使用: %APPDATA%/Sumi-Kara/config/global.json
        这样开发环境和打包环境行为一致
        """
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            return os.path.join(appdata, "Sumi-Kara", "config", "global.json").replace("\\", "/")
        # 备用：使用项目目录
        return "./config/global.json"

    def _load(self):
        """Load configuration from file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                logger.info(f"Loaded configuration from {self.config_path}")
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                self.config = self.BASE_DEFAULT_CONFIG.copy()
                self._save()
        else:
            logger.info("No config file found, using defaults")
            self.config = self.BASE_DEFAULT_CONFIG.copy()
            self._save()

    def _save(self):
        """Save configuration to file."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logger.info(f"Saved configuration to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            key: 配置键名
            default: 默认值（当配置不存在时使用基础默认配置的值）

        Returns:
            配置值
        """
        # 优先使用已保存的配置
        if key in self.config:
            return self.config[key]

        # 回退到基础默认配置
        if default is None:
            default = self.BASE_DEFAULT_CONFIG.get(key)

        return default

    def __setitem__(self, key: str, value: Any):
        """Set configuration value (dict-like interface).

        Args:
            key: 配置键名
            value: 配置值
        """
        self.config[key] = value

    def __getitem__(self, key: str) -> Any:
        """Get configuration value (dict-like interface).

        Args:
            key: 配置键名

        Returns:
            配置值
        """
        return self.get(key)

    def set(self, key: str, value: Any):
        """Set configuration value and save.

        Args:
            key: 配置键名
            value: 配置值
        """
        self.config[key] = value
        self._save()

    def save(self):
        """Save configuration to file."""
        self._save()

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration.

        Returns:
            所有配置（包含基础默认配置中未设置的值）
        """
        result = self.BASE_DEFAULT_CONFIG.copy()
        result.update(self.config)
        return result

    def reset_to_defaults(self):
        """重置所有配置为默认值"""
        self.config = self.BASE_DEFAULT_CONFIG.copy()
        self._save()
        logger.info("Configuration reset to defaults")


# Global config instance
global_config = GlobalConfig()
