"""
    UI Setting handling a boolean value.
"""
from PySide6 import QtCore
from PySide6.QtWidgets import QCheckBox


class UI(QCheckBox):

    settingsUpdated = QtCore.Signal(dict)

    def __init__(self, name, default_value=None):
        super(UI, self).__init__()
        if default_value is not None:
            self.setChecked(default_value)

        self.name = name
        self.toggled.connect(self.toggledValueSlot)

    def setValue(self, value):
        self.setChecked(value)

    def value(self):
        return self.isChecked()

    def toggledValueSlot(self):
        self.settingsUpdated.emit({self.name: self.isChecked()})
