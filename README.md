# C4D Skill

`c4d-model-builder` is a Codex skill for scripted Cinema 4D modeling workflows. It helps create, inspect, render, and document `.c4d` scenes with Cinema 4D's `c4dpy.exe` instead of manual UI steps.

## Project Structure

```text
C4D-skill/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   └── c4d-python-patterns.md
└── scripts/
    ├── find_c4dpy.py
    ├── inspect_scene.py
    ├── package_clean_skill.py
    └── render_preview.py
```

- `SKILL.md` contains the skill metadata, trigger description, and workflow instructions.
- `agents/openai.yaml` provides UI metadata for the skill.
- `references/c4d-python-patterns.md` stores compact Cinema 4D Python examples that should be read only when needed.
- `scripts/find_c4dpy.py` locates Cinema 4D's Python interpreter from PATH and common install locations.
- `scripts/inspect_scene.py` prints scene object, polygon, point, and material summaries.
- `scripts/render_preview.py` renders a PNG preview from a `.c4d` scene.
- `scripts/package_clean_skill.py` creates a `.skill` package without Git metadata or cache files.

This layout follows the standard skill pattern: one root `SKILL.md`, with optional `scripts/`, `references/`, and `agents/` directories.

## Requirements

- Cinema 4D installed locally.
- `c4dpy.exe` available in PATH or in a common Maxon/Cinema 4D install directory.
- Python 3 for helper scripts and validation.

On Windows, use UTF-8 mode for validation and packaging commands because `SKILL.md` includes Chinese trigger phrases:

```powershell
python -X utf8 <command>
```

## Validate

From the repository root:

```powershell
python -X utf8 "C:\Users\NOC\.codex\skills\skill-creator\scripts\quick_validate.py" .
python -m py_compile scripts\find_c4dpy.py scripts\inspect_scene.py scripts\package_clean_skill.py scripts\render_preview.py
```

## Locate c4dpy.exe

```powershell
python -X utf8 scripts\find_c4dpy.py --require
```

If this fails, add the Cinema 4D install directory containing `c4dpy.exe` to PATH or pass the absolute interpreter path when running C4D scripts.

## Use the Utilities

Inspect a scene:

```powershell
& "<c4dpy.exe>" "scripts\inspect_scene.py" --scene "<workspace>\model.c4d"
```

Render a preview:

```powershell
& "<c4dpy.exe>" "scripts\render_preview.py" --scene "<workspace>\model.c4d" --output "<workspace>\model_preview.png" --camera "<camera name>"
```

## Package

Use the clean packager from the repository root:

```powershell
python -X utf8 scripts\package_clean_skill.py . dist
```

The generated `.skill` archive excludes `.git`, `__pycache__`, existing `.skill` files, and other local build artifacts.

