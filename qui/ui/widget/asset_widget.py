"""
    Reusable asset related widgets.
"""
import os

from PySide6 import QtCore
from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QTreeWidget,
    QWidget,
    QSizePolicy,
    QHBoxLayout,
    QTreeWidgetItem,
)

from datetime import datetime, timedelta
from qui.ui.button import QuickButton
from qui import icon_provider
from qui.vcs import perforce

__client_root = None
__last_call_datetime = None
def remove_client_root_from_filename(filename):
    """
    Return `filename` without the path part corresponding to the current user
    client root returned by the command 'p4 info'.
    Note 'p4 info' command is cached for 10 sec.
    """
    global __client_root, __last_call_datetime

    realpath = os.path.realpath(filename)
    if __client_root is not None:
        if (datetime.now() - __last_call_datetime) > timedelta(seconds=10):
            __client_root = None

    if __client_root is None:
        with perforce.server.connect() as p4:
            res = p4.run('info')[0]
            __client_root = os.path.realpath(res['clientRoot'])

    __last_call_datetime = datetime.now()
    offset = (
        0 if __client_root.endswith('/') or __client_root.endswith('\\')
        else 1
    )
    return "{}".format(realpath[len(__client_root) + offset:])



class AssetTreeFilterMixin(object):
    """
    Mixin to help creating a filter widget compatible with the AssetTreeWidget.
    """
    filterChanged = QtCore.Signal()

    @property
    def filter_str(self):
        raise NotImplementedError()

    @property
    def extensions(self):
        raise NotImplementedError()


