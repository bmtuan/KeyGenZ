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
    # Modern color palette
    PRIMARY = "#6366F1"  # Indigo
    PRIMARY_HOVER = "#4F46E5"
    PRIMARY_LIGHT = "#EEF2FF"
    SUCCESS = "#10B981"  # Emerald
    DANGER = "#EF4444"   # Red
    WARNING = "#F59E0B"  # Amber
    SURFACE = "#FFFFFF"
    SURFACE_VARIANT = "#F8FAFC"
    BORDER = "#E2E8F0"
    TEXT_PRIMARY = "#1E293B"
    TEXT_SECONDARY = "#64748B"
    TEXT_MUTED = "#94A3B8"
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔑 Key Manager Pro")
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)

        self.manager = KeyManager()

        # Apply modern styling to the main window
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.SURFACE_VARIANT};
                color: {self.TEXT_PRIMARY};
            }}
        """)
        
        # Top-level widgets
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        # Header with modern design
        header = QWidget()
        header.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.SURFACE}, stop:1 {self.SURFACE_VARIANT});
                border: 1px solid {self.BORDER};
                border-radius: 12px;
                margin: 4px;
            }}
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 20, 24, 20)

        title_box = QVBoxLayout()
        self.title_label = QLabel("🔑 Activation Key Manager")
        self.title_label.setStyleSheet(f"""
            font-size: 28px; 
            font-weight: 700; 
            color: {self.TEXT_PRIMARY};
            margin-bottom: 4px;
        """)
        self.count_label = QLabel()
        self.count_label.setStyleSheet(f"""
            font-size: 14px; 
            color: {self.TEXT_SECONDARY};
            font-weight: 500;
        """)
        title_box.addWidget(self.title_label)
        title_box.addWidget(self.count_label)

        header_layout.addLayout(title_box)
        header_layout.addStretch()

        self.add_btn = QPushButton("➕ Add New Key")
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.PRIMARY}, stop:1 {self.PRIMARY_HOVER});
                color: white; 
                padding: 12px 24px;
                border: none; 
                border-radius: 8px; 
                font-weight: 600;
                font-size: 14px;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.PRIMARY_HOVER}, stop:1 {self.PRIMARY});
            }}
            QPushButton:pressed {{
                background: {self.PRIMARY_HOVER};
                padding-top: 13px;
                padding-bottom: 11px;
            }}
        """)
        self.add_btn.clicked.connect(self.add_key)
        header_layout.addWidget(self.add_btn)
        root.addWidget(header)

        # Search with modern styling
        search_row = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 Search keys by name, key, or date...")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.setStyleSheet(f"""
            QLineEdit {{
                background: {self.SURFACE};
                border: 2px solid {self.BORDER};
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                color: {self.TEXT_PRIMARY};
            }}
            QLineEdit:focus {{
                border-color: {self.PRIMARY};
                background: {self.SURFACE};
            }}
            QLineEdit::placeholder {{
                color: {self.TEXT_MUTED};
            }}
        """)
        self.search_edit.textChanged.connect(self.on_search)
        search_row.addWidget(self.search_edit)
        root.addLayout(search_row)

        # Table with modern styling
        self.table = QTableView()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setEditTriggers(QTableView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(f"""
            QTableView {{
                background: {self.SURFACE};
                border: 1px solid {self.BORDER};
                border-radius: 8px;
                gridline-color: {self.BORDER};
                selection-background-color: {self.PRIMARY_LIGHT};
                selection-color: {self.TEXT_PRIMARY};
                font-size: 13px;
            }}
            QTableView::item {{
                padding: 12px 8px;
                border-bottom: 1px solid {self.BORDER};
            }}
            QTableView::item:selected {{
                background: {self.PRIMARY_LIGHT};
                color: {self.TEXT_PRIMARY};
            }}
            QTableView::item:hover {{
                background: {self.SURFACE_VARIANT};
            }}
            QHeaderView::section {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.SURFACE_VARIANT}, stop:1 {self.BORDER});
                color: {self.TEXT_PRIMARY};
                padding: 12px 8px;
                border: none;
                border-right: 1px solid {self.BORDER};
                border-bottom: 2px solid {self.BORDER};
                font-weight: 600;
                font-size: 13px;
            }}
            QHeaderView::section:first {{
                border-top-left-radius: 8px;
            }}
            QHeaderView::section:last {{
                border-top-right-radius: 8px;
                border-right: none;
            }}
        """)
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

        # Status bar
        self.statusBar().showMessage("Ready")
        self.statusBar().setStyleSheet(f"""
            QStatusBar {{
                background: {self.SURFACE};
                border-top: 1px solid {self.BORDER};
                color: {self.TEXT_SECONDARY};
                font-size: 12px;
                padding: 4px;
            }}
        """)

        # Menu shortcuts (optional)
        act_add = QAction("Add", self)
        act_add.setShortcut("Ctrl+N")
        act_add.triggered.connect(self.add_key)
        self.addAction(act_add)

        act_quit = QAction("Quit", self)
        act_quit.setShortcut("Ctrl+Q")
        act_quit.triggered.connect(self.close)
        self.addAction(act_quit)
        
        # Search shortcut
        act_search = QAction("Search", self)
        act_search.setShortcut("Ctrl+F")
        act_search.triggered.connect(lambda: self.search_edit.setFocus())
        self.addAction(act_search)


    # --------- Utilities ----------
    def map_proxy_row_to_source_row(self, proxy_row: int) -> int:
        src_idx = self.proxy.mapToSource(self.proxy.index(proxy_row, COL_NAME))
        return src_idx.row()

    def get_row_data_by_proxy_row(self, proxy_row: int) -> dict:
        src_row = self.map_proxy_row_to_source_row(proxy_row)
        return self.model.rows[src_row]

    def update_count_label(self):
        count = self.model.rowCount()
        if count == 0:
            self.count_label.setText("No keys found")
        elif count == 1:
            self.count_label.setText("1 activation key")
        else:
            self.count_label.setText(f"{count} activation keys")

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

            copy_btn = QPushButton("📋 Copy")
            copy_btn.setCursor(Qt.PointingHandCursor)
            copy_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {self.SUCCESS};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-weight: 500;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background: #059669;
                }}
                QPushButton:pressed {{
                    background: #047857;
                }}
            """)
            copy_btn.clicked.connect(lambda _=False, row=r: self.on_copy_clicked(row))

            del_btn = QPushButton("🗑️ Delete")
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {self.DANGER};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-weight: 500;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background: #DC2626;
                }}
                QPushButton:pressed {{
                    background: #B91C1C;
                }}
            """)
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
        
        # Update status bar
        if text:
            filtered_count = self.proxy.rowCount()
            total_count = self.model.rowCount()
            if filtered_count == 0:
                self.statusBar().showMessage(f"No keys found matching '{text}'")
            else:
                self.statusBar().showMessage(f"Found {filtered_count} of {total_count} keys matching '{text}'")
        else:
            self.statusBar().showMessage("Ready")

    def add_key(self):
        dlg = AddKeyDialog(self)
        if dlg.exec() == QDialog.Accepted:
            try:
                name, secret, ttl, days = dlg.values()
                self.manager.add_key_row(name, secret, ttl, days)
                self.model.set_rows(self.manager.load_keys())
                self.update_count_label()
                self.rebuild_action_widgets()
                self.statusBar().showMessage(f"Key '{name}' added successfully")
                
                # Create a styled success message
                success_msg = QMessageBox(self)
                success_msg.setWindowTitle("✅ Success")
                success_msg.setText("Activation key created successfully!")
                success_msg.setInformativeText(f"Key '{name}' has been added to your collection.")
                success_msg.setIcon(QMessageBox.Information)
                success_msg.setStyleSheet(f"""
                    QMessageBox {{
                        background: {self.SURFACE};
                        color: {self.TEXT_PRIMARY};
                    }}
                    QMessageBox QPushButton {{
                        background: {self.SUCCESS};
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 16px;
                        font-weight: 600;
                        min-width: 80px;
                    }}
                    QMessageBox QPushButton:hover {{
                        background: #059669;
                    }}
                """)
                success_msg.exec()
            except Exception as e:
                # Create a styled error message
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle("❌ Error")
                error_msg.setText("Failed to create activation key!")
                error_msg.setInformativeText(str(e))
                error_msg.setIcon(QMessageBox.Critical)
                error_msg.setStyleSheet(f"""
                    QMessageBox {{
                        background: {self.SURFACE};
                        color: {self.TEXT_PRIMARY};
                    }}
                    QMessageBox QPushButton {{
                        background: {self.DANGER};
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 16px;
                        font-weight: 600;
                        min-width: 80px;
                    }}
                    QMessageBox QPushButton:hover {{
                        background: #DC2626;
                    }}
                """)
                error_msg.exec()

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
        self.statusBar().showMessage(f"Key '{data['name']}' copied to clipboard")
        
        # Create a styled success message
        msg = QMessageBox(self)
        msg.setWindowTitle("✅ Success")
        msg.setText("Activation key copied to clipboard!")
        msg.setInformativeText(f"Key: {data['name']}")
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background: {self.SURFACE};
                color: {self.TEXT_PRIMARY};
            }}
            QMessageBox QPushButton {{
                background: {self.SUCCESS};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background: #059669;
            }}
        """)
        msg.exec()

    def on_delete_clicked(self, proxy_row: int):
        try:
            data = self.get_row_data_by_proxy_row(proxy_row)
        except Exception:
            self.rebuild_action_widgets()
            return

        key_id = data["id"]
        key_name = data["name"]
        
        # Create a styled confirmation dialog
        confirm = QMessageBox(self)
        confirm.setWindowTitle("⚠️ Confirm Deletion")
        confirm.setText(f"Are you sure you want to delete this activation key?")
        confirm.setInformativeText(f"Key: {key_name}\n\nThis action cannot be undone.")
        confirm.setIcon(QMessageBox.Warning)
        confirm.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirm.setDefaultButton(QMessageBox.No)
        confirm.setStyleSheet(f"""
            QMessageBox {{
                background: {self.SURFACE};
                color: {self.TEXT_PRIMARY};
            }}
            QMessageBox QPushButton {{
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                min-width: 80px;
            }}
            QMessageBox QPushButton[text="Yes"] {{
                background: {self.DANGER};
                color: white;
            }}
            QMessageBox QPushButton[text="Yes"]:hover {{
                background: #DC2626;
            }}
            QMessageBox QPushButton[text="No"] {{
                background: {self.TEXT_MUTED};
                color: white;
            }}
            QMessageBox QPushButton[text="No"]:hover {{
                background: {self.TEXT_SECONDARY};
            }}
        """)
        
        if confirm.exec() == QMessageBox.Yes:
            self.manager.delete_key(key_id)
            self.model.set_rows(self.manager.load_keys())
            self.update_count_label()
            self.rebuild_action_widgets()
            self.statusBar().showMessage(f"Key '{key_name}' deleted successfully")
            
            # Create a styled success message for deletion
            success_msg = QMessageBox(self)
            success_msg.setWindowTitle("🗑️ Deleted")
            success_msg.setText("Activation key deleted successfully!")
            success_msg.setInformativeText(f"Key '{key_name}' has been removed.")
            success_msg.setIcon(QMessageBox.Information)
            success_msg.setStyleSheet(f"""
                QMessageBox {{
                    background: {self.SURFACE};
                    color: {self.TEXT_PRIMARY};
                }}
                QMessageBox QPushButton {{
                    background: {self.SUCCESS};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 600;
                    min-width: 80px;
                }}
                QMessageBox QPushButton:hover {{
                    background: #059669;
                }}
            """)
            success_msg.exec()

    def closeEvent(self, event):
        self.manager.close()
        super().closeEvent(event)