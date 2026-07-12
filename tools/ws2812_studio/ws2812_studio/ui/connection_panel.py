from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QFrame, QLabel, QPushButton, QVBoxLayout

from ws2812_studio.constants import DEFAULT_BAUDRATE, SUPPORTED_BAUDRATES
from ws2812_studio.services.serial_transport import available_serial_ports


class ConnectionPanel(QFrame):
    connectRequested = Signal(str, int, bool)
    disconnectRequested = Signal()
    pingRequested = Signal()
    infoRequested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.port = QComboBox()
        self.baud = QComboBox()
        for baud in SUPPORTED_BAUDRATES:
            self.baud.addItem(str(baud), baud)
        self.baud.setCurrentText(str(DEFAULT_BAUDRATE))
        self.mode = QComboBox()
        self.mode.addItem("Simulador", True)
        self.mode.addItem("Dispositivo real", False)
        refresh = QPushButton("Actualizar puertos")
        refresh.clicked.connect(self.refresh_ports)
        self.connect_btn = QPushButton("Conectar")
        self.connect_btn.clicked.connect(self._connect_clicked)
        disconnect = QPushButton("Desconectar")
        disconnect.clicked.connect(self.disconnectRequested.emit)
        ping = QPushButton("PING")
        ping.clicked.connect(self.pingRequested.emit)
        info = QPushButton("GET_INFO")
        info.clicked.connect(self.infoRequested.emit)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Conexion"))
        layout.addWidget(self.mode)
        layout.addWidget(self.port)
        layout.addWidget(self.baud)
        layout.addWidget(refresh)
        layout.addWidget(self.connect_btn)
        layout.addWidget(disconnect)
        layout.addWidget(ping)
        layout.addWidget(info)
        self.refresh_ports()

    def refresh_ports(self) -> None:
        current = self.port.currentText()
        self.port.clear()
        ports = available_serial_ports()
        if ports:
            self.port.addItems(ports)
        else:
            self.port.addItem("/dev/ttyUSB0")
        index = self.port.findText(current)
        if index >= 0:
            self.port.setCurrentIndex(index)

    def _connect_clicked(self) -> None:
        self.connectRequested.emit(self.port.currentText(), int(self.baud.currentData()), bool(self.mode.currentData()))
