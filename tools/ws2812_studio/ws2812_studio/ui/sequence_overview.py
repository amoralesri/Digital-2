from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QPoint, QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ws2812_studio.constants import HEIGHT, WIDTH
from ws2812_studio.models.frame import Frame


class SequenceOverview(QWidget):
    frameSelected = Signal(int)
    frameDeleteRequested = Signal(int)
    frameMoveRequested = Signal(int, int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumSize(320, 320)
        self.setMouseTracking(True)
        self._frames: list[Frame] = []
        self._current_index = 0
        self._cards: list[QRect] = []
        self._delete_mode = False
        self._reorder_mode = False
        self._drag_index: int | None = None
        self._drop_index: int | None = None
        self._drag_pos = QPoint()
        self._drag_offset = QPoint()

    def set_frames(self, frames: Sequence[Frame], current_index: int) -> None:
        self._frames = list(frames)
        self._current_index = max(0, min(current_index, len(self._frames) - 1)) if self._frames else 0
        self._drop_index = None
        self._drag_index = None
        self._drag_pos = QPoint()
        self._drag_offset = QPoint()
        self.updateGeometry()
        self.update()

    def set_delete_mode(self, enabled: bool) -> None:
        self._delete_mode = enabled
        if enabled:
            self._reorder_mode = False
            self._drag_index = None
            self._drop_index = None
            self.unsetCursor()
        self.update()

    def set_reorder_mode(self, enabled: bool) -> None:
        self._reorder_mode = enabled
        if enabled:
            self._delete_mode = False
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            self._drag_index = None
            self._drop_index = None
            self.unsetCursor()
        self.update()

    def sizeHint(self) -> QSize:  # noqa: N802
        columns = max(1, self._column_count(760))
        rows = max(1, (len(self._frames) + columns - 1) // columns)
        return QSize(760, 20 + rows * 150)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return QSize(320, 320)

    def _column_count(self, width: int | None = None) -> int:
        available = max(240, width or self.width())
        return max(1, (available - 24) // 136)

    def _layout_cards(self) -> list[QRect]:
        margin = 12
        gap = 10
        card_w = 126
        card_h = 140
        columns = self._column_count()
        cards: list[QRect] = []
        for index in range(len(self._frames)):
            row = index // columns
            col = index % columns
            x = margin + col * (card_w + gap)
            y = margin + row * (card_h + gap)
            cards.append(QRect(x, y, card_w, card_h))
        needed_rows = max(1, (len(self._frames) + columns - 1) // columns)
        self.setMinimumHeight(margin * 2 + needed_rows * card_h + max(0, needed_rows - 1) * gap)
        return cards

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#0c0f14"))
        self._cards = self._layout_cards()
        if not self._frames:
            painter.setPen(QColor("#94a3b8"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Sin frames")
            return
        if self._reorder_mode and self._drag_index is not None:
            self._paint_reorder_preview(painter)
            return
        for index, frame in enumerate(self._frames):
            self._paint_card(painter, index, frame, self._cards[index])

    def _paint_card(self, painter: QPainter, index: int, frame: Frame, card: QRect) -> None:
        selected = index == self._current_index
        dragged = index == self._drag_index
        border = QColor("#17a36f") if selected else QColor("#2a3440")
        fill = QColor("#10231e") if selected else QColor("#151a21")
        if dragged:
            border = QColor("#00d9ff")
            fill = QColor("#0b2630")
        painter.setPen(QPen(border, 2 if selected else 1))
        painter.setBrush(fill)
        painter.drawRoundedRect(card, 8, 8)

        painter.setPen(QColor("#e0f2fe"))
        painter.drawText(card.adjusted(10, 8, -10, 0), Qt.AlignmentFlag.AlignLeft, f"Frame {index + 1}")
        painter.setPen(QColor("#94a3b8"))
        painter.drawText(card.adjusted(10, 8, -10, 0), Qt.AlignmentFlag.AlignRight, f"{frame.duration_ms} ms")

        grid = QRect(card.x() + 15, card.y() + 34, 96, 96)
        cell = grid.width() // WIDTH
        for y in range(HEIGHT):
            for x in range(WIDTH):
                r, g, b = frame.get_pixel(x, y)
                rect = QRect(grid.x() + x * cell, grid.y() + y * cell, cell - 1, cell - 1)
                color = QColor(r, g, b) if r + g + b >= 10 else QColor("#101821")
                painter.setPen(QPen(QColor("#223142"), 1))
                painter.setBrush(color)
                painter.drawRoundedRect(rect, 2, 2)

        if self._delete_mode:
            close = self._close_rect(card)
            painter.setPen(QPen(QColor("#ffd7de"), 1))
            painter.setBrush(QColor("#7f2738"))
            painter.drawEllipse(close)
            painter.setPen(QPen(QColor("#fff1f2"), 2))
            painter.drawLine(close.left() + 6, close.top() + 6, close.right() - 6, close.bottom() - 6)
            painter.drawLine(close.right() - 6, close.top() + 6, close.left() + 6, close.bottom() - 6)

    def _paint_drop_marker(self, painter: QPainter, drop_index: int) -> None:
        if not self._cards:
            return
        if drop_index >= len(self._cards):
            card = self._cards[-1]
            x = card.right() + 6
            y1 = card.top() + 10
            y2 = card.bottom() - 10
        else:
            card = self._cards[drop_index]
            x = card.left() - 6
            y1 = card.top() + 10
            y2 = card.bottom() - 10
        painter.setPen(QPen(QColor("#00d9ff"), 3))
        painter.drawLine(x, y1, x, y2)

    def _paint_reorder_preview(self, painter: QPainter) -> None:
        if self._drag_index is None or not self._cards:
            return
        order = self._preview_order()
        for slot, frame_index in enumerate(order):
            if frame_index == self._drag_index:
                continue
            self._paint_card(painter, frame_index, self._frames[frame_index], self._cards[slot])

        dragged_card = QRect(self._drag_pos - self._drag_offset, self._cards[0].size())
        shadow = dragged_card.adjusted(4, 6, 4, 6)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 95))
        painter.drawRoundedRect(shadow, 10, 10)
        painter.setOpacity(0.96)
        self._paint_card(painter, self._drag_index, self._frames[self._drag_index], dragged_card)
        painter.setOpacity(1.0)

    def _preview_order(self) -> list[int]:
        if self._drag_index is None:
            return list(range(len(self._frames)))
        order = list(range(len(self._frames)))
        dragged = order.pop(self._drag_index)
        target = self._normalized_drop_target()
        order.insert(target, dragged)
        return order

    def _normalized_drop_target(self) -> int:
        if self._drop_index is None:
            return self._drag_index or 0
        max_index = max(0, len(self._frames) - 1)
        return max(0, min(self._drop_index, max_index))

    def _close_rect(self, card: QRect) -> QRect:
        return QRect(card.right() - 25, card.top() + 7, 18, 18)

    def _card_index_at(self, point) -> int | None:
        for index, card in enumerate(self._cards):
            if card.contains(point):
                return index
        return None

    def _drop_slot_at(self, point) -> int | None:
        if not self._cards:
            return None
        for index, card in enumerate(self._cards):
            if card.contains(point):
                return index
        return min(
            range(len(self._cards)),
            key=lambda index: (self._cards[index].center() - point).manhattanLength(),
        )

    def mousePressEvent(self, event) -> None:  # noqa: N802
        point = event.position().toPoint()
        for index, card in enumerate(self._cards):
            if not card.contains(point):
                continue
            if self._delete_mode and self._close_rect(card).contains(point):
                self.frameDeleteRequested.emit(index)
                return
            if self._reorder_mode:
                self._drag_index = index
                self._drop_index = index
                self._drag_pos = point
                self._drag_offset = point - card.topLeft()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                event.accept()
                self.update()
                return
            if card.contains(point):
                self.frameSelected.emit(index)
                return

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if not self._reorder_mode or self._drag_index is None:
            return
        point = event.position().toPoint()
        self._drag_pos = point
        drop_index = self._drop_slot_at(point)
        if drop_index is not None and drop_index != self._drop_index:
            self._drop_index = drop_index
        event.accept()
        self.update()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if not self._reorder_mode or self._drag_index is None:
            self._drag_index = None
            self._drop_index = None
            return
        source = self._drag_index
        target = self._normalized_drop_target()
        self._drag_index = None
        self._drop_index = None
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        if target is None:
            self.update()
            return
        if target != source and 0 <= target < len(self._frames):
            self.frameMoveRequested.emit(source, target)
        else:
            self.frameSelected.emit(source)
            self.update()
        event.accept()
