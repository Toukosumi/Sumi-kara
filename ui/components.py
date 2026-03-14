"""通用 UI 组件模块 - 提供可复用的 PyQt5 组件和样式."""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton,
    QLineEdit, QComboBox, QProgressBar, QHBoxLayout, QVBoxLayout
)


# ===== 浅色主题颜色变量 =====
class ThemeColors:
    """主题颜色配置"""
    # 背景色
    LIGHT_BG = "#f5f5f5"
    LIGHT_CARD = "#ffffff"
    LIGHT_BORDER = "#e0e0e0"

    # 文字颜色
    TEXT_COLOR = "#212529"
    TEXT_SECONDARY = "#6c757d"

    # 主色调
    PRIMARY_PURPLE = "#667eea"
    PRIMARY_PURPLE_END = "#764ba2"
    PRIMARY_GREEN = "#11998e"
    PRIMARY_GREEN_END = "#38ef7d"
    PRIMARY_BLUE = "#1976d2"
    PRIMARY_BLUE_END = "#42a5f5"

    # 图标颜色
    ICON_PURPLE = "#667eea"
    ICON_GREEN = "#11998e"
    ICON_BLUE = "#1976d2"
    ICON_ORANGE = "#f97316"


# ===== 通用样式 =====
class Styles:
    """通用样式定义"""

    # 卡片样式
    CARD_STYLE = f"""
        QFrame {{
            background-color: {ThemeColors.LIGHT_CARD};
            border-radius: 8px;
            padding: 12px;
            border: 1px solid {ThemeColors.LIGHT_BORDER};
        }}
    """

    # 标题标签样式
    LABEL_TITLE_STYLE = f"""
        QLabel {{
            color: {ThemeColors.TEXT_COLOR};
            font-size: 13px;
            font-weight: bold;
        }}
    """

    # 普通标签样式
    LABEL_STYLE = f"""
        QLabel {{
            color: {ThemeColors.TEXT_SECONDARY};
            font-size: 12px;
        }}
    """

    # 表单标签样式（带图标，更醒目）
    FORM_LABEL_STYLE = f"""
        QLabel {{
            color: {ThemeColors.TEXT_COLOR};
            font-size: 13px;
            font-weight: bold;
        }}
    """

    # 输入框样式
    LINEEDIT_STYLE = f"""
        QLineEdit {{
            background-color: {ThemeColors.LIGHT_CARD};
            color: {ThemeColors.TEXT_COLOR};
            border: 1px solid {ThemeColors.LIGHT_BORDER};
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 12px;
        }}
        QLineEdit:focus {{
            border: 1px solid {ThemeColors.PRIMARY_PURPLE};
        }}
        QLineEdit:disabled {{
            background-color: {ThemeColors.LIGHT_BG};
            color: {ThemeColors.TEXT_SECONDARY};
        }}
    """

    # 下拉框样式
    COMBOBOX_STYLE = f"""
        QComboBox {{
            background-color: {ThemeColors.LIGHT_CARD};
            color: {ThemeColors.TEXT_COLOR};
            border: 1px solid {ThemeColors.LIGHT_BORDER};
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 12px;
        }}
        QComboBox:focus {{
            border: 1px solid {ThemeColors.PRIMARY_PURPLE};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {ThemeColors.TEXT_SECONDARY};
            margin-right: 8px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {ThemeColors.LIGHT_CARD};
            color: {ThemeColors.TEXT_COLOR};
            selection-background-color: {ThemeColors.PRIMARY_PURPLE};
            border: 1px solid {ThemeColors.LIGHT_BORDER};
        }}
    """

    # ===== 按钮样式 =====

    # 主按钮 - 紫色渐变
    @staticmethod
    def primary_button(gradient_start: str = ThemeColors.PRIMARY_PURPLE,
                       gradient_end: str = ThemeColors.PRIMARY_PURPLE_END) -> str:
        return f"""
            QPushButton {{
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                background: qlineargradient(x1:0, y1:0, x1:1, y1:0,
                    stop:0 {gradient_start}, stop:1 {gradient_end});
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x1:1, y1:0,
                    stop:0 {gradient_start}dd, stop:1 {gradient_end}dd);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x1:1, y1:0,
                    stop:0 {gradient_start}aa, stop:1 {gradient_end}aa);
            }}
            QPushButton:disabled {{
                background: #cccccc;
                color: #999999;
            }}
        """

    # 成功按钮 - 绿色渐变
    SUCCESS_BUTTON_STYLE = primary_button.__func__(
        ThemeColors.PRIMARY_GREEN, ThemeColors.PRIMARY_GREEN_END
    )

    # 信息按钮 - 蓝色渐变
    INFO_BUTTON_STYLE = primary_button.__func__(
        ThemeColors.PRIMARY_BLUE, ThemeColors.PRIMARY_BLUE_END
    )

    # 次要按钮 - 灰色
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

    # 危险按钮 - 红色渐变
    DANGER_BUTTON_STYLE = primary_button.__func__(
        "#dc3545", "#e74c3c"
    )

    # ===== 进度条样式 =====

    @staticmethod
    def progress_bar(gradient_start: str = ThemeColors.PRIMARY_PURPLE,
                     gradient_end: str = ThemeColors.PRIMARY_PURPLE_END) -> str:
        return f"""
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
                    stop:0 {gradient_start}, stop:1 {gradient_end});
            }}
        """

    # 蓝色进度条
    INFO_PROGRESS_STYLE = progress_bar.__func__(
        ThemeColors.PRIMARY_BLUE, ThemeColors.PRIMARY_BLUE_END
    )

    # 绿色进度条
    SUCCESS_PROGRESS_STYLE = progress_bar.__func__(
        ThemeColors.PRIMARY_GREEN, ThemeColors.PRIMARY_GREEN_END
    )


