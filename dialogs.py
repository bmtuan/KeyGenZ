# dialogs.py
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
)


class AddKeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tạo Khóa Mới")
        self.setModal(True)

        self.name_edit = QLineEdit()
        self.secret_edit = QLineEdit()
        self.secret_edit.setText("031200006280")
        self.secret_edit.setEchoMode(QLineEdit.Password)

        self.ttl_spin = QSpinBox()
        self.ttl_spin.setRange(1, 2_147_483_647)
        self.ttl_spin.setValue(300)

        self.days_spin = QSpinBox()
        self.days_spin.setRange(1, 10_000)
        self.days_spin.setValue(30)

        form = QFormLayout()
        form.addRow("Tên", self.name_edit)
        form.addRow("Khóa Bí Mật", self.secret_edit)
        form.addRow("TTL (giây)", self.ttl_spin)
        form.addRow("Thời Hạn Hiệu Lực (ngày)", self.days_spin)

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