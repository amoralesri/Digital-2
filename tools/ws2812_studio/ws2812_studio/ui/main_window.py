from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from typing import Callable, TypeVar

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ws2812_studio.constants import APP_NAME
from ws2812_studio.models.frame import Frame
from ws2812_studio.models.project import Project
from ws2812_studio.services.device_controller import DeviceController
from ws2812_studio.services.image_converter import convert_image_to_frame
from ws2812_studio.services.serial_transport import SerialTransport, SimulatedTransport

from .color_panel import ColorPanel
from .connection_panel import ConnectionPanel
from .image_import_dialog import choose_image
from .matrix_canvas import MatrixCanvas
from .settings_dialog import SettingsDialog
from .timeline_widget import TimelineWidget

T = TypeVar("T")


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.project = Project()
        self.current_frame_index = 0
        self.controller: DeviceController | None = None
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ws2812-uart")
        self.send_in_flight = False
        self.send_pending = False
        self.playing = False
        self.dirty = False

        self.connection_label = QLabel("Desconectado")
        self.connection_label.setObjectName("Bad")
        self.device_label = QLabel("Sin dispositivo")
        self.live_sync = QCheckBox("Live Sync")
        self.live_timer = QTimer(self)
        self.live_timer.setSingleShot(True)
        self.live_timer.setInterval(100)
        self.live_timer.timeout.connect(self.send_current_frame)
        self.play_timer = QTimer(self)
        self.play_timer.timeout.connect(self._play_next_frame)

        self.canvas = MatrixCanvas()
        self.canvas.set_frame(self.current_frame)
        self.canvas.frameChanged.connect(self._frame_changed)
        self.canvas.hovered.connect(self._hovered)

        self.connection = ConnectionPanel()
        self.connection.connectRequested.connect(self.connect_device)
        self.connection.disconnectRequested.connect(self.disconnect_device)
        self.connection.pingRequested.connect(self.ping)
        self.connection.infoRequested.connect(self.get_info)

        self.color_panel = ColorPanel()
        self.color_panel.colorChanged.connect(self.canvas.set_color)
        self.color_panel.brightnessChanged.connect(lambda _: self._queue_live_sync())

        self.timeline = TimelineWidget()
        self.timeline.addFrameRequested.connect(self.add_frame)
        self.timeline.duplicateFrameRequested.connect(self.duplicate_frame)
        self.timeline.deleteFrameRequested.connect(self.delete_frame)
        self.timeline.playRequested.connect(self.toggle_play)
        self.timeline.stopRequested.connect(self.stop_playback)
        self.timeline.durationChanged.connect(self._duration_changed)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.status = QLabel("x=0 y=0 idx=0 RGB=(0,0,0) GRB=0x000000")

        self._build_ui()
        self._refresh_timeline()

    @property
    def current_frame(self) -> Frame:
        return self.project.animation.frames[self.current_frame_index]

    def _build_ui(self) -> None:
        title = QLabel(APP_NAME)
        title.setObjectName("Title")
        settings = QPushButton("Configuracion")
        settings.clicked.connect(lambda: SettingsDialog(self).exec())
        send = QPushButton("Enviar frame")
        send.clicked.connect(self.send_current_frame)
        clear = QPushButton("Limpiar matriz")
        clear.clicked.connect(self.clear_frame)
        import_btn = QPushButton("Importar imagen")
        import_btn.clicked.connect(self.import_image)
        new_btn = QPushButton("Nuevo")
        new_btn.clicked.connect(self.new_project)
        open_btn = QPushButton("Abrir")
        open_btn.clicked.connect(self.open_project)
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self.save_project)

        top = QHBoxLayout()
        top.addWidget(title)
        top.addSpacing(20)
        top.addWidget(self.connection_label)
        top.addWidget(self.device_label)
        top.addStretch()
        top.addWidget(self.live_sync)
        top.addWidget(settings)

        tools = QVBoxLayout()
        for name, label in [
            ("pencil", "Lapiz"),
            ("eraser", "Borrador"),
            ("eyedropper", "Cuentagotas"),
            ("fill", "Relleno"),
            ("line", "Linea"),
            ("rectangle", "Rectangulo"),
        ]:
            button = QToolButton()
            button.setText(label)
            button.setCheckable(True)
            button.clicked.connect(lambda checked, tool=name: self._set_tool(tool))
            if name == "pencil":
                button.setChecked(True)
            tools.addWidget(button)
        tools.addWidget(clear)
        tools.addWidget(import_btn)
        tools.addWidget(send)
        tools.addWidget(new_btn)
        tools.addWidget(open_btn)
        tools.addWidget(save_btn)
        tools.addStretch()

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(self.connection)
        left_layout.addLayout(tools)

        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.addWidget(self.canvas, 1)
        center_layout.addWidget(self.status)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.addWidget(self.color_panel)
        right_layout.addWidget(QLabel("Registro de comunicacion"))
        right_layout.addWidget(self.log, 1)

        splitter = QSplitter()
        splitter.addWidget(left)
        splitter.addWidget(center)
        splitter.addWidget(right)
        splitter.setStretchFactor(1, 1)

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.addLayout(top)
        layout.addWidget(splitter, 1)
        layout.addWidget(self.timeline)
        self.setCentralWidget(root)

    def _set_tool(self, tool: str) -> None:
        self.canvas.set_tool(tool)

    def log_line(self, message: str) -> None:
        self.log.append(message)

    def connect_device(self, port: str, baud: int, simulator: bool) -> None:
        try:
            transport = SimulatedTransport() if simulator else SerialTransport(port, baud)
            self.controller = DeviceController(transport, self.project.mapping)
            self.controller.open()
            self.connection_label.setText("Conectado")
            self.connection_label.setObjectName("Good")
            self.device_label.setText("Simulador" if simulator else f"{port} @ {baud}")
            self.log_line("Conexion establecida")
        except Exception as exc:  # noqa: BLE001
            self.connection_label.setText("Error")
            self.log_line(f"ERROR conexion: {exc}")

    def disconnect_device(self) -> None:
        if self.controller:
            self.controller.close()
        self.controller = None
        self.connection_label.setText("Desconectado")
        self.device_label.setText("Sin dispositivo")
        self.log_line("Conexion cerrada")

    def _require_controller(self) -> DeviceController | None:
        if self.controller is None:
            QMessageBox.warning(self, APP_NAME, "Conecta el simulador o el dispositivo real primero.")
            return None
        return self.controller

    def _run_device_action(
        self,
        label: str,
        action: Callable[[], T],
        on_success: Callable[[T], None] | None = None,
        on_done: Callable[[], None] | None = None,
    ) -> None:
        future: Future[T] = self.executor.submit(action)

        def poll() -> None:
            if not future.done():
                QTimer.singleShot(20, poll)
                return
            try:
                result = future.result()
            except Exception as exc:  # noqa: BLE001
                self.log_line(f"ERROR {label}: {exc}")
            else:
                if on_success:
                    on_success(result)
            finally:
                if on_done:
                    on_done()

        QTimer.singleShot(20, poll)

    def ping(self) -> None:
        controller = self._require_controller()
        if not controller:
            return
        self._run_device_action(
            "PING",
            controller.ping,
            lambda response: self.log_line(f"RX PING: {response.status.name} {response.message}"),
        )

    def get_info(self) -> None:
        controller = self._require_controller()
        if not controller:
            return

        def received(response) -> None:
            info = response.payload.decode("ascii", errors="replace")
            self.log_line(f"RX GET_INFO: {response.status.name} {info}")
            if info:
                self.device_label.setText(info.split("|")[0])

        self._run_device_action("GET_INFO", controller.get_info, received)

    def send_current_frame(self) -> None:
        controller = self._require_controller()
        if not controller:
            return
        if self.send_in_flight:
            self.send_pending = True
            return
        frame = self.current_frame.copy()
        brightness = self.color_panel.brightness.value()
        self.send_in_flight = True

        def done() -> None:
            self.send_in_flight = False
            if self.send_pending:
                self.send_pending = False
                QTimer.singleShot(0, self.send_current_frame)

        self._run_device_action(
            "SET_FRAME",
            lambda: controller.send_frame(frame, brightness),
            lambda response: self.log_line(f"TX SET_FRAME: {response.status.name} {response.message}"),
            done,
        )

    def _queue_live_sync(self) -> None:
        if self.live_sync.isChecked() and self.controller is not None:
            self.live_timer.start()

    def _frame_changed(self) -> None:
        self.dirty = True
        self._queue_live_sync()

    def _hovered(self, x: int, y: int, index: int, color: tuple[int, int, int]) -> None:
        r, g, b = color
        grb = (g << 16) | (r << 8) | b
        self.status.setText(f"x={x} y={y} idx={index} RGB=({r},{g},{b}) GRB=0x{grb:06x}")

    def clear_frame(self) -> None:
        self.current_frame.clear()
        self.canvas.update()
        self._frame_changed()

    def import_image(self) -> None:
        path = choose_image(self)
        if not path:
            return
        try:
            frame = convert_image_to_frame(path)
            frame.duration_ms = self.current_frame.duration_ms
            self.project.animation.frames[self.current_frame_index] = frame
            self.canvas.set_frame(frame)
            self._frame_changed()
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(self, APP_NAME, f"No se pudo importar la imagen:\n{exc}")

    def add_frame(self) -> None:
        self.project.animation.add_frame()
        self.current_frame_index = len(self.project.animation.frames) - 1
        self.canvas.set_frame(self.current_frame)
        self._refresh_timeline()

    def duplicate_frame(self) -> None:
        self.project.animation.duplicate_frame(self.current_frame_index)
        self.current_frame_index += 1
        self.canvas.set_frame(self.current_frame)
        self._refresh_timeline()

    def delete_frame(self) -> None:
        self.project.animation.remove_frame(self.current_frame_index)
        self.current_frame_index = min(self.current_frame_index, len(self.project.animation.frames) - 1)
        self.canvas.set_frame(self.current_frame)
        self._refresh_timeline()

    def _duration_changed(self, value: int) -> None:
        self.current_frame.duration_ms = value
        self.dirty = True

    def _refresh_timeline(self) -> None:
        self.timeline.set_info(
            self.current_frame_index,
            len(self.project.animation.frames),
            self.current_frame.duration_ms,
        )

    def toggle_play(self) -> None:
        if self.playing:
            self.play_timer.stop()
            self.playing = False
            return
        self.playing = True
        self._play_next_frame()

    def _play_next_frame(self) -> None:
        self.canvas.set_frame(self.current_frame)
        if self.controller:
            self.send_current_frame()
        delay = max(20, int(self.current_frame.duration_ms / max(0.1, self.project.animation.speed)))
        self.current_frame_index += 1
        if self.current_frame_index >= len(self.project.animation.frames):
            if self.project.animation.loop:
                self.current_frame_index = 0
            else:
                self.stop_playback()
                return
        self._refresh_timeline()
        self.play_timer.start(delay)

    def stop_playback(self) -> None:
        self.playing = False
        self.play_timer.stop()
        if self.controller:
            controller = self.controller
            self._run_device_action(
                "STOP",
                controller.stop,
                lambda response: self.log_line(f"TX STOP: {response.status.name}"),
            )

    def new_project(self) -> None:
        self.project = Project()
        self.current_frame_index = 0
        self.canvas.set_frame(self.current_frame)
        self._refresh_timeline()

    def open_project(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Abrir proyecto", "", "WS2812 Project (*.ws2812project)")
        if not path:
            return
        self.project = Project.load(path)
        self.current_frame_index = 0
        self.canvas.set_frame(self.current_frame)
        self._refresh_timeline()

    def save_project(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Guardar proyecto", "", "WS2812 Project (*.ws2812project)")
        if not path:
            return
        if not path.endswith(".ws2812project"):
            path += ".ws2812project"
        self.project.save(Path(path))
        self.dirty = False

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt override.
        self.executor.shutdown(wait=False, cancel_futures=True)
        super().closeEvent(event)
