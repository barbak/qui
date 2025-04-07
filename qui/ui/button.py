"""
    Custom buttons and helpers.
"""
from PySide6 import QtCore
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import (
    QIcon,
    QMouseEvent,
)
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from qui import icon_provider


class ButtonBox(QWidget):
    """
    Widget to have Close and Refresh buttons ready to use.
    `close_slot` is mandatory.
    `refresh_slot` is the function called on the refresh button clicked event.
    `settings_slot` is the function called on the settings button clicked event.
    """

    def __init__(self, close_slot, refresh_slot=None, settings_slot=None,
                 parent=None, f=Qt.WindowFlags()):
        super().__init__(parent=parent, f=f)
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.refresh_btn = QuickButton("Refresh", refresh_slot)
        if not refresh_slot:
            self.refresh_btn.setVisible(False)

        self.close_btn = QuickButton("Close", close_slot)
        self.settings_btn = QuickButton(icon=icon_provider.get('cog-solid.svg', color=(32, 32, 32)),
                                        clicked_slot=settings_slot)
        self.settings_btn.setToolTip("Toggle tool settings")
        self.settings_btn.setCheckable(True)  # On/off settings
        self.settings_btn.setVisible(False)  # Not shown by default.
        self.doc_btn = QuickButton(
            icon=icon_provider.get('interrogation_point.svg', color=(32, 32, 32))
        )
        self.doc_btn.setToolTip("Open tool documentation...")
        self.doc_btn.setVisible(False)  # Not shown by default.
        # should be visible only if there is settings.
        # The ToolWidget has automatic behaviour for this. (Shown on first setting added)
        # If you use something else you have to reimplement this behaviour
        # if you want to use it withh the settings feature.
        self.layout().addWidget(self.settings_btn)
        self.layout().addWidget(self.refresh_btn, 1)
        self.layout().addWidget(self.close_btn, 1)
        self.layout().addWidget(self.doc_btn)

    def open_doc_url(self, doc_url):
        import webbrowser
        webbrowser.open(doc_url)


class QuickButton(QPushButton):
    """
    Wrapper around QPushButton, to create it properly set in one call.
    """

    doubleClicked = QtCore.Signal(QMouseEvent)
    rightPressed = QtCore.Signal(QMouseEvent)

    def __init__(self,
                 text="",
                 clicked_slot=None,
                 tooltip=None,
                 properties=None,
                 icon=QIcon(),
                 icon_size=None,
                 parent=None):
        """
        `icon_size` is a tuple(int(width), int(height))
        """
        super().__init__(icon=icon, text=text, parent=parent)
        self._clicked_slot = clicked_slot
        if properties is None:
            properties = {}

        if text:
            self.setText(text)

        if clicked_slot:
            self.clicked.connect(clicked_slot)

        if tooltip is not None:
            self.setToolTip(tooltip)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        if icon_size is not None:
            self.setIconSize(QSize(*icon_size))

        for k, v in properties.items():
            self.setProperty(str(k), v)

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.rightPressed.emit(event)

        super().mousePressEvent(event)

    @property
    def clicked_slot(self):
        return self._clicked_slot

    @clicked_slot.setter
    def clicked_slot(self, value):
        if self._clicked_slot:
            self.clicked.disconnect(self._clicked_slot)

        self.clicked.connect(value)
        self._clicked_slot = value


class TogglableEyeButton(QuickButton):
    def __init__(self, clicked_slot=None, tooltip=None):
        super().__init__(
            icon=icon_provider.get('eye-opened.svg'),
            tooltip=tooltip,
            clicked_slot=clicked_slot,
        )
        self.setCheckable(True)
        self.toggled.connect(self.toggled_slot)

    def toggled_slot(self, value):
        # checked -> hidden.
        self.setIcon(
            icon_provider.get(
                'eye-closed.svg' if value is True else 'eye-opened.svg'
            )
        )

    def is_eye_closed(self):
        return self.isChecked() is True

    def is_eye_opened(self):
        return self.is_eye_closed() is False

    def set_eye_closed(self, value):
        self.setChecked(value)

    def set_eye_opened(self, value):
        self.set_eye_closed(not value)
