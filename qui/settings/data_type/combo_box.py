"""
    UI Setting handling a combobox value.
"""
import types

from PySide6 import QtCore
from PySide6.QtWidgets import QComboBox

def qt_combobox_items_string_list(combo_box):
    """
    Return the items' text list from the QCombobox `combo_box`.
    """
    item_texts = []
    model = combo_box.model()
    for i in range(model.rowCount()):
        item_texts.append(model.item(i, 0).text())

    return item_texts


class UI(QComboBox):

    settingsUpdated = QtCore.Signal(dict)

    def __init__(self, name, default_value=None):
        super(UI, self).__init__()

        self.name = name
        self.currentIndexChanged.connect(self.currentIndexChangedSlot)
        self.default_value = default_value
        self.items_string_list = types.MethodType(qt_combobox_items_string_list, self)

    def setValue(self, value):
        self.setCurrentIndex(value)

    def value(self):
        return self.currentIndex()

    def currentIndexChangedSlot(self):
        self.settingsUpdated.emit({self.name: self.value()})
