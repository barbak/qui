"""
    ComboBox related implementations.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QComboBox,
    QSizePolicy,
    QSpacerItem,
    QWidget,
    QHBoxLayout,
)

def _sorted_unique_list(x):
    """
    Return a sorted list with unique values.
    """
    return sorted(list(set(x)))


class IdedComboBox(QComboBox):
    """
    QComboBox with an id.
    """
    def __init__(self, _id, parent=None):
        super().__init__(parent=parent)
        self.id = _id

    def itemsStringList(self):
        """
        Return the widget's string list entries available.
        """
        if not self.model():
            return []

        ret = []
        model = self.model()
        for i in range(model.rowCount()):
            ret.append(model.item(i, 0).text())

        return ret


class ComboChunkWidget(QWidget):
    """
    Quick search for structured name list with minimum prior knowledge
    of the datas we want to quick search.
    """

    def __init__(self, chunk_list=None, parent=None, f=Qt.WindowFlags()):
        """
        chunk_list of the form:
            [
                ["ck1", "ck2", ..., "ckn"],
                ...
                ["ck1", "ck2", ..., "ckm"],
            ]
        """
        from functools import partial

        super().__init__(parent=parent, f=f)
        if chunk_list is None:
            chunk_list = []

        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.combo_boxes = []
        self.chunk_list = []
        self.first_combo_box = IdedComboBox(0)
        self.first_combo_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.first_combo_box.addItems(['*'] + _sorted_unique_list([c[0] for c in self.chunk_list]))
        self.first_combo_box.currentIndexChanged.connect(
            partial(self.comboValueChangedSlot, self.first_combo_box)
        )
        self.combo_layout = QHBoxLayout()
        self.combo_layout.setContentsMargins(0, 0, 0, 0)
        self.combo_layout.setSpacing(0)
        self.layout().addWidget(self.first_combo_box)
        self.layout().addLayout(self.combo_layout)
        self.layout().addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.set_chunk_list(chunk_list)

    @property
    def current_chunks(self):
        """
        Return the current chunk value list currently selected, '*' entries
        are omitted.
        """
        current_chunks = []
        if self.first_combo_box.currentIndex() < 1:
            return current_chunks

        current_chunks.append(self.first_combo_box.currentText())
        for cb in self.combo_boxes:
            if cb.currentIndex() < 1:
                return current_chunks

            current_chunks.append(cb.currentText())

        return current_chunks

    def comboValueChangedSlot(self, combobox, index):
        from functools import partial

        if index < 1 and combobox is self.first_combo_box:  # nothing set or '*'
            self.combo_layout.clear_layout()
            self.combo_boxes = []
            return  # Nothing else to do

        # remove from combobox.id till the end.
        while self.combo_layout.count() > combobox.id:
            item = self.combo_layout.takeAt(self.combo_layout.count() - 1)
            w = item.widget()
            if w is not None:
                w.deleteLater()

            self.combo_boxes.pop()

        if index > 0:  # we are on something != '*'
            # we have to add a new chunk combobox if possible
            new_item_list = self.get_chunk_values_starting_with(self.current_chunks)
            if new_item_list:
                cb = IdedComboBox(combobox.id+1)
                cb.addItems(['*'] + new_item_list)
                cb.currentIndexChanged.connect(partial(self.comboValueChangedSlot, cb))
                self.combo_boxes.append(cb)
                self.combo_layout.addWidget(cb)

    def set_chunk_list(self, chunk_list):
        """
        Assure that we kept a full copy of the original chunk_list
        and not instances on its content.
        """
        self.chunk_list = [list(c) for c in chunk_list]
        self.set_chunk_values(self.current_chunks)

    def set_chunk_values(self, chunk_list):
        """
        TODO
        Set the widget's comboboxes to values specified by chunk_list as much as possible.
        """
        self.combo_layout.clear_layout()
        self.first_combo_box.clear()
        self.first_combo_box.addItems(['*'] + self.get_chunk_values_starting_with([]))
        for i,c in enumerate(chunk_list):
            if i == 0:
                if c not in self.first_combo_box.itemsStringList():
                    self.first_combo_box.setCurrentIndex(0)
                    return  # No more thing to do

                else:
                    self.first_combo_box.setCurrentText(c)

            else:  # self.combo_boxes
                raise NotImplementedError("Still TODO.")

    def get_chunk_values_starting_with(self, start_chunks=None):
        """
        Return the list of the possible values for the next chunk
        starting with start_chunks.
        """
        if start_chunks is None:
            start_chunks = []

        filtered_chunk_list = [list(c) for c in self.chunk_list]
        col_index = len(start_chunks)
        for i,s in enumerate(start_chunks):
            filtered_chunk_list = [ck
                                   for ck in filtered_chunk_list
                                   if i < len(ck) and ck[i] == s]

        return _sorted_unique_list([ck[col_index]
                                    for ck in filtered_chunk_list
                                    if col_index < len(ck)])
