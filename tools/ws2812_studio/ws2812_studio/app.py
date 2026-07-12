from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .constants import APP_NAME
from .ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    style_path = Path(__file__).with_name("resources") / "styles.qss"
    if style_path.exists():
        app.setStyleSheet(style_path.read_text(encoding="utf-8"))
    window = MainWindow()
    window.resize(1280, 820)
    window.show()
    return app.exec()
