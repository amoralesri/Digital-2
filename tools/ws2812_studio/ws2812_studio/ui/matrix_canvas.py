from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ws2812_studio.constants import HEIGHT, WIDTH
from ws2812_studio.models.frame import Frame
from ws2812_studio.services.mapping import MatrixMapping


class MatrixCanvas(QWidget):
    frameChanged = Signal()
    hovered = Signal(int, int, int, tuple)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumSize(360, 360)
        self.setMouseTracking(True)
        self.frame = Frame.blank()
        self.mapping = MatrixMapping()
        self.current_color = (16, 0, 0)
        self.tool = "pencil"
        self._dragging = False
        self._line_start: tuple[int, int] | None = None

    def set_frame(self, frame: Frame) -> None:
        self.frame = frame
        self.update()

    def set_color(self, color: tuple[int, int, int]) -> None:
        self.current_color = color

    def set_tool(self, tool: str) -> None:
        self.tool = tool

    def cell_rect(self, x: int, y: int) -> QRect:
        side = min(self.width(), self.height()) - 20
        cell = side // WIDTH
        x0 = (self.width() - cell * WIDTH) // 2
        y0 = (self.height() - cell * HEIGHT) // 2
        return QRect(x0 + x * cell, y0 + y * cell, cell, cell)

    def pos_to_cell(self, pos: QPoint) -> tuple[int, int] | None:
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if self.cell_rect(x, y).contains(pos):
                    return x, y
        return None

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#0c0f14"))
        for y in range(HEIGHT):
            for x in range(WIDTH):
                r, g, b = self.frame.get_pixel(x, y)
                rect = self.cell_rect(x, y).adjusted(4, 4, -4, -4)
                color = QColor(r, g, b)
                glow = QColor(r, g, b, 80)
                painter.setPen(QPen(QColor("#27313d"), 1))
                painter.setBrush(glow)
                painter.drawRoundedRect(rect.adjusted(-2, -2, 2, 2), 8, 8)
                painter.setBrush(color)
                painter.drawRoundedRect(rect, 7, 7)
                if r + g + b < 12:
                    painter.setBrush(QColor("#111820"))
                    painter.drawRoundedRect(rect, 7, 7)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        cell = self.pos_to_cell(event.position().toPoint())
        if cell:
            x, y = cell
            self.hovered.emit(x, y, self.mapping.logical_to_physical(x, y), self.frame.get_pixel(x, y))
            if self._dragging and self.tool in ("pencil", "eraser"):
                self._apply_cell(x, y, erase=self.tool == "eraser")

    def mousePressEvent(self, event) -> None:  # noqa: N802
        cell = self.pos_to_cell(event.position().toPoint())
        if cell is None:
            return
        x, y = cell
        if event.button() == Qt.MouseButton.RightButton:
            self._apply_cell(x, y, erase=True)
            return
        self._dragging = True
        if self.tool == "eyedropper":
            self.current_color = self.frame.get_pixel(x, y)
        elif self.tool == "fill":
            self.frame.fill(self.current_color)
            self.frameChanged.emit()
            self.update()
        elif self.tool == "line":
            if self._line_start is None:
                self._line_start = (x, y)
            else:
                self._draw_line(self._line_start, (x, y))
                self._line_start = None
        elif self.tool == "rectangle":
            if self._line_start is None:
                self._line_start = (x, y)
            else:
                self._draw_rectangle(self._line_start, (x, y))
                self._line_start = None
        else:
            self._apply_cell(x, y, erase=self.tool == "eraser")

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        self._dragging = False

    def _apply_cell(self, x: int, y: int, erase: bool = False) -> None:
        self.frame.set_pixel(x, y, (0, 0, 0) if erase else self.current_color)
        self.frameChanged.emit()
        self.update()

    def _draw_line(self, start: tuple[int, int], end: tuple[int, int]) -> None:
        x0, y0 = start
        x1, y1 = end
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.frame.set_pixel(x0, y0, self.current_color)
            if (x0, y0) == (x1, y1):
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy
        self.frameChanged.emit()
        self.update()

    def _draw_rectangle(self, start: tuple[int, int], end: tuple[int, int]) -> None:
        x0, x1 = sorted((start[0], end[0]))
        y0, y1 = sorted((start[1], end[1]))
        for x in range(x0, x1 + 1):
            self.frame.set_pixel(x, y0, self.current_color)
            self.frame.set_pixel(x, y1, self.current_color)
        for y in range(y0, y1 + 1):
            self.frame.set_pixel(x0, y, self.current_color)
            self.frame.set_pixel(x1, y, self.current_color)
        self.frameChanged.emit()
        self.update()
