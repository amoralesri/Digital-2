from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSpinBox


class TimelineWidget(QFrame):
    addFrameRequested = Signal()
    duplicateFrameRequested = Signal()
    deleteFrameRequested = Signal()
    playRequested = Signal()
    stopRequested = Signal()
    durationChanged = Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.info = QLabel("Frame 1/1")
        self.duration = QSpinBox()
        self.duration.setRange(20, 5000)
        self.duration.setValue(250)
        self.duration.setSuffix(" ms")
        self.duration.valueChanged.connect(self.durationChanged.emit)
        add = QPushButton("+")
        add.setToolTip("Crear frame")
        dup = QPushButton("Duplicar")
        delete = QPushButton("Eliminar")
        play = QPushButton("Play/Pausa")
        stop = QPushButton("Stop")
        add.clicked.connect(self.addFrameRequested.emit)
        dup.clicked.connect(self.duplicateFrameRequested.emit)
        delete.clicked.connect(self.deleteFrameRequested.emit)
        play.clicked.connect(self.playRequested.emit)
        stop.clicked.connect(self.stopRequested.emit)
        layout = QHBoxLayout(self)
        layout.addWidget(QLabel("Timeline"))
        layout.addWidget(self.info)
        layout.addWidget(self.duration)
        layout.addWidget(add)
        layout.addWidget(dup)
        layout.addWidget(delete)
        layout.addWidget(play)
        layout.addWidget(stop)
        layout.addStretch()

    def set_info(self, frame_index: int, total: int, duration_ms: int) -> None:
        self.info.setText(f"Frame {frame_index + 1}/{total}")
        self.duration.blockSignals(True)
        self.duration.setValue(duration_ms)
        self.duration.blockSignals(False)
