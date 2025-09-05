# main.py
from PySide6.QtWidgets import QApplication

from main_window import MainWindow


# ------------------------------
# Entry
# ------------------------------
def main():
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exec()


if __name__ == "__main__":
    main()
