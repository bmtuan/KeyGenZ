# models.py
from datetime import datetime

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt


# Column constants
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
        # Color the date cells based on expiry with better visual indicators
        if role == Qt.ForegroundRole and (col in (COL_ACTIVATE_EXP, COL_APP_EXP)):
            text = self.data(self.index(index.row(), col), Qt.DisplayRole)
            try:
                dt = datetime.strptime(text, "%Y-%m-%d %H:%M:%S")
                now = datetime.now()
                if dt < now:
                    return Qt.red  # Expired
                elif (dt - now).days <= 7:
                    return Qt.darkYellow  # Expiring soon (within 7 days)
                else:
                    return Qt.darkGreen  # Valid
            except Exception:
                return None
        
        # Add background color for expired rows
        if role == Qt.BackgroundRole:
            row_data = self.rows[index.row()]
            try:
                activate_exp = datetime.strptime(row_data["activate_expired_date"], "%Y-%m-%d %H:%M:%S")
                app_exp = datetime.strptime(row_data["app_expired_date"], "%Y-%m-%d %H:%M:%S")
                now = datetime.now()
                if activate_exp < now or app_exp < now:
                    return Qt.lightGray  # Light gray background for expired keys
            except Exception:
                pass
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