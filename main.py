# key_manager_pyside6.py
import base64
import hashlib
import hmac
import sqlite3
import time
import uuid
from datetime import datetime, timedelta

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PySide6.QtGui import QAction, QGuiApplication, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
)
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QLineEdit as PLineEdit
from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStyle,
    QStyledItemDelegate,
    QTableView,
    QVBoxLayout,
    QWidget,
)


# ------------------------------
# Data / Storage
# ------------------------------
class KeyManager:
    def __init__(self, db_path="activation_keys.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_table()

    def create_table(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS activation_keys (
                id TEXT PRIMARY KEY,
                name TEXT,
                key TEXT UNIQUE,
                created_date TEXT,
                activate_expired_date TEXT,
                app_expired_date TEXT
            )
        """
        )
        self.conn.commit()

    def load_keys(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM activation_keys ORDER BY created_date DESC")
        return [dict(row) for row in cur.fetchall()]

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass

    @staticmethod
    def generate_key(secret_key: str, ttl_seconds: int, ttl_seconds_app: int) -> str:
        """
        Generate a key using a secret key, TTL, and app-specific TTL.
        """
        current_time = int(time.time())
        expiration_time = current_time + int(ttl_seconds)
        app_expiration_time = current_time + int(ttl_seconds_app)
        data = f"{current_time}:{expiration_time}:{app_expiration_time}"
        signature = hmac.new(
            secret_key.encode(), data.encode(), hashlib.sha256
        ).digest()

        encoded_data = base64.urlsafe_b64encode(data.encode()).decode()
        encoded_signature = base64.urlsafe_b64encode(signature).decode()
        return f"{encoded_data}:{encoded_signature}"

    def add_key_row(
        self, name: str, secret_key: str, ttl_seconds: int, validity_days: int
    ):
        if not name.strip() or not secret_key.strip():
            raise ValueError("All fields are required.")

        ttl_app_seconds = int(validity_days) * 24 * 60 * 60
        new_key = self.generate_key(secret_key, int(ttl_seconds), ttl_app_seconds)

        now = datetime.now()
        created_date = now.strftime("%Y-%m-%d %H:%M:%S")
        activate_expired_date = (now + timedelta(seconds=int(ttl_seconds))).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        app_expired_date = (now + timedelta(seconds=ttl_app_seconds)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        cur = self.conn.cursor()
        cur.execute(
            """INSERT INTO activation_keys
               (id, name, key, created_date, activate_expired_date, app_expired_date)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                str(uuid.uuid4()),
                name.strip(),
                new_key,
                created_date,
                activate_expired_date,
                app_expired_date,
            ),
        )
        self.conn.commit()

    def delete_key(self, key_id: str):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM activation_keys WHERE id = ?", (key_id,))
        self.conn.commit()


# ------------------------------
# Table Model
# ------------------------------
COL_ID = 0
COL_NAME = 1
COL_KEY_PREVIEW = 2
COL_CREATED = 3
COL_ACTIVATE_EXP = 4
COL_APP_EXP = 5
COL_ACTIONS = 6

HEADERS = [
    "ID (hidden)",
    "Name",
    "Key",
    "Created Date",
    "Activate Expired Date",
    "App Expired Date",
    "Actions",
]


