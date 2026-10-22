import subprocess
import shutil
import sys
import os
from pathlib import Path


def get_linux_path(filename):
    if shutil.which("zenity"):
        res = subprocess.run(
            [
                "zenity",
                "--file-selection",
                "--save",
                f"--filename={filename}.odt",
                "--title=Save Document As (Change extension for .odt, .pdf, .docx, .md)",
                "--file-filter=Supported Documents (*.odt, *.docx, *.md, *.pdf) | *.odt *.docx *.md *.pdf",
                "--file-filter=LibreOffice Writer (*.odt) | *.odt",
                "--file-filter=Word Document (*.docx) | *.docx",
                "--file-filter=Markdown (*.md) | *.md",
                "--file-filter=PDF Document (*.pdf) | *.pdf",
            ],
            capture_output=True,
            text=True
        )

        if res.returncode != 0:
            return None

        path = res.stdout.strip()

        if not Path(path).suffix:
            path = f"{path}.odt"

        return path
    else:
        return get_windows_mac_path()

def get_windows_mac_path():
    """
    I don't have a means to test this (yet)
    For the mean time, I will return a hardcoded (env) path
    """
    return os.environ["TMP_TEST_FOLDER"]