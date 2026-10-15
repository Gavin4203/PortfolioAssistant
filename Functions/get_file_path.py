import subprocess
import shutil
import sys
import os

def get_linux_path(filename):
    if shutil.which("zenity"):
        res = subprocess.run(
            [
                "zenity",
                "--file-selection",
                "--directory",
                "--title=Select Destination Folder"
            ],
            capture_output=True,
            text=True
        )
        return res.stdout.strip() if res.returncode == 0 else None
    else:
        return get_windows_mac_path()

def get_windows_mac_path():
    """
    I don't have a means to test this (yet)
    For the mean time, I will return a hardcoded (env) path
    """
    return os.environ["TMP_TEST_FOLDER"]