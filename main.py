# main.py
import os
import sys

from PySide6 import QtGui, QtWidgets

from main_window import MainWindow

basedir = os.path.dirname(__file__)
try:
    from ctypes import windll  # Only exists on Windows.

    myappid = "mycompany.myproduct.subproduct.version"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(os.path.join(basedir, "logo.ico")))
    win = MainWindow()
    win.show()
    app.exec()


if __name__ == "__main__":
    main()
