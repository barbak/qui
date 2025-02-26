"""
    QGroupBoxes related implementations.
"""
from copy import deepcopy

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLineEdit,
)


class StatusGroupBox(QGroupBox):
    """
    TODO
        'var' attribute type
          where descriptor value can handle
            (
                (int(int_value), "My Label for the int"),
                (float(float_value), "My Label for the float"),
                (str(string_value), "My label for this string"),
            )
        AtributeType acceptable should be all things that can be json serializable.

    Fixme Finsish this
    Create a GroupBox allowing to set different attributes that can be setted
    from the UI.

    All these values are retrieved by calling the `self.desc_dict` method.

    Attributes are describes as a list of tuples, in which each tuple is of
    the form:
      ('attributename_attributeType', descriptor_value)

    `attributeType` is in ['str', 'bool']
    `descriptor_value` depends of attribute type:

    Bool case
    If attribute type is 'bool', the descriptor must provide list of tuples such as:
        ((bool(True|False), str(label)), ...)

    This will generate a combobox in which items are the list of all str(label)
    found in the descriptor value. The first boolean value is used to populate
    the desc_dict when requested.

    Str case

    TODO

    Usage:
    class MyStatusGroupBox(ProductionStatusGroupBox):
        def __init__(self):

            # First, describe your attributes
            attrs = (
                ('work_level_str', ['PH', 'P1', 'P2']),
                ('is_mandatory_bool', ((False, 'No'), (True, 'Yes'))),
                ('comments_str', str()),
                # ...
            )

            # Second, call the ancestor's __init__ function
            # You can set a prefix to all of your attributes by specifying
            # the strip prefix that will be prepended on all of your
            # attribute names in the desc_dict.
            super(ModelingStatusGroupBox, self).__init__(
                setting_prefix='character_', desc_dict=attrs
            )

            # Third (optional), put a title to the group box.
            self.setTitle('Group Box Title')

            # Fourth (optional), do whatever you need to.
    """

    @staticmethod
    def __beautify_attr_name(name):
        return " ".join(
            [t.capitalize() for t in name.split('_')[0:-1]]
        )

    def __init__(self, setting_prefix, desc_dict, parent=None):
        """
        Fixme when python 3
        /!\ desc_dict should be an ordered dict
        so for the moment its a tuple of pairs.
        """
        super(StatusGroupBox, self).__init__(parent=parent)
        self.setting_prefix = setting_prefix

        self.attrs = deepcopy(desc_dict)

        self.widgets = []
        layout = QFormLayout()
        for k, v in desc_dict: # desc_dict.items()
            widget = None
            if k.endswith('_str') and type(v) in [list, tuple]:
                widget = QComboBox()
                widget.addItems(v)

            if k.endswith('_str') and type(v) in [unicode, str]:
                widget = QLineEdit()
                widget.setText(v)

            if k.endswith('_bool') and type(v) in [list, tuple]:
                widget = QComboBox()
                widget.addItems([i[1] for i in v])

            if widget is None:
                raise RuntimeError("Cannot compute something ...", k)

            layout.addRow(self.__beautify_attr_name(k), widget)
            self.widgets.append((k, widget))

        self.setLayout(layout)

    def desc_dict(self, strip_prefix=True):
        # if self.isCheckable() is True and self.isChecked() is False:
        #     return {}
        final_attr = lambda x: "{}{}".format(
            "" if strip_prefix is True else self.setting_prefix,
            x
        )
        d = {}
        for idx, t in enumerate(self.widgets):
            k, w = t
            if type(w) is QComboBox and k.endswith("_bool"):
                v = w.currentText()
                for i in self.attrs[idx][1]:
                    if v == i[1]:
                        d[final_attr(k)] = i[0]
                        break

            elif type(w) is QComboBox:
                d[final_attr(k)] = w.currentText()

            elif type(w) is QLineEdit:
                d[final_attr(k)] = w.text()

        return d

    @property
    def attr_names(self):
        """
        Return the list of attribute names from `self.attrs`.
        """
        return ["{}{}".format(self.setting_prefix, t[0]) for t in self.attrs]

    def get_attr_valid_values(self, attr_name):
        """
        Return valid values for attribute named `attr_name`.
        """
        if attr_name not in self.attr_names:
            raise RuntimeError("Attribute {} is invalid.".format(repr(attr_name)))

        for k, v in self.attrs:
            if "{}{}".format(self.setting_prefix, k) == attr_name:
                return v

        raise RuntimeError("Should be unreachable.")

    def reset_to_default_values(self):
        """
        Put all the widgets in self.widgets to their default state.
        QComboBoxes' current index set to 0.
        QLineEdit's text string set to ''.
        """
        for _,w in self.widgets:
            if type(w) is QComboBox:
                w.setCurrentIndex(0)

            elif type(w) is QLineEdit:
                w.setText('')

    def update_with(self, meta_dict):
        """
        Update UIs with datas from `meta_dict`.
        If `meta_dict` is {}, uis are resetted to default value.
        """
        self.reset_to_default_values()
        for k in [k for k in meta_dict if k.startswith(self.setting_prefix)]:
            if k in self.attr_names:
                w = self.attr_widget(k)
                if type(w) == QComboBox and k.endswith('_bool'):
                    w.setCurrentText(
                        self.convert_bool_to_str(k, meta_dict[k])
                    )

                elif type(w) == QComboBox and k.endswith('_str'):
                    w.setCurrentText(meta_dict[k])

                elif type(w) == QLineEdit:
                    w.setText(meta_dict[k])

                else:
                    raise RuntimeError(
                        "Attribute {} associated with a {} is not handeld."
                            .format(repr(k), type(w))
                    )

    def convert_bool_to_str(self, attr_name, attr_value):
        """
        Return a display text string associated to the boolean attribute.
        """
        if attr_name not in self.attr_names:
            raise RuntimeError("Attribute {} is invalid.".format(repr(attr_name)))

        value_tuples = self.get_attr_valid_values(attr_name)
        for value, string in value_tuples:
            if value == attr_value:
                return string

        raise ValueError("Value {} not found in {}".format(
            repr(attr_value), repr(value_tuples),
        ))

    def attr_widget(self, attr_name):
        """
        Return the widget associated with `attr_name`, None otherwise.
        """
        if attr_name not in self.attr_names:
            return None

        return self.widgets[self.attr_names.index(attr_name)][1]


