import argparse
import fnmatch
import zipfile
from pathlib import Path


EXCLUDE_DIRS = {".git", "__pycache__", "node_modules", ".pytest_cache"}
EXCLUDE_FILES = {".DS_Store", ".gitignore"}
EXCLUDE_GLOBS = {"*.pyc", "*.pyo", "*.skill"}


def should_exclude(rel_path):
    if any(part in EXCLUDE_DIRS for part in rel_path.parts):
        return True
    if rel_path.name in EXCLUDE_FILES:
        return True
    return any(fnmatch.fnmatch(rel_path.name, pattern) for pattern in EXCLUDE_GLOBS)


def main():
    parser = argparse.ArgumentParser(description="Package a skill without repo metadata.")
    parser.add_argument("skill_dir", help="Path to the skill directory containing SKILL.md.")
    parser.add_argument(
        "output_dir",
        nargs="?",
        default=".",
        help="Directory for the generated .skill file.",
    )
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    if not (skill_dir / "SKILL.md").is_file():
        raise SystemExit("SKILL.md not found in %s" % skill_dir)

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    package_path = output_dir / ("%s.skill" % skill_dir.name)

    with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in skill_dir.rglob("*"):
            if not file_path.is_file():
                continue
            rel_path = file_path.relative_to(skill_dir.parent)
            if should_exclude(rel_path):
                continue
            archive.write(file_path, rel_path)

    print("package=%s" % package_path)


if __name__ == "__main__":
    main()
