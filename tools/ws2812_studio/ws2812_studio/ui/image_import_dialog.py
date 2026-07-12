from __future__ import annotations

from PySide6.QtWidgets import QFileDialog, QWidget


def choose_image(parent: QWidget | None = None) -> str | None:
    path, _ = QFileDialog.getOpenFileName(
        parent,
        "Importar imagen",
        "",
        "Imagenes (*.png *.jpg *.jpeg *.bmp *.webp)",
    )
    return path or None
