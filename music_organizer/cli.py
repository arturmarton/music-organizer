import argparse
import sys
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def library_path():
    """Resolve the desktop's Music directory without a user-specific path."""
    if not shutil.which("xdg-user-dir"):
        raise ValueError("xdg-user-dir is required to find the Music folder; install xdg-user-dirs")
    try:
        result = subprocess.run(
            ["xdg-user-dir", "MUSIC"], check=True, capture_output=True, text=True
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError(f"Could not find the system Music folder: {exc}") from exc
    value = result.stdout.strip()
    path = Path(value)
    if not value or not path.is_absolute() or path == Path.home():
        raise ValueError("The system Music folder is not configured; set XDG_MUSIC_DIR in ~/.config/user-dirs.dirs")
    return path


def main():
    parser = argparse.ArgumentParser(prog="music", add_help=False)
    commands = parser.add_mutually_exclusive_group(required=True)
    commands.add_argument("--download", nargs="?", const="", metavar="LINK")
    commands.add_argument("--sync", action="store_true")
    args = parser.parse_args()
    try:
        if args.download is not None:
            from . import download
            download.main(PROJECT_ROOT, args.download or None)
        else:
            from . import sync
            sync.main(library_path())
    except Exception as exc:
        print(f"[X] {exc}", file=sys.stderr)
        return 1
    return 0
