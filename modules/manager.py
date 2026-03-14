"""Module manager - manages all registered modules."""
from typing import Dict, List, Optional

from modules.base.module_base import ModuleBase
from utils import logger


class ModuleManager:
    """Manages all functional modules."""

    def __init__(self) -> None:
        self._modules: Dict[str, ModuleBase] = {}

    def register(self, module: ModuleBase) -> None:
        """Register a module.

        Args:
            module: Module instance to register
        """
        name = module.get_name()
        if name in self._modules:
            logger.warning(f"Module '{name}' already registered, skipping")
            return
        self._modules[name] = module
        logger.info(f"Registered module: {name} (v{module.get_version()})")

    def unregister(self, name: str) -> None:
        """Unregister a module.

        Args:
            name: Module name to unregister
        """
        if name in self._modules:
            del self._modules[name]
            logger.info(f"Unregistered module: {name}")

    def get_module(self, name: str) -> Optional[ModuleBase]:
        """Get module by name.

        Args:
            name: Module name

        Returns:
            Module instance or None
        """
        return self._modules.get(name)

    def get_all_modules(self) -> List[ModuleBase]:
        """Get all registered modules.

        Returns:
            List of all modules
        """
        return list(self._modules.values())

    def get_module_names(self) -> List[str]:
        """Get all module names.

        Returns:
            List of module names
        """
        return list(self._modules.keys())

    def clear(self) -> None:
        """Clear all registered modules."""
        self._modules.clear()
        logger.info("Cleared all registered modules")


# Global module manager instance
module_manager = ModuleManager()
