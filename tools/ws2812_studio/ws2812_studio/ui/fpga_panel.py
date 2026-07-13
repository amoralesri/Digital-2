from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QPushButton, QVBoxLayout


class FPGAPanel(QFrame):
    detectRequested = Signal()
    disconnectRequested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Panel")
        self.status = QLabel("No detectada")
        self.status.setObjectName("Bad")
        self.detail = QLabel("FT232RL JTAG")
        self.detail.setObjectName("Muted")

        detect = QPushButton("Detectar FPGA")
        detect.setObjectName("Primary")
        detect.clicked.connect(self.detectRequested.emit)
        disconnect = QPushButton("Desconectar FPGA")
        disconnect.setObjectName("Danger")
        disconnect.clicked.connect(self.disconnectRequested.emit)

        actions = QGridLayout()
        actions.addWidget(detect, 0, 0)
        actions.addWidget(disconnect, 0, 1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        title = QLabel("FPGA por JTAG")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)
        layout.addWidget(self.status)
        layout.addWidget(self.detail)
        layout.addLayout(actions)

    def set_detected(self, detail: str) -> None:
        self.status.setText("FPGA detectada")
        self.status.setObjectName("Good")
        self.detail.setText(detail)
        self.style().unpolish(self.status)
        self.style().polish(self.status)

    def set_disconnected(self) -> None:
        self.status.setText("Desconectada")
        self.status.setObjectName("Bad")
        self.detail.setText("JTAG liberado")
        self.style().unpolish(self.status)
        self.style().polish(self.status)

    def set_busy(self, text: str) -> None:
        self.status.setText(text)
        self.status.setObjectName("StageLabel")
        self.style().unpolish(self.status)
        self.style().polish(self.status)