class ModelingStatusGroupBox(StatusGroupBox):
    def __init__(self, checkable=False):
        attrs = (
            ('model_level_str', ['PH', 'P1', 'P2']),
            ('texture_level_str', ['PH', 'P1', 'P2']),
            ('has_fx_bool', ((False, 'No'), (True, 'Yes'))),
            ('comments_str', str()),
        )
        super(ModelingStatusGroupBox, self).__init__(
            setting_prefix='character_', desc_dict=attrs
        )
        self.setTitle('Modeling Status')
        if checkable is True:
            self.setCheckable(True)
            self.setChecked(False)


class RiggingStatusGroupBox(StatusGroupBox):
    def __init__(self, checkable=False):
        attrs = (
            ('body_skin_level_str', ['PH', 'P1', 'P2']),
            ('face_skin_level_str', ['PH', 'P1', 'P2']),
            ('hair_skin_level_str', ['PH', 'P1', 'P2']),
            ('lod_level_str', ['None', 'PH', 'P1', 'P2']),
            ('has_bsp_bool', ((False, 'No'), (True, 'Yes'))),
            ('comments_str', str()),
        )
        super(RiggingStatusGroupBox, self).__init__(
            setting_prefix='setup_', desc_dict=attrs
        )
        self.setTitle('Rigging Status')
        if checkable is True:
            self.setCheckable(True)
            self.setChecked(False)
