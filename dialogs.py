# dialogs.py
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class AddKeyDialog(QDialog):
    # Modern color palette matching main window
    PRIMARY = "#6366F1"
    PRIMARY_HOVER = "#4F46E5"
    SUCCESS = "#10B981"
    DANGER = "#EF4444"
    SURFACE = "#FFFFFF"
    SURFACE_VARIANT = "#F8FAFC"
    BORDER = "#E2E8F0"
    TEXT_PRIMARY = "#1E293B"
    TEXT_SECONDARY = "#64748B"
    TEXT_MUTED = "#94A3B8"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔑 Generate New Activation Key")
        self.setModal(True)
        self.resize(500, 400)
        self.setMinimumSize(450, 350)
        
        # Apply modern styling
        self.setStyleSheet(f"""
            QDialog {{
                background: {self.SURFACE_VARIANT};
                color: {self.TEXT_PRIMARY};
            }}
        """)

        # Header
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
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(20, 16, 20, 16)
        
        title = QLabel("Create New Activation Key")
        title.setStyleSheet(f"""
            font-size: 20px; 
            font-weight: 700; 
            color: {self.TEXT_PRIMARY};
            margin-bottom: 4px;
        """)
        subtitle = QLabel("Fill in the details below to generate a new activation key")
        subtitle.setStyleSheet(f"""
            font-size: 13px; 
            color: {self.TEXT_SECONDARY};
        """)
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)

        # Form container
        form_container = QWidget()
        form_container.setStyleSheet(f"""
            QWidget {{
                background: {self.SURFACE};
                border: 1px solid {self.BORDER};
                border-radius: 8px;
                margin: 4px;
            }}
        """)
        
        form = QFormLayout(form_container)
        form.setContentsMargins(24, 20, 24, 20)
        form.setSpacing(16)
        form.setLabelAlignment(Qt.AlignRight)

        # Name field
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter a descriptive name for this key")
        self.name_edit.setStyleSheet(f"""
            QLineEdit {{
                background: {self.SURFACE};
                border: 2px solid {self.BORDER};
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 14px;
                color: {self.TEXT_PRIMARY};
            }}
            QLineEdit:focus {{
                border-color: {self.PRIMARY};
            }}
            QLineEdit::placeholder {{
                color: {self.TEXT_MUTED};
            }}
        """)

        # Secret field
        self.secret_edit = QLineEdit()
        self.secret_edit.setText("031200006280")
        self.secret_edit.setEchoMode(QLineEdit.Password)
        self.secret_edit.setPlaceholderText("Enter the secret key")
        self.secret_edit.setStyleSheet(f"""
            QLineEdit {{
                background: {self.SURFACE};
                border: 2px solid {self.BORDER};
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 14px;
                color: {self.TEXT_PRIMARY};
            }}
            QLineEdit:focus {{
                border-color: {self.PRIMARY};
            }}
            QLineEdit::placeholder {{
                color: {self.TEXT_MUTED};
            }}
        """)

        # TTL field
        self.ttl_spin = QSpinBox()
        self.ttl_spin.setRange(1, 2_147_483_647)
        self.ttl_spin.setValue(300)
        self.ttl_spin.setSuffix(" seconds")
        self.ttl_spin.setStyleSheet(f"""
            QSpinBox {{
                background: {self.SURFACE};
                border: 2px solid {self.BORDER};
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 14px;
                color: {self.TEXT_PRIMARY};
            }}
            QSpinBox:focus {{
                border-color: {self.PRIMARY};
            }}
        """)

        # Days field
        self.days_spin = QSpinBox()
        self.days_spin.setRange(1, 10_000)
        self.days_spin.setValue(30)
        self.days_spin.setSuffix(" days")
        self.days_spin.setStyleSheet(f"""
            QSpinBox {{
                background: {self.SURFACE};
                border: 2px solid {self.BORDER};
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 14px;
                color: {self.TEXT_PRIMARY};
            }}
            QSpinBox:focus {{
                border-color: {self.PRIMARY};
            }}
        """)

        # Add form fields with styled labels
        name_label = QLabel("📝 Name:")
        name_label.setStyleSheet(f"font-weight: 600; color: {self.TEXT_PRIMARY};")
        form.addRow(name_label, self.name_edit)
        
        secret_label = QLabel("🔐 Secret Key:")
        secret_label.setStyleSheet(f"font-weight: 600; color: {self.TEXT_PRIMARY};")
        form.addRow(secret_label, self.secret_edit)
        
        ttl_label = QLabel("⏱️ TTL:")
        ttl_label.setStyleSheet(f"font-weight: 600; color: {self.TEXT_PRIMARY};")
        form.addRow(ttl_label, self.ttl_spin)
        
        days_label = QLabel("📅 Validity Period:")
        days_label.setStyleSheet(f"font-weight: 600; color: {self.TEXT_PRIMARY};")
        form.addRow(days_label, self.days_spin)

        # Buttons with modern styling
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.setStyleSheet(f"""
            QDialogButtonBox {{
                background: {self.SURFACE};
                border-top: 1px solid {self.BORDER};
                padding: 16px;
            }}
            QPushButton {{
                background: {self.PRIMARY};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 14px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background: {self.PRIMARY_HOVER};
            }}
            QPushButton:pressed {{
                background: {self.PRIMARY_HOVER};
            }}
            QPushButton[text="Cancel"] {{
                background: {self.TEXT_MUTED};
            }}
            QPushButton[text="Cancel"]:hover {{
                background: {self.TEXT_SECONDARY};
            }}
        """)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        layout.addWidget(header)
        layout.addWidget(form_container, 1)
        layout.addWidget(btns)

    def values(self):
        return (
            self.name_edit.text().strip(),
            self.secret_edit.text().strip(),
            int(self.ttl_spin.value()),
            int(self.days_spin.value()),
        )