"""
    settings: scene settings, user settings, remote settings ...
"""

from PySide6 import QtCore
from PySide6.QtCore import QObject

from . import data_type

"""
TODO
    Settings base elements.
    ToolSettings is the base class, handle only runtime settings (ReadWrite)
    If you want to handle more backends subclass this.
    Used to give a common API for settings/config values.
"""
from . import backend


class ToolSettings(object):
    """
    Base class for an App Settings.
    Handle the scope 'runtime' by default.
    Implements: get / set / delete / has /  list
    """
    def __init__(self, scope: str):
        self.backends: dict[str, backend.NotImplementedSettings] = {
            'runtime': backend.RuntimeOnlySettings(),
        }
        self.scope = scope

    def get(self, what, default=None) -> ...:
        """
        Get the value `what` from current backend specified by `self.scope`,
        return `default` if the backend could not fulfill the request.
        """
        if self.scope not in self.backends.keys():
            raise NotImplementedError("Settings backend '{}' not supported.".format(self.scope))

        return self.backends[self.scope].get(what, default)

    def set(self, what, value) -> None:
        """
        Set the setting `what` with value `value` in `self.scope` backend.
        """
        if self.scope not in self.backends.keys():
            raise NotImplementedError("Settings backend '{}' not supported.".format(self.scope))

        return self.backends[self.scope].set(what, value)

    def delete(self, what) -> None:
        """
        Delete the value `what` from `self.scope` backend.
        """
        if self.scope not in self.backends.keys():
            raise NotImplementedError("Settings backend '{}' not supported.".format(self.scope))

        return self.backends[self.scope].delete(what)

    def list(self) -> list:
        """
        List settings' values contained in `self.scope` backend.
        """
        if self.scope not in self.backends.keys():
            raise NotImplementedError("Settings backend '{}' not supported.".format(self.scope))

        return self.backends[self.scope].list()

    def has(self, what) -> bool:
        """
        Return True if setting `what` can be found in `self.scope` backend,
        False otherwise.
        """
        if self.scope not in self.backends.keys():
            raise NotImplementedError("Settings backend '{}' not supported.".format(self.scope))

        return self.backends[self.scope].has(what)


class Setting(object):
    def __init__(self, name, type_, scopes,
                 label=None, tooltip=None, default_value=None):
        """
        Class to hold a setting value
        TODO
        type_: int, str, unicode, bool, float, [str]|[unicode]|(str,)|(unicode,)
        scopes: str(), unicode(), tuple|list(unicode()), tuple|list(str())
        """
        super().__init__()
        self.name = name
        self.type_ = type_
        # Checking type validity
        if self.is_valid() is False:
            raise RuntimeError("Type {} is not supported as a setting.".format(repr(type_)))

        scopes = tuple((scopes,)) if type(scopes) not in (list, tuple) else tuple(scopes)

        self.scopes = scopes
        self.label = label
        self.tooltip = "Scope(s) {}\n{}".format(self.scopes, tooltip)
        self.default_value = default_value
        self.ui = getattr(data_type, self.type_).UI(name, self.default_value)
        if self.tooltip:
            self.ui.setToolTip(self.tooltip)

    def is_valid(self) -> bool:
        """
        Return True if `self.type_` is a valid type description, False otherwise.
        """
        import os
        return self.type_ in [
            ".".join(i.split(".")[0:-1]) for i in os.listdir(
                os.path.realpath(os.path.dirname(data_type.__file__))
            )
            if i.endswith('.py')
        ]

    def value(self) -> ...:
        return self.ui.value()

    def setValue(self, value: ...):
        """
        TODO
        """
        self.ui.setValue(value)


class SettingsHandler(QObject):

    settingsAdded = QtCore.Signal()
    settingsUpdated = QtCore.Signal(dict)

    def __init__(self, tool_widget, domain_name=None,
                 save_slot=None, load_slot=None, items=None):
        """
        TODO
        `tool_widget`, points to a qui.ui.widget.ToolWidget object.
        """
        super().__init__()
        self.domain = domain_name if domain_name else tool_widget.__class__.__name__
        self.items = []
        if save_slot:
            self.save = save_slot

        if load_slot:
            self.load = load_slot

        self.settingsUpdated.connect(self.save)
        if hasattr(tool_widget, 'showSettingsBtnSlot'):
            # Coupling here.
            self.settingsAdded.connect(tool_widget.showSettingsBtnSlot)

        if items:
            for i in items:
                self += i

    def values(self, scope=None) -> dict:
        return {
            i: i.value()
            for i in self.items
            if scope is None or scope in i.scopes
        }

    def keys(self):
        return [i.name for i in self.items]

    def __getitem__(self, key):
        for i in self.items:
            if i.name == key:
                return i

        raise KeyError(key)

    def __iter__(self):
        return iter(self.items)

    def scoped_dict(self):
        """
        Return a dict with scopes' elements as keys and the self.domain as
        content for each scope.
        Useful to have a copy of all the settings in one struct before updating them.
        """
        scoped_dict = {}
        for setting in self.items:
            for scope in setting.scopes:
                if scope not in scoped_dict:
                    scoped_dict[scope] = {}

                scoped_dict[scope][setting.name] = setting.value()

        return scoped_dict

    def add_setting(self, name, type_, scopes, default_value=None,
                    label=None, tooltip=None):

        s = Setting(name, type_, scopes, label, tooltip, default_value)
        self += s

    def __add__(self, other):  # To be able to write settings += Setting(...)
        if type(other) is not Setting:
            raise NotImplemented

        other.ui.settingsUpdated.connect(self.settingsUpdated)
        self.items.append(other)
        self.settingsAdded.emit()
        return self

    def load(self):
        """
        Default implementation to set the initial's values to self.items.
        """
        raise NotImplementedError
        # Example:
        # scoped_dict = self.settings.scoped_dict()
        # usr_settings = ToolSettings('usr').get(self.settings.domain, {})
        # scoped_dict.get('usr', {}).update(usr_settings)
        # for i in self.settings:
        #     if 'usr' in i.scopes:
        #         i.setValue(scoped_dict.get('usr', {}).get(i.name, i.default_value))

    def save(self, settings_update=None):
        raise NotImplementedError
        # Example:
        # settings = ToolSettings('usr').get(self.settings.domain, {})
        # settings.update(settings_update)
        # ToolSettings('usr').set(self.settings.domain, settings)
