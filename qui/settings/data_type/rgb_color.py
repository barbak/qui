"""
    UI Setting handling a named color value.
"""
from PySide6 import QtCore
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QHBoxLayout,
    QWidget,
)

from qui.ui import get_readable_text_color
from qui.ui.button import QuickButton


class UI(QWidget):

    settingsUpdated = QtCore.Signal(dict)

    def __init__(self, name, default_value=None):
        super(UI, self).__init__()
        self.name = name
        self.default_color = QColor()
        self.color = QColor()
        if default_value is not None:
            if type(default_value) in [tuple, list]:
                self.default_color.setRgb(*default_value)

            elif type(default_value) is str:
                self.default_color.setNamedColor(default_value)

            self.color = QColor(self.default_color)

        self.button = QuickButton(
            self.color.name(), clicked_slot=self.buttonClickedSlot
        )
        self.reset_btn = QuickButton("Reset", clicked_slot=self.resetSlot)
        self.dialog = QColorDialog(self)
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.button, 2)
        self.layout().addWidget(self.reset_btn)
        self.layout().addStretch(1)
        self.dialog.colorSelected.connect(self.colorSelectedSlot)

    def resetSlot(self):
        self.setValue(self.default_color.name())
        self.colorSelectedSlot(self.default_color)

    def buttonClickedSlot(self):
        self.dialog.setCurrentColor(self.color)
        self.dialog.exec_()

    def updateButtonColors(self):
        text_color = get_readable_text_color(self.color)
        self.button.setStyleSheet(
            'background-color: {};'.format(self.color.name()) +
            'color: {};'.format(text_color.name())
        )

    def colorSelectedSlot(self, color):
        self.color = color
        self.updateButtonColors()
        self.button.setText(color.name())
        self.settingsUpdated.emit({self.name: self.color.name()})

    def setValue(self, value):
        c = QColor()
        if type(value) in [tuple, list]:
            c.setRgb(*value)

        else:
            c.setNamedColor(value)

        if c.isValid() is False:
            raise ValueError(
                "Cannot set invalid color value {} to {} setting.".format(
                    repr(value), repr(self.name)
                )
            )
        self.colorSelectedSlot(c)

    def value(self):
        return self.color.name()
