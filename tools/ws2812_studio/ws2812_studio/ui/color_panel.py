from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QColorDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QVBoxLayout,
)
from PySide6.QtCore import Qt


class ColorPanel(QFrame):
    colorChanged = Signal(tuple)
    brightnessChanged = Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Panel")
        self.setMinimumWidth(320)
        self._base_color = (255, 0, 0)
        self._color_brightness = 255
        self.preview = QLabel()
        self.preview.setObjectName("ColorPreview")
        self.preview.setFixedHeight(32)
        self.preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.preview_label = QLabel()
        self.preview_label.setObjectName("ColorReadout")
        self.r = self._spin()
        self.g = self._spin()
        self.b = self._spin()
        for spin in (self.r, self.g, self.b):
            spin.valueChanged.connect(self._spin_changed)
        self.brightness = QSlider(Qt.Orientation.Horizontal)
        self.brightness.setRange(0, 255)
        self.brightness.setValue(255)
        self.brightness.valueChanged.connect(self._brightness_changed)
        self.brightness_value = QSpinBox()
        self.brightness_value.setRange(0, 255)
        self.brightness_value.setValue(255)
        self.brightness_value.setFixedSize(44, 24)
        self.brightness_value.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.brightness_value.valueChanged.connect(self.brightness.setValue)
        choose = QPushButton("Elegir color")
        choose.clicked.connect(self._choose)
        choose.setObjectName("Secondary")

        presets = QGridLayout()
        presets.setHorizontalSpacing(8)
        presets.setVerticalSpacing(8)
        for index, (name, color) in enumerate(
            [
                ("Rojo", (255, 0, 0)),
                ("Verde", (0, 255, 0)),
                ("Azul", (0, 0, 255)),
                ("Blanco", (255, 255, 255)),
                ("Ambar", (255, 135, 0)),
                ("Lima", (150, 255, 0)),
                ("Cian", (0, 220, 255)),
                ("Magenta", (255, 0, 190)),
                ("Rosa", (255, 80, 150)),
                ("Violeta", (125, 70, 255)),
                ("Calido", (255, 190, 110)),
                ("Off", (0, 0, 0)),
            ]
        ):
            button = QPushButton()
            button.setObjectName("Swatch")
            button.setToolTip(name)
            button.setFixedSize(30, 22)
            border = "#536170" if color == (0, 0, 0) else "transparent"
            button.setStyleSheet(
                "QPushButton#Swatch {"
                f"background: rgb({color[0]}, {color[1]}, {color[2]});"
                f"border: 1px solid {border};"
                "border-radius: 5px;"
                "}"
            )
            button.clicked.connect(lambda _checked=False, value=color: self.set_color(value))
            presets.addWidget(button, index // 6, index % 6)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(7)
        title = QLabel("Paleta")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)
        layout.addWidget(self.preview)
        layout.addWidget(self.preview_label)
        layout.addLayout(presets)
        layout.addSpacing(8)
        layout.addLayout(self._rgb_row())
        layout.addLayout(self._brightness_row())
        layout.addWidget(choose)
        self.set_color(self._base_color)

    def _spin(self) -> QSpinBox:
        spin = QSpinBox()
        spin.setRange(0, 255)
        spin.setFixedSize(44, 24)
        spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        return spin

    def _rgb_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(4)
        for label, spin in (("R", self.r), ("G", self.g), ("B", self.b)):
            badge = QLabel(label)
            badge.setObjectName("ChannelBadge")
            badge.setFixedSize(22, 24)
            row.addWidget(badge)
            row.addWidget(spin)
        row.addStretch()
        return row

    def _brightness_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(6)
        badge = QLabel("Brillo")
        badge.setObjectName("ChannelBadge")
        badge.setFixedSize(48, 24)
        row.addWidget(badge)
        row.addWidget(self.brightness, 1)
        row.addWidget(self.brightness_value)
        return row

    def set_color(self, color: tuple[int, int, int]) -> None:
        self._base_color = color
        self.r.blockSignals(True)
        self.g.blockSignals(True)
        self.b.blockSignals(True)
        self.r.setValue(color[0])
        self.g.setValue(color[1])
        self.b.setValue(color[2])
        self.r.blockSignals(False)
        self.g.blockSignals(False)
        self.b.blockSignals(False)
        self._emit_color()

    def effective_color(self) -> tuple[int, int, int]:
        scale = max(0, min(255, int(self._color_brightness)))
        r, g, b = self._base_color
        return (r * scale // 255, g * scale // 255, b * scale // 255)

    def _emit_color(self) -> None:
        color = self.effective_color()
        self.preview.setStyleSheet(f"background: rgb({color[0]}, {color[1]}, {color[2]});")
        self.preview_label.setText(f"RGB {color[0]}, {color[1]}, {color[2]}  |  brillo {self._color_brightness}")
        self.colorChanged.emit(color)

    def _spin_changed(self) -> None:
        self.set_color((self.r.value(), self.g.value(), self.b.value()))

    def _brightness_changed(self, value: int) -> None:
        self._color_brightness = max(0, min(255, int(value)))
        self.brightness_value.blockSignals(True)
        self.brightness_value.setValue(self._color_brightness)
        self.brightness_value.blockSignals(False)
        self._emit_color()
        self.brightnessChanged.emit(self._color_brightness)

    def _choose(self) -> None:
        color = QColorDialog.getColor(QColor(*self._base_color), self)
        if color.isValid():
            self.set_color((color.red(), color.green(), color.blue()))
