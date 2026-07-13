from pathlib import Path

from ws2812_studio.models.frame import Frame
from ws2812_studio.models.project import Project
from ws2812_studio.services import build_program
from ws2812_studio.services.build_program import CommandResult, parse_timing


def test_parse_timing_uses_last_report():
    output = "\n".join(
        [
            "Info: Max frequency for clock '$glbnet$crg_clkout0': 59.45 MHz (FAIL at 60.00 MHz)",
            "Info: Max frequency for clock '$glbnet$crg_clkout0': 72.39 MHz (PASS at 60.00 MHz)",
        ]
    )
    timing = parse_timing(output)
    assert timing.pass_timing is True
    assert timing.fmax_mhz == 72.39


def test_build_pipeline_success_without_real_synthesis(tmp_path, monkeypatch):
    repo = tmp_path
    (repo / "Litex" / "NO_bios_fw_dma").mkdir(parents=True)
    gateware = repo / "Litex" / "build" / "colorlight_5a_75b_ws2812" / "gateware"
    gateware.mkdir(parents=True)
    (gateware / "colorlight_5a_75b.bit").write_bytes(b"bit")
    project_path = repo / "demo.ws2812project"
    Project().save(project_path)

    calls = []

    def fake_run(command, cwd, env=None, emit=None):
        calls.append(command)
        text = "Info: Max frequency for clock '$glbnet$crg_clkout0': 72.39 MHz (PASS at 60.00 MHz)\n"
        return CommandResult(command, 0, text, 0.01)

    monkeypatch.setattr(build_program, "require_tools", lambda tools: None)
    monkeypatch.setattr(build_program, "run_command", fake_run)

    lines = []
    assert build_program.build_and_program(project_path, repo, program=False, emit=lines.append) == 0
    assert any("Frames: 1" in line for line in lines)
    assert any("PASS" in line for line in lines)
    assert len(calls) == 2


def test_program_existing_fails_when_detect_does_not_match(tmp_path, monkeypatch):
    repo = tmp_path
    gateware = repo / "Litex" / "build" / "colorlight_5a_75b_ws2812" / "gateware"
    gateware.mkdir(parents=True)
    (gateware / "colorlight_5a_75b.bit").write_bytes(b"bit")

    def fake_run(command, cwd, env=None, emit=None):
        return CommandResult(command, 0, "no devices\n", 0.01)

    monkeypatch.setattr(build_program, "require_tools", lambda tools: None)
    monkeypatch.setattr(build_program, "run_command", fake_run)

    lines = []
    assert build_program.program_existing_bitstream(repo, emit=lines.append) == 1
    assert any("No se detecto" in line for line in lines)
