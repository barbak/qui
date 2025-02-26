# QUi - Qt UI based framework for RADing some creation tools

## Repository For ARCHIVE

This repo exists just for archiving some not anymore maintained useful code.
Feel free to use it or any part of it for your projects.

## License

This project is licensed under the MIT License.
See the [LICENSE](./LICENSE) file
for the full license text.

## Contains
* Easy to use base widget with support for
    * Settings Management
        * Object oriented declaration and usage with the `Setting` and the `SettingsHandler` classes.
            ```python
            # TODO MORE FACTUAL EXAMPLE
            class Setting(object):
                def __init__(self, name, type_, scopes,
                        label=None, tooltip=None, default_value=None):
                """
                Class to hold a setting value
                TODO
                type_: int, str, unicode, bool, float, [str]|[unicode]|(str,)|(unicode,)
                scopes: str(), unicode(), tuple|list(unicode()), tuple|list(str())
                """
                ...
            ```
            ```python
            # TODO MORE FACTUAL EXAMPLE
            class SettingsHandler(QObject):
                def add_setting(self, name, type_, scopes, default_value=None,
                    label=None, tooltip=None):
                    ...
            ```
        * Load / Save / User Interface
    * Set a documentation url by setting the widget `doc_url` property to whatever you want to point to,
      the `ToolWidget` class will add a button opening a browser on the provided url in its graphical interface.
        ```python
        from qui.ui.widget import ToolWidget
        class MehToolWidget(ToolWidget):
            def __init__(self):
                super().__init__()
                self.doc_url = "https://fett263.com"
        ```

    * Close / Dynamic Refresh Buttons

* Perforce API that support the reuse of connection within a with statements.
    ```python
    def first_function(*args, p4_adapter=None, env=None, **kwargs):
        with server.connect(env=env, p4_adapter=p4_adapter) as p4_adapter:
            # You can pass the p4_adapter to another function using a with statement
            # to reuse the connection to the perforce server.
            second_function(*args, env=env, p4_adapter=p4_adapter, **kwargs)


    def second_function(*args, p4_adapter=None, env=None, **kwargs):
        with server.connect(env=env, p4_adapter=p4_adapter) as p4_adapter:
            # You can modulate the exception level of the API
            # using a with statement as below.
            with p4_adapter.at_exception_level(P4.RAISE_NONE):
                p4_adapter.run('whatever')
            # Here the exception_level returns to whatever the
            # p4_adapter was at the beginnning of the function


    from qui.vcs import perforce

    with perforce.server.connect() as p4:
        first_function(p4_adapter=p4)
    ```


* Settings System that can help to manage different scope of settings.
    * Example: Studio / Project / User scopes can specify any setting value and the developper can resolve this as he intended.
    (That's why there is no default implementation of the load_settings and save_settings slots for the moment)

## History

It is based on a primitive toolset used in a video game studio to make tools inside Maya 2018.

It has been cleaned of all the maya specific and basically ported to python 3.