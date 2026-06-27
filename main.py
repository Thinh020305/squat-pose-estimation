from __future__ import annotations

import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def _ensure_project_venv() -> None:
    root = Path(__file__).resolve().parent
    venv_python = root / ".venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        return
    current = Path(sys.executable).resolve()
    target = venv_python.resolve()
    if current != target:
        os.execv(str(target), [str(target), str(Path(__file__).resolve())])


if __name__ == "__main__":
    _ensure_project_venv()
    server = subprocess.Popen([sys.executable, str(Path(__file__).with_name("app.py"))])
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:5000")
    try:
        server.wait()
    except KeyboardInterrupt:
        server.terminate()