class ActivationKeysModel(QAbstractTableModel):
    def __init__(self, rows: list[dict]):
        super().__init__()
        self.rows = rows or []

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.rows)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(HEADERS)

    def headerData(
        self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole
    ):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return HEADERS[section]
        return section + 1

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        row = self.rows[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == COL_ID:
                return row["id"]
            elif col == COL_NAME:
                return row["name"]
            elif col == COL_KEY_PREVIEW:
                key = row["key"]
                return (key[:20] + "...") if key and len(key) > 23 else key
            elif col == COL_CREATED:
                return row["created_date"]
            elif col == COL_ACTIVATE_EXP:
                return row["activate_expired_date"]
            elif col == COL_APP_EXP:
                return row["app_expired_date"]
            elif col == COL_ACTIONS:
                return ""  # buttons live here via setIndexWidget
        # Color the date cells based on expiry
        if role == Qt.ForegroundRole and (col in (COL_ACTIVATE_EXP, COL_APP_EXP)):
            text = self.data(self.index(index.row(), col), Qt.DisplayRole)
            try:
                dt = datetime.strptime(text, "%Y-%m-%d %H:%M:%S")
                return Qt.red if dt < datetime.now() else Qt.darkGreen
            except Exception:
                return None
        return None

    # Helpers for retrieving the full values by source row
    def key_id_at(self, source_row: int) -> str:
        return self.rows[source_row]["id"]

    def key_full_at(self, source_row: int) -> str:
        return self.rows[source_row]["key"]

    def set_rows(self, rows: list[dict]):
        self.beginResetModel()
        self.rows = rows or []
        self.endResetModel()


class AnyColumnFilterProxy(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self._text = ""

    def setFilterText(self, text: str):
        self._text = (text or "").lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        if not self._text:
            return True
        model: ActivationKeysModel = self.sourceModel()
        for col in range(model.columnCount()):
            # Skip actions col
            if col == COL_ACTIONS:
                continue
            idx = model.index(source_row, col, source_parent)
            val = model.data(idx, Qt.DisplayRole)
            if val and self._text in str(val).lower():
                return True
        return False


# ------------------------------
# Add Key Dialog
# ------------------------------
class AddKeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate New Key")
        self.setModal(True)

        self.name_edit = PLineEdit()
        self.secret_edit = PLineEdit()
        self.secret_edit.setText("031200006280")
        self.secret_edit.setEchoMode(PLineEdit.Password)

        self.ttl_spin = QSpinBox()
        self.ttl_spin.setRange(1, 2_147_483_647)
        self.ttl_spin.setValue(300)

        self.days_spin = QSpinBox()
        self.days_spin.setRange(1, 10_000)
        self.days_spin.setValue(30)

        form = QFormLayout()
        form.addRow("Name", self.name_edit)
        form.addRow("Secret Key", self.secret_edit)
        form.addRow("TTL (seconds)", self.ttl_spin)
        form.addRow("Validity Period (days)", self.days_spin)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(btns)

    def values(self):
        return (
            self.name_edit.text().strip(),
            self.secret_edit.text().strip(),
            int(self.ttl_spin.value()),
            int(self.days_spin.value()),
        )


# ------------------------------
# Main Window
# ------------------------------
class MainWindow(QMainWindow):
    PRIMARY = "#1976D2"
    HEADER_BG = "#E3F2FD"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Key Manager")
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
        self.title_label = QLabel("Activation Key Manager")
        self.title_label.setStyleSheet("font-size:22px; font-weight:600;")
        self.count_label = QLabel()
        self.count_label.setStyleSheet("color:#555;")
        title_box.addWidget(self.title_label)
        title_box.addWidget(self.count_label)

        header_layout.addLayout(title_box)
        header_layout.addStretch()

        self.add_btn = QPushButton("Add New Key")
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
        self.search_edit.setPlaceholderText("Search keys...")
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
        act_add = QAction("Add", self)
        act_add.setShortcut("Ctrl+N")
        act_add.triggered.connect(self.add_key)
        self.addAction(act_add)

        act_quit = QAction("Quit", self)
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
        self.count_label.setText(f"Total Keys: {self.model.rowCount()}")

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

            copy_btn = QPushButton("Copy")
            copy_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
            copy_btn.setCursor(Qt.PointingHandCursor)
            copy_btn.clicked.connect(lambda _=False, row=r: self.on_copy_clicked(row))

            del_btn = QPushButton("Delete")
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
                QMessageBox.information(self, "Success", "Key added successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

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
        QMessageBox.information(self, "Copied", "Key copied to clipboard!")

    def on_delete_clicked(self, proxy_row: int):
        try:
            data = self.get_row_data_by_proxy_row(proxy_row)
        except Exception:
            self.rebuild_action_widgets()
            return

        key_id = data["id"]
        confirm = QMessageBox.question(
            self,
            "Delete Key",
            "Are you sure you want to delete this key?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            self.manager.delete_key(key_id)
            self.model.set_rows(self.manager.load_keys())
            self.update_count_label()
            self.rebuild_action_widgets()
            # Use information message to mimic your original "negative" notify color meaning deletion happened
            QMessageBox.information(self, "Deleted", "Key deleted successfully.")

    def closeEvent(self, event):
        self.manager.close()
        super().closeEvent(event)


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
