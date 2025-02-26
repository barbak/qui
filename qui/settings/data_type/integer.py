"""
    UI Setting handling an integer value.
"""
from PySide6 import QtCore
from PySide6.QtWidgets import QSpinBox


class UI(QSpinBox):

    settingsUpdated = QtCore.Signal(dict)

    def __init__(self, name, default_value=None):
        super(UI, self).__init__()
        if default_value is not None:
            self.setValue(default_value)

        self.name = name
        self.default_value = default_value
        self.valueChanged.connect(self.valueChangedSlot)

    def valueChangedSlot(self):
        self.settingsUpdated.emit({self.name: self.value()})