class AssetTreeWidget(QTreeWidget):
    class ItemWidget(QWidget):
        def __init__(self, parent=None, f=Qt.WindowFlags()):
            super(AssetTreeWidget.ItemWidget, self).__init__(
                parent=parent, f=f
            )
            self.keys = []
            self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 3, 0)
            layout.addStretch(1)
            self.button = QuickButton("", clicked_slot=self.clickedSlot)
            layout.addWidget(self.button)
            self.setLayout(layout)
            self.setStyleSheet("""
                QuickButton {
                    background-color: "#A33";
                    width: 16;
                    font-weight: bold;
                }
                QuickButton:pressed {
                    background-color: rgb(85, 25, 25);
                    padding: 5px;
                    border-radius: 1px;
                }
                QuickButton[isLatestRev="true"] {
                    background-color: rgb(51, 170, 51);
                }
                QuickButton[isLatestRev="true"]:pressed {
                    background-color: rgb(25, 85, 25);
                }
                QuickButton[isLatestRev="false"] {
                    background-color: rgb(170, 170, 51);
                }
                QuickButton[isLatestRev="false"]:pressed {
                    background-color: rgb(85, 85, 25);
                }
            """)

        def _updateButtonToolTip(self):
            d = self.property_dict
            if 'haveRev' in d:
                already_checked_out = (
                    "C"
                    if 'otherAction' in d or 'action' in d
                    else ''
                )
                self.button.setToolTip(
                    "{}/{}".format(d['haveRev'], d['headRev'])
                )
                self.button.setProperty(
                    str('isLatestRev'), d['haveRev'] == d['headRev']
                )
                self.button.setText("C" if already_checked_out else '')
                others = []
                if 'action' in d:
                    others.append("{} ({}) #{}".format(
                        d['actionOwner'], d['action'], d['change'])
                    )

                if 'otherAction' in d:
                    for user, action in zip(d['otherOpen'], d['otherAction']):
                        others.append("{} ({})".format(user, action))

                if others != []:
                    self.button.setToolTip(
                        "{}\n{}".format(self.button.toolTip(), "\n".join(others))
                    )

            else:
                self.button.setToolTip("Not perforced !")
                # Remove isLatestRev property
                # https://doc.qt.io/qtforpython-5.12/pysideapi2.html#qvariant
                self.button.setProperty(str('isLatestRev'), None)

            # trigger an update to use the correct style
            # if properties has changed.
            self.button.style().unpolish(self.button)
            self.button.style().polish(self.button)

        def clickedSlot(self):
            with perforce.server.connect() as p4:
                filename = self.property(str('clientFile'))
                print("Updating {} ...".format(repr(filename)))
                res = p4.run('sync', '-f', filename)
                if res != []:
                    res = p4.run('fstat', filename)
                    try:
                        self.property_dict = res[0]

                    except KeyError:
                        print("WRN - Some expected keys are missing.", repr(res[0]))

                print("Done.")

        @property
        def property_dict(self):
            d = {}.fromkeys(self.keys)
            for k in d:
                d[k] = self.property(str(k))

            return d

        @property_dict.setter
        def property_dict(self, property_dict):
            for k in property_dict:
                self.setProperty(str(k), property_dict[k])
                if k not in self.keys:
                    self.keys.append(k)

            self._updateButtonToolTip()

    def __init__(self, filter_widget, list_asset_func, parent=None):
        """
        TODO correct docstring.
        `filter_widget` is an object with 2 mandatories properties:
                filter_str, returning the filter string
                (will be lowered and split on spaces, matches by the `in`
                operator)
                extensions list of type [".ma", ".mb", ".fbx"] or None
                if no extension filtering is wanted.
        `list_asset_func` return a list of dict such as:
        [
            {
                'clientFile': realpath,
                'basename': os.path.basename(realpath),
            }
        ]
        """
        super(AssetTreeWidget, self).__init__(parent=parent)
        self.get_asset_list = list_asset_func
        self.filter_widget = filter_widget
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.filter_widget.filterChanged.connect(self.update_items_visibility)
        self.setColumnCount(2)
        self.setHeaderLabels(['Asset Name', 'Directory'])
        self.sortByColumn(1, Qt.AscendingOrder)

    @property
    def current_item_property_dict(self):
        item = self.currentItem()
        if item is None:
            return None

        return self.itemWidget(item, 1).property_dict

    def get_item_property_dict(self, item):
        return self.itemWidget(item, 1).property_dict

    def update_items_visibility(self):
        filter_str = self.filter_widget.filter_str.lower()
        extensions = self.filter_widget.extensions
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            w = self.itemWidget(item, 1)
            basename = w.property(str('clientFile')).lower()
            _, ext = os.path.splitext(basename)
            hidden = False
            if filter_str != '' and not all(s in basename
                                            for s in filter_str.split()):
                hidden = True

            if extensions is not None and ext not in extensions:
                hidden = True

            item.setHidden(hidden)

    def populate(self):
        self.clear()
        try:
            self.setSortingEnabled(False)
            self.hide()
            for a in self.get_asset_list():
                item = QTreeWidgetItem()
                item.setText(0, a['basename'])
                item.setText(
                    1,
                    utils.path.remove_client_root_from_filename(
                        os.path.dirname(a['clientFile'])
                    ).replace("\\", " ")
                )
                item.setIcon(1, icon_provider.get('empty.svg'))
                item.setToolTip(0, a['clientFile'])
                item.setToolTip(1, os.path.dirname(a['clientFile']))
                w = self.ItemWidget(self)
                w.setProperty(str('clientFile'), a['clientFile'])
                w.property_dict = a
                self.addTopLevelItem(item)
                self.setItemWidget(item, 1, w)

        except Exception:
            import traceback
            traceback.print_exc()

        finally:
            self.resizeColumnToContents(0)
            self.show()
            self.setSortingEnabled(True)
            self.filter_widget.filterChanged.emit()

    def tree_widget_item(self, filename):
        name = os.path.basename(filename)
        # In an ideal world (ie. not on windows), you should be able
        # to do this like that.
        # for i in self.findItems(name, Qt.MatchExactly):
        # But instead you have to ignore case...
        for i in self.findItems(name, Qt.MatchFixedString):
            w = self.itemWidget(i, 1)
            src_file = os.path.realpath(w.property(str('clientFile')))
            if src_file.lower() == os.path.realpath(filename).lower():
                # We have not totally given up, so we issue a warning
                # to remember.
                if src_file != os.path.realpath(filename):
                    print(
                        "WRN - Case mismatch between local and perforce file. "
                        "({} / {})".format(
                            repr(src_file), repr(os.path.realpath(filename))
                        )
                    )

                return i

        raise RuntimeError("Filename {} has no item widget associated.".format(
            repr(filename)
        ))

    def tree_widget_items(self):
        return self.findItems("", Qt.MatchContains)

    def update_perforce_infos(self):
        item_dicts = []
        with perforce.server.connect() as p4:
            with p4.at_exception_level(p4.RAISE_NONE):
                item_dicts += p4.run(
                    'fstat',
                    [
                        d['clientFile']
                        for d in [
                            self.itemWidget(self.topLevelItem(i), 1).property_dict
                            for i in range(self.topLevelItemCount())
                        ]
                    ]
                )

        for d in item_dicts:
            item_widget = self.itemWidget(
                self.tree_widget_item(d['clientFile']), 1
            )

            if item_widget is None:
                raise RuntimeError(
                    "Cannot find item and/or widget for {}.".format(repr(d))
                )

            # NOTES
            # returned dict does not have necessary the haveRev and headRev
            # depending if the file is opened for add / edit.
            # Attributes name can differ depending of the action / headAction field.
            # TODO: Investigate this more deeply.
            # if 'haveRev' not in d:
            #     print("WRN - No haveRev in dict the file is probably not synced.\n{}.".format(repr(d)))
            #
            # if 'headRev' not in d:
            #     print("WRN - No headRev in dict the file is probably not synced.\n{}.".format(repr(d)))

            item_widget.property_dict = d
            item_widget.property_dict = { # FIXME APA Typo ??? Use dict.update instead ?
                'isLatestRev': d.get('haveRev', "-1") == d.get('headRev', "0")
            }
