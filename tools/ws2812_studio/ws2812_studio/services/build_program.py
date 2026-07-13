from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import re
import shutil
import subprocess
import sys
import time
from typing import Callable

from ws2812_studio.models.project import Project
from ws2812_studio.services.codegen import write_generated_animation

STAGES = [
    "Validando proyecto",
    "Generando animacion",
    "Compilando firmware",
    "Generando SoC",
    "Sintetizando",
    "Ejecutando place-and-route",
    "Generando bitstream",
    "Detectando FPGA",
    "Programando FPGA",
    "Finalizado",
]


@dataclass(frozen=True)
class CommandResult:
    command: list[str]
    returncode: int
    output: str
    elapsed_s: float


@dataclass(frozen=True)
class TimingResult:
    fmax_mhz: float | None
    pass_timing: bool
    raw_line: str


class PipelineError(RuntimeError):
    pass


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def litex_python(repo_root: Path) -> str:
    candidate = repo_root / ".venv-litex" / "bin" / "python"
    return str(candidate) if candidate.exists() else sys.executable


def run_command(
    command: list[str],
    cwd: Path,
    env: dict[str, str] | None = None,
    emit: Callable[[str], None] | None = None,
) -> CommandResult:
    started = time.monotonic()
    process = subprocess.Popen(
        command,
        cwd=str(cwd),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    output_lines: list[str] = []
    assert process.stdout is not None
    for line in process.stdout:
        output_lines.append(line)
        if emit:
            emit(line.rstrip("\n"))
    returncode = process.wait()
    return CommandResult(command, returncode, "".join(output_lines), time.monotonic() - started)


def require_tools(tools: list[str]) -> None:
    missing = [tool for tool in tools if shutil.which(tool) is None]
    if missing:
        raise PipelineError("Faltan dependencias: " + ", ".join(missing))


def parse_timing(output: str) -> TimingResult:
    lines = [line for line in output.splitlines() if "Max frequency for clock" in line]
    if not lines:
        return TimingResult(None, False, "No se encontro reporte de Fmax.")
    line = lines[-1]
    match = re.search(r":\s*([0-9]+(?:\.[0-9]+)?) MHz \((PASS|FAIL) at 60\.00 MHz\)", line)
    if not match:
        return TimingResult(None, False, line)
    return TimingResult(float(match.group(1)), match.group(2) == "PASS", line)


def validate_bitstream(repo_root: Path, build_output: str) -> TimingResult:
    bitstream = repo_root / "Litex" / "build" / "colorlight_5a_75b_ws2812" / "gateware" / "colorlight_5a_75b.bit"
    if not bitstream.exists() or bitstream.stat().st_size <= 0:
        raise PipelineError(f"No se genero un bitstream valido: {bitstream}")
    timing = parse_timing(build_output)
    if not timing.pass_timing:
        raise PipelineError(f"Timing no valido: {timing.raw_line}")
    return timing


def emit_stage(emit: Callable[[str], None], index: int, status: str) -> None:
    emit(f"::stage::{index}|{STAGES[index - 1]}|{status}")


def build_and_program(
    project_path: str | Path,
    repo_root: str | Path | None = None,
    program: bool = True,
    emit: Callable[[str], None] | None = None,
) -> int:
    emit = emit or print
    root = Path(repo_root) if repo_root is not None else default_repo_root()
    litex_dir = root / "Litex"
    firmware_dir = litex_dir / "NO_bios_fw_dma"
    bitstream = litex_dir / "build" / "colorlight_5a_75b_ws2812" / "gateware" / "colorlight_5a_75b.bit"

    try:
        emit_stage(emit, 1, "Ejecutando")
        project = Project.load(project_path)
        emit_stage(emit, 1, "PASS")

        emit_stage(emit, 2, "Ejecutando")
        summary = write_generated_animation(project, firmware_dir)
        emit(f"Frames: {summary.frame_count}")
        emit(f"Datos: {summary.data_bytes} bytes")
        emit(f"Duracion total: {summary.total_duration_ms} ms")
        emit_stage(emit, 2, "PASS")

        require_tools(["riscv64-unknown-elf-gcc", "yosys", "nextpnr-ecp5", "ecppack"])
        if program:
            require_tools(["openFPGALoader"])

        emit_stage(emit, 3, "Ejecutando")
        env = os.environ.copy()
        env["BUILD_DIR"] = "../build/colorlight_5a_75b_ws2812/"
        env["PYTHON"] = litex_python(root)
        fw_result = run_command(["make", "-C", "NO_bios_fw_dma", "clean", "all"], litex_dir, env, emit)
        if fw_result.returncode != 0:
            emit_stage(emit, 3, "FAIL")
            raise PipelineError("La compilacion del firmware fallo.")
        emit_stage(emit, 3, "PASS")

        build_cmd = [
            litex_python(root),
            "colorlight_5a_75b_ws2812_dma.py",
            "--revision=8.2",
            "--device-override=LFE5U-25F-6BG256C",
            "--ws2812-pin",
            "j1:0",
            "--build",
            "--no-compile-software",
            "--nextpnr-seed",
            "1",
        ]
        emit_stage(emit, 4, "Ejecutando")
        emit_stage(emit, 5, "Ejecutando")
        emit_stage(emit, 6, "Ejecutando")
        emit_stage(emit, 7, "Ejecutando")
        build_result = run_command(build_cmd, litex_dir, None, emit)
        if build_result.returncode != 0:
            emit_stage(emit, 4, "FAIL")
            emit_stage(emit, 5, "FAIL")
            emit_stage(emit, 6, "FAIL")
            emit_stage(emit, 7, "FAIL")
            raise PipelineError("El build del SoC/bitstream fallo.")
        timing = validate_bitstream(root, build_result.output)
        emit(f"Timing: {timing.raw_line}")
        emit_stage(emit, 4, "PASS")
        emit_stage(emit, 5, "PASS")
        emit_stage(emit, 6, "PASS")
        emit_stage(emit, 7, "PASS")

        if program:
            detect_cmd = ["openFPGALoader", "-c", "ft232RL", "--pins=TXD:CTS:DTR:RXD", "--detect"]
            emit_stage(emit, 8, "Ejecutando")
            detect_result = run_command(detect_cmd, root, None, emit)
            if detect_result.returncode != 0 or "0x41111043" not in detect_result.output or "LFE5U-25" not in detect_result.output:
                emit_stage(emit, 8, "FAIL")
                raise PipelineError("No se detecto la Colorlight. Comprueba alimentacion, FT232RL y JTAG.")
            emit_stage(emit, 8, "PASS")

            program_cmd = [
                "openFPGALoader",
                "-c",
                "ft232RL",
                "--pins=TXD:CTS:DTR:RXD",
                str(bitstream.relative_to(root)),
            ]
            emit_stage(emit, 9, "Ejecutando")
            program_result = run_command(program_cmd, root, None, emit)
            if program_result.returncode != 0:
                emit_stage(emit, 9, "FAIL")
                raise PipelineError("La programacion de SRAM fallo.")
            emit_stage(emit, 9, "PASS")
        else:
            emit_stage(emit, 8, "Cancelado")
            emit_stage(emit, 9, "Cancelado")

        emit("FPGA programada correctamente." if program else "Bitstream generado correctamente.")
        if program:
            emit("La animacion ya esta ejecutandose en la matriz.")
        emit_stage(emit, 10, "PASS")
        return 0
    except Exception as exc:  # noqa: BLE001 - user-facing pipeline boundary.
        emit(f"ERROR: {exc}")
        emit_stage(emit, 10, "FAIL")
        return 1


def program_existing_bitstream(
    repo_root: str | Path | None = None,
    emit: Callable[[str], None] | None = None,
) -> int:
    emit = emit or print
    root = Path(repo_root) if repo_root is not None else default_repo_root()
    bitstream = root / "Litex" / "build" / "colorlight_5a_75b_ws2812" / "gateware" / "colorlight_5a_75b.bit"
    try:
        require_tools(["openFPGALoader"])
        if not bitstream.exists() or bitstream.stat().st_size <= 0:
            raise PipelineError(f"No existe el bitstream: {bitstream}")

        emit_stage(emit, 8, "Ejecutando")
        detect_cmd = ["openFPGALoader", "-c", "ft232RL", "--pins=TXD:CTS:DTR:RXD", "--detect"]
        detect_result = run_command(detect_cmd, root, None, emit)
        if detect_result.returncode != 0 or "0x41111043" not in detect_result.output or "LFE5U-25" not in detect_result.output:
            emit_stage(emit, 8, "FAIL")
            raise PipelineError("No se detecto la Colorlight. Comprueba alimentacion, FT232RL y JTAG.")
        emit_stage(emit, 8, "PASS")

        emit_stage(emit, 9, "Ejecutando")
        program_cmd = [
            "openFPGALoader",
            "-c",
            "ft232RL",
            "--pins=TXD:CTS:DTR:RXD",
            str(bitstream.relative_to(root)),
        ]
        program_result = run_command(program_cmd, root, None, emit)
        if program_result.returncode != 0:
            emit_stage(emit, 9, "FAIL")
            raise PipelineError("La programacion de SRAM fallo.")
        emit_stage(emit, 9, "PASS")
        emit("FPGA programada correctamente.")
        emit("La animacion ya esta ejecutandose en la matriz.")
        emit_stage(emit, 10, "PASS")
        return 0
    except Exception as exc:  # noqa: BLE001
        emit(f"ERROR: {exc}")
        emit_stage(emit, 10, "FAIL")
        return 1
