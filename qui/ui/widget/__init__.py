"""
    Widget related implementations.
"""
from collections import OrderedDict

from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QPalette,
)
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from qui import icon_provider

from qui.ui.button import (
    QuickButton,
)

from .asset_widget import AssetTreeWidget
from .tool_widget import ToolWidget


class FrameLayoutWidget(QWidget):
    """
    More or less Python port of the ELF `frameLayout` control.
    It's a kind of collapsible QGroupBox with a big header.
    """

    collapsed = QtCore.Signal()

    def __init__(self, text=None, checked=True, collapsable=True,
                 parent=None, f=Qt.WindowFlags()):
        super(FrameLayoutWidget, self).__init__(parent=parent, f=f)
        layout = QVBoxLayout()
        super(FrameLayoutWidget, self).setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        bg_color = self.palette().color(QPalette.Button).rgba()
        fg_color = self.palette().color(QPalette.Text).rgba()
        if collapsable is True:
            self.__button = QToolButton(text=text, checkable=True, checked=checked)
            self.__button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.__button.setStyleSheet(
                f"""
                QToolButton {{
                    background-color: "#{bg_color:06x}";
                    padding: "3px";
                    font-weight: bold;
                    text-align: left;
                    color: "#{fg_color:06x}";
                    border-radius: "3px";
                }};
                """
            )
            self.__button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            self.__button.setArrowType(Qt.DownArrow if self.__button.isChecked() else Qt.RightArrow)
            self.__button.toggled.connect(self.toggleSlot)

        else:
            self.__button = QPushButton(text)
            self.__button.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: "#{bg_color:06x}";
                    padding: "3px";
                    padding-left: 10px;
                    text-align: left;
                    color: "#{fg_color:06x}";
                    border-radius: "3px";
                }}
                """
            )

        self.__group_box = QGroupBox()
        layout.addWidget(self.__button)
        layout.addWidget(self.__group_box, 2)
        layout.addStretch(1)
        if type(self.__button) is QToolButton:
            self.__group_box.setVisible(self.__button.isChecked())

    def toggleSlot(self, value):
        self.__button.setArrowType(Qt.DownArrow if self.__button.isChecked() else Qt.RightArrow)
        self.__group_box.setVisible(self.__button.isChecked())
        self.collapsed.emit()

    def setLayout(self, layout):
        return self.__group_box.setLayout(layout)

    def layout(self):
        return self.__group_box.layout()

    def setTitle(self, title):
        self.__button.setText(title)

    def title(self):
        return self.__button.text()

    def isCollapsed(self):
        return self.__button.isChecked() is False

    def setCollapsed(self, value):
        return self.__button.setChecked(value is False)


class P4SettingsWidget(ToolWidget):
    """
    import qui.ui.widget
    qui.ui.widget.P4SettingsWidget().show()
    """
    def __init__(self, parent=None, f=Qt.WindowFlags(), is_window_widget=False):
        from vcs import perforce
        super(P4SettingsWidget, self).__init__(parent=parent, f=f,
                                               is_window_widget=is_window_widget)
        self.setWindowTitle('P4 Settings')
        form_layout = QFormLayout()
        self.setLayout(form_layout)
        perforce_dict = {}
        with perforce.server.connect() as p4:
            perforce_dict.update(perforce.get_current_configuration_dict(p4))

        self.widget_dict = OrderedDict.fromkeys([
            'user',
            'server_level',
            'port',
            'client',
            'password',
            # 'connected',
            'cwd',
            'editor',
            'api_level',
        ])
        for k in self.widget_dict:
            self.widget_dict[k] = QLineEdit()
            self.widget_dict[k].setPlaceholderText(f"{perforce_dict.get(k, 'QUIUndefined')}")
            form_layout.addRow(k, self.widget_dict[k])



