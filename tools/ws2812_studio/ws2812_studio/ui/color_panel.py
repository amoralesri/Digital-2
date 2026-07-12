from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QFormLayout, QFrame, QHBoxLayout, QLabel, QPushButton, QSlider, QSpinBox, QVBoxLayout
from PySide6.QtCore import Qt


class ColorPanel(QFrame):
    colorChanged = Signal(tuple)
    brightnessChanged = Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._color = (16, 0, 0)
        self.preview = QLabel()
        self.preview.setFixedHeight(48)
        self.r = self._spin()
        self.g = self._spin()
        self.b = self._spin()
        for spin in (self.r, self.g, self.b):
            spin.valueChanged.connect(self._spin_changed)
        self.brightness = QSlider(Qt.Orientation.Horizontal)
        self.brightness.setRange(0, 255)
        self.brightness.setValue(255)
        self.brightness.valueChanged.connect(self.brightnessChanged.emit)
        choose = QPushButton("Color")
        choose.clicked.connect(self._choose)

        form = QFormLayout()
        form.addRow("R", self.r)
        form.addRow("G", self.g)
        form.addRow("B", self.b)
        form.addRow("Brillo", self.brightness)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Color"))
        layout.addWidget(self.preview)
        layout.addLayout(form)
        layout.addWidget(choose)
        self.set_color(self._color)

    def _spin(self) -> QSpinBox:
        spin = QSpinBox()
        spin.setRange(0, 255)
        return spin

    def set_color(self, color: tuple[int, int, int]) -> None:
        self._color = color
        self.r.blockSignals(True)
        self.g.blockSignals(True)
        self.b.blockSignals(True)
        self.r.setValue(color[0])
        self.g.setValue(color[1])
        self.b.setValue(color[2])
        self.r.blockSignals(False)
        self.g.blockSignals(False)
        self.b.blockSignals(False)
        self.preview.setStyleSheet(f"background: rgb({color[0]}, {color[1]}, {color[2]}); border-radius: 8px;")
        self.colorChanged.emit(color)

    def _spin_changed(self) -> None:
        self.set_color((self.r.value(), self.g.value(), self.b.value()))

    def _choose(self) -> None:
        color = QColorDialog.getColor(QColor(*self._color), self)
        if color.isValid():
            self.set_color((color.red(), color.green(), color.blue()))
