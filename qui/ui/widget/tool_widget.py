"""
    ToolWidget related module.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from qui.settings import SettingsHandler

from .. button import (
    ButtonBox,
)


class SettingsHandlerWidget(QScrollArea):
    def __init__(self, parent=None):
        super(SettingsHandlerWidget, self).__init__(parent=parent)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setWidgetResizable(True)
        self.setStyleSheet("""
            SettingsHandlerWidget {
                border: 1px solid black;
            }
            """)


class ToolWidget(QWidget):
    """
    Base class for tool widget with predefined close and
    potentially refresh/close/settings button ready to use.
    """

    def __init__(self, refresh_slot=None):
        """
        `refresh_slot` is the function to be bind with the refresh button if the
        """
        super().__init__()
        self._doc_url = None
        layout = QVBoxLayout()
        layout.setContentsMargins(3, 3, 3, 3)
        super().setLayout(layout)
        # Create a widget placeholder
        self.content_widget = QWidget()
        self.settings_widget = SettingsHandlerWidget()
        # self.refresh = refresh_slot if refresh_slot else lambda: None
        self.button_box = ButtonBox(self.close,
                                    refresh_slot=refresh_slot,
                                    settings_slot=self.create_settings_widget_slot)
        self.button_box.settings_btn.clicked.connect(self._settingsBtnSlot)
        self.settings_widget.setVisible(False)
        self.settings_handler: SettingsHandler = SettingsHandler(self)  # Init it in your tool
        layout.addWidget(self.content_widget, 1)
        layout.addWidget(self.settings_widget, 1)
        layout.addWidget(self.button_box)

    def setLayout(self, layout):
        self.content_widget.setLayout(layout)

    def layout(self):
        return self.content_widget.layout()

    def setRefreshSlot(self, refresh_slot):
        if self.button_box is not None:
            self.button_box.refresh_btn.clicked.connect(refresh_slot)
            self.button_box.refresh_btn.setVisible(True)

    def showSettingsBtnSlot(self):
        """
        To be plugged on SettingsHandler.settingsUpdated.
        """
        if self.button_box is not None:
            self.button_box.settings_btn.setVisible(True if self.settings_handler else False)

    def _settingsBtnSlot(self):
        if self.button_box is not None:
            settings_on = self.button_box.settings_btn.isChecked()
            if self.settings_handler is not None:
                self.settings_handler.load()
            self.content_widget.setVisible(not settings_on)
            self.settings_widget.setVisible(settings_on)

    @property
    def doc_url(self):
        return self._doc_url

    @doc_url.setter
    def doc_url(self, value):
        from functools import partial
        self._doc_url = value
        if value is not None:
            self.button_box.doc_btn.clicked.connect(
                partial(self.button_box.open_doc_url, value)
            )

        self.button_box.doc_btn.setVisible(False if self._doc_url is None else True)

    def create_settings_widget_slot(self):
        """
        Populate the settings_widget if it has not been already populated.
        """
        if self.settings_handler is None:
            raise RuntimeError(
                "Cannot create settings widget, no settings handler found."
            )

        if self.settings_widget.widget() is None:
            widget = QWidget()
            layout = QVBoxLayout()
            widget.setLayout(layout)
            layout.setContentsMargins(3, 3, 0, 3)
            layout.setSpacing(3)
            row_number = 0
            grid_layout = QGridLayout()
            grid_layout.setColumnStretch(0, 0)
            grid_layout.setColumnStretch(1, 1)
            for setting in self.settings_handler:
                label = None
                if setting.label:
                    # Add a trailing space to avoid label being cropped when
                    # checking a QCheckBox (probably other widgets are concerned)
                    label = QLabel(f"{setting.label} ")
                    label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignRight.AlignCenter)
                    label.setToolTip(setting.tooltip)

                if label:
                    label.setBuddy(setting.ui)
                    grid_layout.addWidget(label, row_number, 0)
                    grid_layout.addWidget(setting.ui, row_number, 1)

                else:
                    # If no label is present we put the widget as a complete row
                    # Useful for very tool specific widget.
                    grid_layout.addWidget(setting.ui, row_number, 0, 1, 2)

                row_number += 1

            layout.addLayout(grid_layout)
            layout.addStretch(1)
            self.settings_widget.setWidget(widget)

    @property
    def userStylableColors(self):
        return {
            'unchecked_color': "red",
            'checked_color': "green",
            'disabled_color': "Gray",
        }

    def enableUserStylableCSS(self, value):
        self.patchStyleSheetSlot({'vivid_colors': value})

    def patchStyleSheetSlot(self, settings):
        """
        Plug this to settingsUpdated signal.
        TODO: Should use self.settings instead of a arg passing.
        DEPRECATED
        """
        userStylableColors = self.userStylableColors
        if 'vivid_colors' in settings:
            self.setStyleSheet("")  # To Force color reevaluation.
            if settings['vivid_colors'] is True:
                # (#15001567)
                # have to set `border: none` to override default.
                # https://forum.qt.io/topic/41325/solved-background-of-checked-qpushbutton-with-stylesheet
                self.setStyleSheet(f"""
                QPushButton[userStylable=true] {{
                    background-color: {userStylableColors['unchecked_color']};
                    padding: 5px;
                    border-radius: 1px;
                    border: none;
                }}
                QPushButton:checked[userStylable=true] {{
                    background-color: {userStylableColors['checked_color']};
                }}
                QPushButton:disabled[userStylable=true] {{
                    background-color: {userStylableColors['disabled_color']};
                    color: #AAA;
                }}
                """)