# ===== 可复用组件 =====

class CardFrame(QFrame):
    """卡片容器组件"""

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setStyleSheet(Styles.CARD_STYLE)


class TitleLabel(QLabel):
    """标题标签组件"""

    def __init__(self, text: str = "", parent: QWidget = None):
        super().__init__(text, parent)
        self.setStyleSheet(Styles.LABEL_TITLE_STYLE)


class ContentLabel(QLabel):
    """内容标签组件"""

    def __init__(self, text: str = "", parent: QWidget = None):
        super().__init__(text, parent)
        self.setStyleSheet(Styles.LABEL_STYLE)


class StyledLineEdit(QLineEdit):
    """带样式的输入框组件"""

    def __init__(self, placeholder: str = "", parent: QWidget = None):
        super().__init__(parent)
        self.setStyleSheet(Styles.LINEEDIT_STYLE)
        self.setPlaceholderText(placeholder)


class StyledComboBox(QComboBox):
    """带样式的下拉框组件"""

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setStyleSheet(Styles.COMBOBOX_STYLE)


class PrimaryButton(QPushButton):
    """主按钮（紫色）"""

    def __init__(self, text: str = "", parent: QWidget = None):
        super().__init__(text, parent)
        self.setStyleSheet(Styles.primary_button())


class SuccessButton(QPushButton):
    """成功按钮（绿色）"""

    def __init__(self, text: str = "", parent: QWidget = None):
        super().__init__(text, parent)
        self.setStyleSheet(Styles.SUCCESS_BUTTON_STYLE)


class SecondaryButton(QPushButton):
    """次要按钮（灰色）"""

    def __init__(self, text: str = "", parent: QWidget = None):
        super().__init__(text, parent)
        self.setStyleSheet(Styles.SECONDARY_BUTTON_STYLE)


class DangerButton(QPushButton):
    """危险按钮（红色）"""

    def __init__(self, text: str = "", parent: QWidget = None):
        super().__init__(text, parent)
        self.setStyleSheet(Styles.DANGER_BUTTON_STYLE)


class InfoButton(QPushButton):
    """信息按钮（天蓝色）"""

    def __init__(self, text: str = "", parent: QWidget = None):
        super().__init__(text, parent)
        self.setStyleSheet(Styles.INFO_BUTTON_STYLE)


class StyledProgressBar(QProgressBar):
    """带样式的进度条组件"""

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setStyleSheet(Styles.INFO_PROGRESS_STYLE)
        self.setTextVisible(True)
        self.setFormat("进度: %p%")
        self.setMaximumHeight(20)


class SuccessProgressBar(QProgressBar):
    """绿色进度条"""

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setStyleSheet(Styles.SUCCESS_PROGRESS_STYLE)
        self.setTextVisible(True)
        self.setFormat("进度: %p%")
        self.setMaximumHeight(20)


class FormLabel(QLabel):
    """表单行标签（带图标）"""

    def __init__(self, text: str = "", icon: str = "", parent: QWidget = None):
        super().__init__(parent)
        # 组合图标和文字
        content = f"{icon} {text}" if icon else text
        self.setText(content)
        self.setStyleSheet(Styles.FORM_LABEL_STYLE)


class FormRow(QWidget):
    """表单行组件：标签 + 控件 + 可选按钮"""

    def __init__(self, label: str, icon: str = "", label_width: int = 100, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(10)

        # 标签
        self.label = FormLabel(label, icon)
        self.label.setFixedWidth(label_width)

        # 控件容器（外部传入）
        self._main_widget = None

    def set_control(self, widget, stretch: int = 1):
        """设置主控件"""
        self._main_widget = widget
        self.layout().addWidget(self.label)
        self.layout().addWidget(widget, stretch)  # stretch 可配置

    def add_button(self, button):
        """添加按钮"""
        self.layout().addWidget(button)
