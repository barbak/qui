"""
    QIcon provider for Qt.
    When adding icon file, do not forget to update the README.md in the icons
    directory.
"""
import os

from PySide6.QtGui import (
    QColor,
    QIcon,
    QPainter,
    QPixmap,
)

icon_dict = {}


def get(icon_name, pixmap=False, size=None, color=None, path=False):
    """
    Return the QIcon associated with `icon_name` present in the icons directory,
    or the Qt resource if `icon_name` starts with ':'.
    If `pixmap` is True a QPixmap from the same file is returned instead.
    The pixmap size can be specified with `size` arg as
    a tuple(int(width), int(height)).
    The icon can be repaint in a color `color` represented as
    a tuple(int(R8), int(G8), int(B8)).
    If `path` is True, the function return the path of the icon on disk.
    Note: The color will repaint any area that as no transparency.
    """
    global icon_dict

    icon_key = f'{icon_name}{pixmap}{size}{color}' # Dirty but it works
    if icon_key in icon_dict and path is False:
        return icon_dict[icon_key]

    resolved_filename = icon_name
    if not icon_name.startswith(":"):
        icon_directory = os.path.realpath(os.path.join(os.path.dirname(__file__), 'icons'))
        if os.path.exists(os.path.join(icon_directory, icon_name)) is False:
            raise ValueError("Cannot found icon associated with {} file."
                             .format(repr(icon_name)))

        resolved_filename = os.path.join(icon_directory, icon_name)
        if path is True:
            return os.path.realpath(resolved_filename)

    else:
        raise NotImplementedError()

    _pixmap = QPixmap(resolved_filename)
    if color is not None:
        color = QColor(*color)
        p = QPainter(_pixmap)
        p.setCompositionMode(QPainter.CompositionMode_SourceIn)
        p.fillRect(_pixmap.rect(), color)
        p.end()

    icon = QIcon(_pixmap)
    if pixmap is True:
        ret = _pixmap if size is None else icon.pixmap(size[0], size[1])
        icon_dict[icon_key] = ret
        return ret

    icon_dict[icon_key] = icon
    return icon
