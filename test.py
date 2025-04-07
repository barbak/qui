#!/usr/bin/env python3
import os
import sys
from qui.ui.widget import ToolWidget
from qui.settings import (
    backend,
    Setting,
    SettingsHandler,
    ToolSettings,
)
import unreal_stylesheet

from PySide6.QtWidgets import *


class MehToolSettings(ToolSettings):
    def __init__(self, scope):
        super().__init__(scope)
        self.backends.update({
            'prj': backend.JSONReadOnlySettings(
                os.path.join(
                    os.environ.get("TEST_PROJECT_PATH", "."),
                    "Config", "Pipeline", "pipeline.json"
                )
            ),
            'usr': backend.JSONReadWriteSettings(
                os.path.join(".", "usr_settings.json")
            ),
        })

    # def __getattr__(self, item):
    #     if hasattr(self.backends[self.scope], item) is True:
    #         return getattr(self.backends[self.scope], item)

    #     raise AttributeError(
    #         "Scope {} has no attribute {}".format(repr(self.scope), repr(item))
    #     )


class MehToolWidget(ToolWidget):
    def __init__(self):
        super().__init__()
        self.doc_url = "https://fett263.com"
        self.settings_handler = SettingsHandler(
            self,
            save_slot=self.save_settings_slot,
            load_slot=self.load_settings_slot,
        )
        settings = [
            Setting(
                'my_boolean', 'boolean', 'usr',
                label="My Boolean",
                default_value=False,
                tooltip= "MY BOOLEAN EXAMPLE",
            ),
            Setting(
                'my_combo_box', 'combo_box', 'usr',
                label="My Combo Box",
                default_value=0, # index
                tooltip="MY COMBO BOX EXAMPLE",
            ),
            Setting(
                'my_filename', 'filename', 'usr',
                label="My Filename",
                tooltip="MY FILENAME EXAMPLE",
                default_value="DEFAULT MY FILENAME VALUE",
            ),
            Setting(
                'my_integer', 'integer', 'usr',
                label="My Integer",
                default_value=0,
                tooltip= "The button color when the button is disabled.",
            ),
            Setting(
                'my_rgb_color', 'rgb_color', 'usr',
                label="My RGB Color",
                default_value='Gray',
                tooltip= "MY RGB COLOR EXAMPLE",
            ),
            Setting(
                'my_string_line_array', 'string_line_array', 'lcl',
                label="My String Line Array",
                default_value=["DEFAULT STRING LINE ARRAY VALUE",  "AND ANOTHER LINE"],
                tooltip=(
                    "MY STRING ARRAY EXAMPLE\n"
                    "(One directory per line)"
                )
            ),
        ]
        [self.settings_handler + s for s in settings]
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("My Awesome Tool !!!!"))

    def load_settings_slot(self):
        """
        Default implementation to set the initial's values to self.items.
        """
        # raise NotImplementedError
        # Example:
        scoped_dict = self.settings_handler.scoped_dict()
        usr_settings = MehToolSettings('usr').get(self.settings_handler.domain, {})
        scoped_dict.get('usr', {}).update(usr_settings)
        for i in self.settings_handler:
            if 'usr' in i.scopes:
                i.setValue(scoped_dict.get('usr', {}).get(i.name, i.default_value))

    def save_settings_slot(self, settings_update=None):
        # raise NotImplementedError
        # Example:
        settings = MehToolSettings('usr').get(self.settings_handler.domain, {})
        settings.update(settings_update)
        MehToolSettings('usr').set(self.settings_handler.domain, settings)


def main(argv):
    app = QApplication(argv)
    # unreal_stylesheet.setup(app)
    tool_widget = MehToolWidget()
    tool_widget.setWindowTitle("Test Using QUi package")
    tool_widget.resize(640, 480)
    tool_widget.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main(sys.argv))