"""
    UI Setting handling a filename value.
"""
import os

from PySide6 import QtCore
from PySide6.QtWidgets import (
    QFileDialog,
    QLineEdit,
    QHBoxLayout,
    QWidget,
)

from qui.ui.button import QuickButton
from qui import icon_provider


class UI(QWidget):

    settingsUpdated = QtCore.Signal(dict)

    def __init__(self, name, default_value=None):
        super(UI, self).__init__()
        self.name = name
        self.default_filename = default_value
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(
            "Unset value" if default_value is None else default_value
        )
        self.button = QuickButton(
            icon=icon_provider.get('fileNew.png', color=(32, 32, 32)),
            clicked_slot=self.buttonClickedSlot,
        )
        self.dialog = QFileDialog(self)
        self.dialog.setFileMode(QFileDialog.ExistingFile)
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.line_edit, 2)
        self.layout().addWidget(self.button)
        self.layout().addStretch(1)
        self.dialog.fileSelected.connect(self.filenameSelectedSlot)
        self.line_edit.textEdited.connect(self.filenameEditedSlot)

    def buttonClickedSlot(self):
        if self.value() is not None:
            filename = self.value()
            self.dialog.setDirectory(os.path.dirname(filename))
            self.dialog.selectFile(self.value())

        self.dialog.exec_()

    def filenameEditedSlot(self, text):
        self.setValue(text)

    def filenameSelectedSlot(self, filename):
        self.setValue(filename)

    def setValue(self, value):
        self.line_edit.setText(value)
        self.settingsUpdated.emit({self.name: self.value()})

    def value(self):
        if self.line_edit.text() == '':
            return self.default_filename

        return self.line_edit.text()
