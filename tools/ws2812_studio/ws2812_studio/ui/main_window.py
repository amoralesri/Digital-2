from __future__ import annotations

from pathlib import Path
import sys

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import (
    QButtonGroup,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStackedWidget,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ws2812_studio.constants import APP_NAME
from ws2812_studio.models.frame import Frame
from ws2812_studio.models.project import Project
from ws2812_studio.services.codegen import summarize_project, write_generated_animation
from ws2812_studio.services.image_converter import convert_image_to_frame

from .color_panel import ColorPanel
from .fpga_panel import FPGAPanel
from .image_import_dialog import choose_image
from .matrix_canvas import MatrixCanvas
from .sequence_overview import SequenceOverview
from .settings_dialog import SettingsDialog
from .timeline_widget import TimelineWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.project = Project()
        self.project_path: Path | None = None
        self.current_frame_index = 0
        self.build_process: QProcess | None = None
        self.fpga_process: QProcess | None = None
        self.fpga_action = ""
        self.fpga_output = ""
        self.dirty = False

        self.connection_label = QLabel("Desconectado")
        self.connection_label.setObjectName("Bad")
        self.device_label = QLabel("JTAG sin detectar")

        self.canvas = MatrixCanvas()
        self.canvas.set_frame(self.current_frame)
        self.canvas.frameChanged.connect(self._frame_changed)
        self.canvas.hovered.connect(self._hovered)
        self.canvas.colorPicked.connect(self.color_panel_set_color)
        self.sequence_overview = SequenceOverview()
        self.sequence_overview.frameSelected.connect(self.select_frame)
        self.sequence_overview.frameDeleteRequested.connect(self.delete_frame)
        self.sequence_overview.frameMoveRequested.connect(self.move_frame)

        self.fpga_panel = FPGAPanel()
        self.fpga_panel.detectRequested.connect(self.detect_fpga)
        self.fpga_panel.disconnectRequested.connect(self.disconnect_fpga)

        self.color_panel = ColorPanel()
        self.color_panel.colorChanged.connect(self.canvas.set_color)

        self.timeline = TimelineWidget()
        self.timeline.addFrameRequested.connect(self.add_frame)
        self.timeline.previousFrameRequested.connect(self.previous_frame)
        self.timeline.nextFrameRequested.connect(self.next_frame)
        self.timeline.overviewToggled.connect(self._set_sequence_overview)
        self.timeline.deleteModeToggled.connect(self._set_delete_mode)
        self.timeline.reorderModeToggled.connect(self._set_reorder_mode)
        self.timeline.clearRequested.connect(self.clear_frame)
        self.timeline.importImageRequested.connect(self.import_image)
        self.timeline.saveRequested.connect(self.save_project)
        self.timeline.durationChanged.connect(self._duration_changed)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(110)
        self.status = QLabel("x=0 y=0 idx=0 RGB=(0,0,0) GRB=0x000000")
        self.build_stage = QLabel("Build & Program listo")
        self.build_stage.setObjectName("StageLabel")
        self.build_progress = QProgressBar()
        self.build_progress.setRange(0, 10)
        self.build_progress.setValue(0)

        self._build_ui()
        self._refresh_timeline()

    @property
    def current_frame(self) -> Frame:
        return self.project.animation.frames[self.current_frame_index]

    def _build_ui(self) -> None:
        title = QLabel(APP_NAME)
        title.setObjectName("Title")
        settings = QPushButton("Configuracion")
        settings.setObjectName("Secondary")
        settings.clicked.connect(lambda: SettingsDialog(self).exec())
        build_program_btn = QPushButton("Enviar a matriz")
        build_program_btn.setObjectName("Primary")
        build_program_btn.setMinimumHeight(44)
        build_program_btn.setToolTip("Compila el proyecto y programa la Colorlight por JTAG")
        build_program_btn.clicked.connect(lambda: self.start_build_pipeline(program=True))

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.addWidget(title)
        top.addSpacing(20)
        top.addWidget(self.connection_label)
        top.addWidget(self.device_label)
        top.addStretch()
        top.addWidget(settings)

        tools = QGridLayout()
        tools.setHorizontalSpacing(8)
        tools.setVerticalSpacing(8)
        self.tool_group = QButtonGroup(self)
        self.tool_group.setExclusive(True)
        for index, (name, label) in enumerate([
            ("pencil", "Lapiz"),
            ("eraser", "Borrador"),
            ("eyedropper", "Cuentagotas"),
            ("fill", "Relleno"),
            ("line", "Linea"),
            ("rectangle", "Rectangulo"),
        ]):
            button = QToolButton()
            button.setText(label)
            button.setCheckable(True)
            button.setToolTip(label)
            button.setMinimumHeight(32)
            button.clicked.connect(lambda checked, tool=name: self._set_tool(tool))
            self.tool_group.addButton(button)
            if name == "pencil":
                button.setChecked(True)
            tools.addWidget(button, index // 2, index % 2)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        left_layout.addWidget(self.fpga_panel)
        tools_panel = QWidget()
        tools_panel.setObjectName("Panel")
        tools_panel_layout = QVBoxLayout(tools_panel)
        tools_panel_layout.setContentsMargins(12, 12, 12, 12)
        tools_panel_layout.setSpacing(8)
        tools_title = QLabel("Herramientas")
        tools_title.setObjectName("SectionTitle")
        tools_panel_layout.addWidget(tools_title)
        tools_panel_layout.addLayout(tools)
        left_layout.addWidget(tools_panel)
        left_layout.addStretch()

        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(12, 0, 12, 0)
        edit_page = QWidget()
        edit_layout = QVBoxLayout(edit_page)
        edit_layout.setContentsMargins(0, 0, 0, 0)
        edit_layout.addWidget(self.canvas, 1)
        edit_layout.addWidget(self.status)
        overview_scroll = QScrollArea()
        overview_scroll.setWidgetResizable(True)
        overview_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        overview_scroll.setWidget(self.sequence_overview)
        self.center_stack = QStackedWidget()
        self.center_stack.addWidget(edit_page)
        self.center_stack.addWidget(overview_scroll)
        center_layout.addWidget(self.center_stack, 1)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        right_layout.addWidget(self.color_panel)
        action_title = QLabel("Salida fisica")
        action_title.setObjectName("SectionTitle")
        right_layout.addWidget(action_title)
        right_layout.addWidget(build_program_btn)
        right_layout.addWidget(self.build_stage)
        right_layout.addWidget(self.build_progress)
        log_title = QLabel("Registro")
        log_title.setObjectName("SectionTitle")
        right_layout.addWidget(log_title)
        right_layout.addWidget(self.log, 1)

        splitter = QSplitter()
        splitter.addWidget(left)
        splitter.addWidget(center)
        splitter.addWidget(right)
        splitter.setSizes([260, 690, 360])
        splitter.setChildrenCollapsible(False)
        splitter.setStretchFactor(1, 1)

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        layout.addLayout(top)
        layout.addWidget(splitter, 1)
        layout.addWidget(self.timeline)
        self.setCentralWidget(root)

    def color_panel_set_color(self, color: tuple[int, int, int]) -> None:
        self.color_panel.brightness.setValue(255)
        self.color_panel.set_color(color)

    def _set_tool(self, tool: str) -> None:
        self.canvas.set_tool(tool)

    def log_line(self, message: str) -> None:
        self.log.append(message)

    def jtag_command(self, *extra: str) -> list[str]:
        return ["openFPGALoader", "-c", "ft232RL", "--pins=TXD:CTS:DTR:RXD", *extra]

    @property
    def repo_root(self) -> Path:
        return Path(__file__).resolve().parents[4]

    @property
    def studio_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    def _sync_project_from_ui(self) -> None:
        self.project.brightness = 255

    def _default_build_project_path(self) -> Path:
        path = self.studio_root / "build" / "last_build.ws2812project"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def _save_project_for_pipeline(self) -> Path:
        self._sync_project_from_ui()
        path = self.project_path or self._default_build_project_path()
        self.project.save(path)
        self.project_path = path
        self.dirty = False
        self.log_line(f"Proyecto guardado: {path}")
        return path

    def detect_fpga(self) -> None:
        if self.fpga_process is not None:
            QMessageBox.information(self, APP_NAME, "Ya hay una accion JTAG en ejecucion.")
            return
        self.fpga_panel.set_busy("Detectando...")
        self.connection_label.setText("Detectando")
        self.device_label.setText("openFPGALoader --detect")
        self._start_fpga_process(self.jtag_command("--detect"), "detect")

    def disconnect_fpga(self) -> None:
        if self.fpga_process is not None:
            self.fpga_process.kill()
            self.fpga_process = None
        if self.build_process is not None:
            self.build_process.kill()
            self.build_process = None
        self.fpga_panel.set_busy("Desconectando...")
        self.connection_label.setText("Desconectando")
        self.device_label.setText("Reset JTAG")
        self._start_fpga_process(self.jtag_command("--reset"), "disconnect")

    def _start_fpga_process(self, command: list[str], action: str) -> None:
        self.fpga_action = action
        self.fpga_output = ""
        self.fpga_process = QProcess(self)
        self.fpga_process.setProgram(command[0])
        self.fpga_process.setArguments(command[1:])
        self.fpga_process.setWorkingDirectory(str(self.repo_root))
        self.fpga_process.readyReadStandardOutput.connect(self._read_fpga_output)
        self.fpga_process.readyReadStandardError.connect(self._read_fpga_output)
        self.fpga_process.finished.connect(self._fpga_finished)
        self.log_line("$ " + " ".join(command))
        self.fpga_process.start()

    def _read_fpga_output(self) -> None:
        if self.fpga_process is None:
            return
        data = bytes(self.fpga_process.readAllStandardOutput()).decode(errors="replace")
        data += bytes(self.fpga_process.readAllStandardError()).decode(errors="replace")
        self.fpga_output += data
        for line in data.splitlines():
            self.log_line(line)

    def _fpga_finished(self, exit_code: int, _status) -> None:
        action = self.fpga_action
        output = self.fpga_output
        self.log_line(f"JTAG finalizado con codigo {exit_code}")
        if action == "detect" and exit_code == 0 and "0x41111043" in output and "LFE5U-25" in output:
            self.connection_label.setText("FPGA detectada")
            self.connection_label.setObjectName("Good")
            self.device_label.setText("Lattice ECP5 LFE5U-25")
            self.fpga_panel.set_detected("IDCODE 0x41111043 | Colorlight 5A-75B V8.2")
        elif action == "disconnect" and exit_code == 0:
            self.connection_label.setText("Desconectado")
            self.connection_label.setObjectName("Bad")
            self.device_label.setText("JTAG liberado")
            self.fpga_panel.set_disconnected()
        else:
            self.connection_label.setText("Error JTAG")
            self.connection_label.setObjectName("Bad")
            self.device_label.setText("Revisa FT232RL/JTAG")
            self.fpga_panel.set_disconnected()
        self.style().unpolish(self.connection_label)
        self.style().polish(self.connection_label)
        self.fpga_process = None

    def generate_firmware(self) -> None:
        try:
            self._sync_project_from_ui()
            firmware_dir = self.repo_root / "Litex" / "NO_bios_fw_dma"
            summary = write_generated_animation(self.project, firmware_dir)
            self.build_stage.setText("Firmware generado")
            self.log_line(
                f"Generado: {summary.frame_count} frame(s), {summary.data_bytes} bytes, "
                f"{summary.total_duration_ms} ms"
            )
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(self, APP_NAME, f"No se pudo generar el firmware:\n{exc}")

    def _confirm_programming(self) -> bool:
        message = (
            "Se recompilara el firmware y se programara la FPGA mediante JTAG.\n"
            "La matriz debe estar alimentada correctamente y compartir GND con la FPGA.\n\n"
            "La programacion sera en SRAM; se pierde al apagar la FPGA."
        )
        return QMessageBox.question(self, APP_NAME, message) == QMessageBox.StandardButton.Yes

    def start_build_pipeline(self, program: bool) -> None:
        if self.build_process is not None:
            QMessageBox.information(self, APP_NAME, "Ya hay un build en ejecucion.")
            return
        if program and not self._confirm_programming():
            self.log_line("Compilar y programar cancelado por el usuario")
            return
        try:
            summary = summarize_project(self.project)
            project_path = self._save_project_for_pipeline()
            self.log_line(
                f"Animacion: {summary.frame_count} frame(s), {summary.data_bytes} bytes, "
                f"{summary.total_duration_ms} ms"
            )
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(self, APP_NAME, f"Proyecto invalido:\n{exc}")
            return
        args = [
            str(self.studio_root / "scripts" / "build_and_program.py"),
            "--project",
            str(project_path),
            "--repo-root",
            str(self.repo_root),
        ]
        if not program:
            args.append("--no-program")
        self._start_process(args)

    def start_program_only(self) -> None:
        if self.build_process is not None:
            QMessageBox.information(self, APP_NAME, "Ya hay un proceso en ejecucion.")
            return
        if not self._confirm_programming():
            self.log_line("Programacion cancelada por el usuario")
            return
        args = [
            str(self.studio_root / "scripts" / "build_and_program.py"),
            "--repo-root",
            str(self.repo_root),
            "--program-only",
        ]
        self._start_process(args)

    def _start_process(self, args: list[str]) -> None:
        self.build_progress.setValue(0)
        self.build_stage.setText("Iniciando pipeline")
        self.build_process = QProcess(self)
        self.build_process.setProgram(sys.executable)
        self.build_process.setArguments(args)
        self.build_process.setWorkingDirectory(str(self.repo_root))
        self.build_process.readyReadStandardOutput.connect(self._read_build_output)
        self.build_process.readyReadStandardError.connect(self._read_build_output)
        self.build_process.finished.connect(self._build_finished)
        self.log_line("$ " + " ".join([sys.executable, *args]))
        self.build_process.start()

    def _read_build_output(self) -> None:
        if self.build_process is None:
            return
        data = bytes(self.build_process.readAllStandardOutput()).decode(errors="replace")
        data += bytes(self.build_process.readAllStandardError()).decode(errors="replace")
        for line in data.splitlines():
            if line.startswith("::stage::"):
                self._update_stage(line)
            else:
                self.log_line(line)

    def _update_stage(self, line: str) -> None:
        try:
            index_text, name, state = line.removeprefix("::stage::").split("|", 2)
            index = int(index_text)
        except ValueError:
            self.log_line(line)
            return
        self.build_progress.setValue(index)
        self.build_stage.setText(f"{name}: {state}")

    def _build_finished(self, exit_code: int, _status) -> None:
        if exit_code == 0:
            self.build_stage.setText("Pipeline finalizado: PASS")
        else:
            self.build_stage.setText("Pipeline finalizado: FAIL")
        self.log_line(f"Proceso finalizado con codigo {exit_code}")
        self.build_process = None

    def _run_device_action(
        self, *_args, **_kwargs
    ) -> None:
        self.log_line("La ruta UART fue retirada de la UI principal; usa JTAG.")

    def send_current_frame(self) -> None:
        self.log_line("Enviar frame por UART ya no se usa. Usa Enviar a matriz por JTAG.")

    def _queue_live_sync(self) -> None:
        return

    def _frame_changed(self) -> None:
        self.dirty = True
        self._refresh_sequence_overview()
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
            self._refresh_timeline()
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(self, APP_NAME, f"No se pudo importar la imagen:\n{exc}")

    def add_frame(self) -> None:
        self.project.animation.add_frame(Frame.blank(duration_ms=self.current_frame.duration_ms))
        self.current_frame_index = len(self.project.animation.frames) - 1
        self.canvas.set_frame(self.current_frame)
        self.dirty = True
        self._refresh_timeline()

    def delete_frame(self, index: int) -> None:
        frames = self.project.animation.frames
        if not (0 <= index < len(frames)):
            return
        if len(frames) == 1:
            frames[0].clear()
            self.current_frame_index = 0
            self.canvas.set_frame(self.current_frame)
            self.log_line("El ultimo frame se limpio para conservar una matriz base.")
        else:
            del frames[index]
            if self.current_frame_index > index:
                self.current_frame_index -= 1
            elif self.current_frame_index == index:
                self.current_frame_index = min(index, len(frames) - 1)
            self.canvas.set_frame(self.current_frame)
            self.log_line(f"Frame {index + 1} eliminado.")
        self.dirty = True
        self._refresh_timeline()

    def move_frame(self, source: int, target: int) -> None:
        frames = self.project.animation.frames
        if not (0 <= source < len(frames) and 0 <= target < len(frames)) or source == target:
            return
        current_frame = self.current_frame
        frame = frames.pop(source)
        frames.insert(target, frame)
        self.current_frame_index = next(
            index for index, candidate in enumerate(frames) if candidate is current_frame
        )
        self.canvas.set_frame(self.current_frame)
        self.dirty = True
        self.log_line(f"Frame {source + 1} movido a posicion {target + 1}.")
        self._refresh_timeline()

    def select_frame(self, index: int) -> None:
        if not (0 <= index < len(self.project.animation.frames)):
            return
        self.current_frame_index = index
        self.canvas.set_frame(self.current_frame)
        self._refresh_timeline()

    def previous_frame(self) -> None:
        if self.current_frame_index <= 0:
            return
        self.current_frame_index -= 1
        self.canvas.set_frame(self.current_frame)
        self._refresh_timeline()

    def next_frame(self) -> None:
        if self.current_frame_index >= len(self.project.animation.frames) - 1:
            return
        self.current_frame_index += 1
        self.canvas.set_frame(self.current_frame)
        self._refresh_timeline()

    def _duration_changed(self, value: int) -> None:
        self.current_frame.duration_ms = value
        self.dirty = True
        self._refresh_sequence_overview()

    def _refresh_timeline(self) -> None:
        self.timeline.set_info(
            self.current_frame_index,
            len(self.project.animation.frames),
            self.current_frame.duration_ms,
        )
        self._refresh_sequence_overview()

    def _refresh_sequence_overview(self) -> None:
        self.sequence_overview.set_frames(self.project.animation.frames, self.current_frame_index)

    def _set_sequence_overview(self, enabled: bool) -> None:
        if not enabled:
            self.timeline.delete.setChecked(False)
            self.timeline.reorder.setChecked(False)
        self._refresh_sequence_overview()
        self.center_stack.setCurrentIndex(1 if enabled else 0)

    def _set_delete_mode(self, enabled: bool) -> None:
        self.sequence_overview.set_delete_mode(enabled)
        if enabled:
            self.timeline.overview.setChecked(True)

    def _set_reorder_mode(self, enabled: bool) -> None:
        self.sequence_overview.set_reorder_mode(enabled)
        if enabled:
            self.timeline.overview.setChecked(True)

    def new_project(self) -> None:
        self.project = Project()
        self.project_path = None
        self.current_frame_index = 0
        self.canvas.set_frame(self.current_frame)
        self._refresh_timeline()

    def open_project(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Abrir proyecto", "", "WS2812 Project (*.ws2812project)")
        if not path:
            return
        self.project = Project.load(path)
        self.project_path = Path(path)
        self.current_frame_index = 0
        self.canvas.set_frame(self.current_frame)
        self._refresh_timeline()

    def save_project(self) -> None:
        path = self.project_path
        if path is None:
            selected, _ = QFileDialog.getSaveFileName(self, "Guardar proyecto", "", "WS2812 Project (*.ws2812project)")
            if not selected:
                return
            if not selected.endswith(".ws2812project"):
                selected += ".ws2812project"
            path = Path(selected)
        self._sync_project_from_ui()
        self.project.save(path)
        self.project_path = path
        self.dirty = False
        self.log_line(f"Proyecto guardado: {path}")

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt override.
        if self.build_process is not None:
            self.build_process.kill()
        super().closeEvent(event)
