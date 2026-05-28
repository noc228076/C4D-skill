import argparse
import os
from pathlib import Path


COMMON_ROOTS = [
    Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / "Maxon",
    Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / "MAXON",
    Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Maxon",
]

COMMON_GLOBS = [
    Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / "Maxon Cinema 4D*",
    Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / "Cinema 4D*",
]


def path_entries():
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if entry:
            yield Path(entry)


def find_from_path():
    for folder in path_entries():
        candidate = folder / "c4dpy.exe"
        if candidate.is_file():
            return candidate
    return None


def find_from_common_roots():
    for root in COMMON_ROOTS:
        if not root.is_dir():
            continue
        for candidate in root.rglob("c4dpy.exe"):
            if candidate.is_file():
                return candidate
    for pattern in COMMON_GLOBS:
        for root in pattern.parent.glob(pattern.name):
            if root.is_file() and root.name.lower() == "c4dpy.exe":
                return root
            if not root.is_dir():
                continue
            for candidate in root.rglob("c4dpy.exe"):
                if candidate.is_file():
                    return candidate
    return None


def main():
    parser = argparse.ArgumentParser(description="Locate Cinema 4D's c4dpy.exe.")
    parser.add_argument(
        "--require",
        action="store_true",
        help="Exit with an error when c4dpy.exe cannot be found.",
    )
    args = parser.parse_args()

    candidate = find_from_path() or find_from_common_roots()
    if candidate:
        print(str(candidate))
        return

    message = (
        "c4dpy.exe not found. Add Cinema 4D's install directory to PATH or pass "
        "the absolute c4dpy.exe path in the command."
    )
    if args.require:
        raise SystemExit(message)
    print(message)


if __name__ == "__main__":
    main()
