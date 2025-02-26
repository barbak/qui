"""
    ui package.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QFrame,
)



class PixmapAndLabel(QFrame):
    """
    QFrame with 2 QLabels.
    QHBoxLayout[[Label With Pixmap][Label WithText][Stretch 1]]
    """
    def __init__(self, pixmap=None, text=str()):
        super(PixmapAndLabel, self).__init__()
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.pixmap_label = QLabel()
        self.pixmap_label.setPixmap(pixmap)
        self.text_label = QLabel(text)
        self.text_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.layout().addWidget(self.pixmap_label)
        self.layout().addWidget(self.text_label, 1)

    def setText(self, text):
        self.text_label.setText(text)


class ClearableLineEdit(QLineEdit):
    """
    QLineEdit with a cross button appearing when the content is not empty.
    User can cLick the button to clear the line edit.
    +------------------------------+
    |         QLineEdit         [x]| <-- Clearable button
    +------------------------------+
    """
    def __init__(self, parent=None):
        from . import icon_provider
        super(ClearableLineEdit, self).__init__(parent=parent)
        action = self.addAction(
            icon_provider.get('cross_badge.svg', color=(0x66, 0x66, 0x66)),
            QLineEdit.TrailingPosition
        )
        action.setToolTip('Clear filter')
        action.setVisible(False)
        action.triggered.connect(self.clear)
        self.textChanged.connect(self.__toggle_clearable_button_slot)

    def __toggle_clearable_button_slot(self, text):
        self.actions()[0].setVisible(text != '')


def get_readable_text_color(background_color):
    """
    Return a visually readable QColor depending of the QColor
    `background_color`.
    """
    light_color, dark_color = QColor(), QColor()
    light_color.setNamedColor("#eee")
    dark_color.setNamedColor("#111")
    piggy_lum = (
            0.2 * background_color.red() +
            0.7 * background_color.green() +
            0.1 * background_color.blue()
    )
    return light_color if piggy_lum < 127.0 else dark_color
