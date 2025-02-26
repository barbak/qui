"""
    UI Setting handling a value list of str lines.
"""
from PySide6 import QtCore
from PySide6.QtWidgets import QSpinBox, QPlainTextEdit


class UI(QPlainTextEdit):

    settingsUpdated = QtCore.Signal(dict)

    def __init__(self, name, default_value=None):
        super(UI, self).__init__()
        if default_value is not None:
            self.setValue(default_value)

        self.name = name
        self.default_value = default_value
        self.textChanged.connect(self.textChangedSlot)

    def textChangedSlot(self):
        self.settingsUpdated.emit({self.name: self.value()})

    def setValue(self, value):
        self.setPlainText("\n".join(value))

    def value(self):
        return [
            line.strip() for line in self.toPlainText().splitlines()
        ]
