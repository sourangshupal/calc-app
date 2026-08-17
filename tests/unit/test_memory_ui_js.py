"""Run Node tests for calculator memory UI helpers."""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_memory_ui_js_helpers() -> None:
    result = subprocess.run(
        ["node", "--test", str(ROOT / "tests/js/test_memory_ui.mjs")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
