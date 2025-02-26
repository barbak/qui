"""
    Ui/Window/Widget Mansgement utilities.
"""
from PySide6 import QtCore
from PySide6.QtCore import (
    QEventLoop,
    QPoint,
)

from PySide6.QtWidgets import (
    QApplication,
    QSplashScreen,
)

def choose_screen():
    """
    Return the screen id choosed by the user by clicking on the corresponding
    sunshine (:ambientLight.svg)
    """
    class MaSplashScrin(QSplashScreen):
        screenChoosed = QtCore.Signal(int)

        def __init__(self, pix, number):
            super(self.__class__, self).__init__(pix)
            self.number = number

        def mousePressEvent(self, event):
            self.screenChoosed.emit(self.number)
            super(self.__class__, self).mousePressEvent(event)

    desktop = QApplication.desktop()
    el = QEventLoop()
    el.keeper = []  # gc preventer
    for i in range(desktop.screenCount()):
        s = MaSplashScrin(":ambientLight.svg", i)
        g = desktop.screenGeometry(i)
        s.showMessage("Screen #{}".format(i))
        s.move(g.center() - QPoint(*s.size().toTuple()) / 2.0)
        s.screenChoosed.connect(el.exit)
        s.show()
        el.keeper.append(s)

    return el.exec_()
