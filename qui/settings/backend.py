"""
    Backends implementations for ToolSettings.
"""

import json
import os
import sys


class NotImplementedSettings(object):
    """
    Filler raising exception on usage.
    Implements: get / set / delete / has / list
    """

    def get(self, what, default=None) -> ...:
        """
        Get the value `what` from current backend specified by `self.scope`,
        return `default` if the backend could not fulfill the request.
        """
        raise NotImplementedError

    def set(self, what, value) -> None:
        """
        Set the setting `what` with value `value` in `self.scope` backend.
        """
        raise NotImplementedError

    def delete(self, what) -> None:
        """
        Delete the value `what` from `self.scope` backend.
        """
        raise NotImplementedError

    def list(self) -> list:
        """
        List setting' values contained in `self.scope` backend.
        """
        raise NotImplementedError

    def has(self, what) -> bool:
        """
        Return True if setting `what` can be found in `self` backend,
        False otherwise.
        """
        raise NotImplementedError


class JSONReadOnlySettings(NotImplementedSettings):
    """
    Implements: get / has / list
    """
    def __init__(self, json_filename):
        super().__init__()
        self.__json_filename = json_filename

    @property
    def json_filename(self):
        return os.path.realpath(self.__json_filename)

    def _get_dict_from_json(self):
        if self.json_filename is None:
            return {}

        with open(self.json_filename) as f:
            return json.load(f)

        return {}

    def get(self, what, default=None) -> ...:
        ret = default
        try:
            ret = self._get_dict_from_json()[what]

        except Exception as e:
            print(f'WRN - Cannot get {repr(what)} from json file settings. ({repr(e)})')

        finally:
            return ret

    def has(self, what) -> bool:
        return what in self._get_dict_from_json()

    def list(self) -> list:
        return list(self._get_dict_from_json().keys())


class JSONReadWriteSettings(NotImplementedSettings):
    """
    Implements: get / set / delete / has / list
    """
    def __init__(self, json_filename):
        super().__init__()
        self.__json_filename = json_filename

    @property
    def json_filename(self) -> str:
        return os.path.realpath(self.__json_filename)

    @property
    def __settings_dict(self) -> dict:
        if os.path.exists(self.json_filename):
            with open(self.json_filename) as f:
                file_content = f.read()
                if file_content == '':
                    print('WRN - Settings file exists but is empty. '
                          '({})'.format(repr(self.json_filename)))
                    settings_dict = {}

                else:
                    settings_dict = json.loads(file_content)

        else:
            settings_dict = {}

        return settings_dict

    def get(self, what, default=None) -> ...:
        """
        Return the setting named `what`, return `default` if it
        does not exists.
        """
        if what not in self.list():
            # TODO A real logger.
            print("WRN - No entry found for {} !".format(repr(what)))

        return self.__settings_dict.get(what, default)

    def set(self, what, value) -> None:
        """
        Set the User Setting `what` with value `value`.
        `value` must be a json serializable entity.
        """
        settings_dict = self.__settings_dict
        settings_dict[what] = value
        with open(self.json_filename, 'w') as f:
            f.write(json.dumps(settings_dict,
                               indent=2, separators=(',', ': '),
                               sort_keys=True))

    def delete(self, what) -> None:
        """
        Delete the `what` entry in User Settings.
        """
        settings_dict = self.__settings_dict
        if what not in settings_dict:
            raise KeyError("Cannot find '{}' in User Settings.".format(what))

        settings_dict.pop(what)
        with open(self.json_filename, 'w') as f:
            f.write(json.dumps(settings_dict,
                               indent=2, separators=(',', ': '),
                               sort_keys=True))

    def has(self, what) -> bool:
        """
        Return True if `what` in User Setting list, False otherwise.
        """
        return what in self.list()

    def list(self) -> list:
        """
        Return the list of settings' name available in the DCC area.
        """
        return list(self.__settings_dict.keys())


class RuntimeOnlySettings(NotImplementedSettings):
    """
    For settings persisted only during the runtime of the python interpreter.
    """

    __settings = {}

    def get(self, what, default=None) -> ...:
        return RuntimeOnlySettings.__settings.get(what, default)

    def set(self, what, value) -> None:
        RuntimeOnlySettings.__settings[what] = value

    def delete(self, what)  -> None:
        del RuntimeOnlySettings.__settings[what]

    def has(self, what) -> bool:
        return what in RuntimeOnlySettings.__settings

    def list(self) -> list:
        return list(RuntimeOnlySettings.__settings.keys())
