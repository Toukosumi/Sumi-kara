"""ModuleBase - Base class for all functional modules."""
from typing import Any, Dict, Optional

from PyQt5.QtWidgets import QWidget


class ModuleBase:
    """Module base class - all functional modules inherit from this."""

    def get_name(self) -> str:
        """Module display name.

        Returns:
            Module name shown in UI
        """
        raise NotImplementedError

    def get_version(self) -> str:
        """Module version number.

        Returns:
            Module version string
        """
        return "1.0.0"

    def get_description(self) -> str:
        """Module function description.

        Returns:
            Module description
        """
        return ""

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute module functionality.

        Args:
            params: Execution parameters

        Returns:
            Execution result dictionary
        """
        raise NotImplementedError

    def get_progress(self) -> float:
        """Get current progress (0.0 - 1.0).

        Returns:
            Progress value between 0.0 and 1.0
        """
        return 0.0

    def stop(self) -> None:
        """Stop current operation."""
        pass

    def get_config_widget(self, parent: Optional[QWidget] = None) -> Optional[QWidget]:
        """Return configuration widget for this module.

        Args:
            parent: Parent widget

        Returns:
            Configuration widget or None
        """
        return None
