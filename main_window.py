# main_window.py
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QGuiApplication
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStyle,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from dialogs import AddKeyDialog
from key_manager import KeyManager
from models import (
    ActivationKeysModel,
    AnyColumnFilterProxy,
    COL_ACTIONS,
    COL_ID,
    COL_NAME,
)


class MainWindow(QMainWindow):
    PRIMARY = "#1976D2"
    HEADER_BG = "#E3F2FD"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trình Quản Lý Khóa")
        self.resize(1000, 640)

        self.manager = KeyManager()

        # Top-level widgets
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        # Header
        header = QWidget()
        header.setStyleSheet(f"background:{self.HEADER_BG}; border-radius:8px;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)

        title_box = QVBoxLayout()
        self.title_label = QLabel("Trình Quản Lý Khóa Kích Hoạt")
        self.title_label.setStyleSheet("font-size:22px; font-weight:600;")
        self.count_label = QLabel()
        self.count_label.setStyleSheet("color:#555;")
        title_box.addWidget(self.title_label)
        title_box.addWidget(self.count_label)

        header_layout.addLayout(title_box)
        header_layout.addStretch()

        self.add_btn = QPushButton("Thêm Khóa Mới")
        self.add_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogYesButton))
        self.add_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {self.PRIMARY}; color: white; padding: 8px 14px;
                border: none; border-radius: 6px; font-weight: 600;
            }}
            """
        )
        self.add_btn.clicked.connect(self.add_key)
        header_layout.addWidget(self.add_btn)
        root.addWidget(header)

        # Search
        search_row = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Tìm kiếm khóa...")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.textChanged.connect(self.on_search)
        search_row.addWidget(self.search_edit)
        root.addLayout(search_row)

        # Table
        self.table = QTableView()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setEditTriggers(QTableView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        root.addWidget(self.table, 1)

        # Model / Proxy
        self.model = ActivationKeysModel(self.manager.load_keys())
        self.proxy = AnyColumnFilterProxy()
        self.proxy.setSourceModel(self.model)
        self.table.setModel(self.proxy)

        # Hide ID column in the view
        self.table.setColumnHidden(
            self.proxy.mapFromSource(self.model.index(0, COL_ID)).column(), True
        )

        # Set fixed width for Actions column
        self.table.setColumnWidth(COL_ACTIONS, 160)

        # Rebuild action widgets whenever the model changes layout/reset
        self.proxy.layoutChanged.connect(self.rebuild_action_widgets)
        self.proxy.modelReset.connect(self.rebuild_action_widgets)

        # Initial UI state
        self.update_count_label()
        self.rebuild_action_widgets()

        # Menu shortcuts (optional)
        act_add = QAction("Thêm", self)
        act_add.setShortcut("Ctrl+N")
        act_add.triggered.connect(self.add_key)
        self.addAction(act_add)

        act_quit = QAction("Thoát", self)
        act_quit.setShortcut("Ctrl+Q")
        act_quit.triggered.connect(self.close)
        self.addAction(act_quit)

        # Light styling for table selection
        self.table.setStyleSheet(
            """
            QTableView::item:selected { background: #D7E7FF; color: black; }
        """
        )

    # --------- Utilities ----------
    def map_proxy_row_to_source_row(self, proxy_row: int) -> int:
        src_idx = self.proxy.mapToSource(self.proxy.index(proxy_row, COL_NAME))
        return src_idx.row()

    def get_row_data_by_proxy_row(self, proxy_row: int) -> dict:
        src_row = self.map_proxy_row_to_source_row(proxy_row)
        return self.model.rows[src_row]

    def update_count_label(self):
        self.count_label.setText(f"Tổng Số Khóa: {self.model.rowCount()}")

    # --------- Buttons in the Actions column ----------
    def rebuild_action_widgets(self):
        # Clear any previous widgets and rebuild for all rows
        actions_col = COL_ACTIONS
        for r in range(self.proxy.rowCount()):
            idx = self.proxy.index(r, actions_col)
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(6)

            copy_btn = QPushButton("Sao Chép")
            copy_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
            copy_btn.setCursor(Qt.PointingHandCursor)
            copy_btn.clicked.connect(lambda _=False, row=r: self.on_copy_clicked(row))

            del_btn = QPushButton("Xóa")
            del_btn.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.setStyleSheet("QPushButton {color:#C62828;}")
            del_btn.clicked.connect(lambda _=False, row=r: self.on_delete_clicked(row))

            layout.addStretch()
            layout.addWidget(copy_btn)
            layout.addWidget(del_btn)
            layout.addStretch()
            self.table.setIndexWidget(idx, container)

    # --------- Slots ----------
    def on_search(self, text: str):
        self.proxy.setFilterText(text)
        # Buttons need to be rebuilt because rows/indices changed
        self.rebuild_action_widgets()

    def add_key(self):
        dlg = AddKeyDialog(self)
        if dlg.exec() == QDialog.Accepted:
            try:
                name, secret, ttl, days = dlg.values()
                self.manager.add_key_row(name, secret, ttl, days)
                self.model.set_rows(self.manager.load_keys())
                self.update_count_label()
                self.rebuild_action_widgets()
                QMessageBox.information(self, "Thành Công", "Đã thêm khóa thành công!")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def on_copy_clicked(self, proxy_row: int):
        # Map proxy row to source → get full key
        try:
            data = self.get_row_data_by_proxy_row(proxy_row)
        except Exception:
            # Rows might have shifted; rebuild and ignore
            self.rebuild_action_widgets()
            return
        key_full = data["key"]
        QGuiApplication.clipboard().setText(key_full)
        QMessageBox.information(self, "Đã Sao Chép", "Đã sao chép khóa vào clipboard!")

    def on_delete_clicked(self, proxy_row: int):
        try:
            data = self.get_row_data_by_proxy_row(proxy_row)
        except Exception:
            self.rebuild_action_widgets()
            return

        key_id = data["id"]
        confirm = QMessageBox.question(
            self,
            "Xóa Khóa",
            "Bạn có chắc chắn muốn xóa khóa này?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            self.manager.delete_key(key_id)
            self.model.set_rows(self.manager.load_keys())
            self.update_count_label()
            self.rebuild_action_widgets()
            # Use information message to mimic your original "negative" notify color meaning deletion happened
            QMessageBox.information(self, "Đã Xóa", "Đã xóa khóa thành công.")

    def closeEvent(self, event):
        self.manager.close()
        super().closeEvent(event)