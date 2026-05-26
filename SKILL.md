---
name: c4d-model-builder
description: Automate Cinema 4D modeling with Python and c4dpy. Use when the user asks to create, edit, inspect, validate, render, or document scripted C4D/Cinema 4D models, .c4d files, C4D Python API workflows, polygon meshes, splines, sweeps, materials, lighting, cameras, or preview images; also use for Chinese requests such as C4D建模, Cinema 4D建模, 生成c4d模型, 渲染预览, 内六角扳手建模, or agent学习C4D建模.
---

# C4D Model Builder

## Path Rules

Never use paths from this skill, old examples, previous sessions, or reference files as output destinations. Treat all example paths as placeholders only.

Resolve paths in this order:

1. Use the exact output directory or filename the user explicitly requested.
2. Otherwise use the current working directory from the active environment/session.
3. Put generated project scripts, `.c4d` files, preview images, and exports in that resolved workspace.
4. Only write elsewhere after the user explicitly asks for that location.

In generated Python scripts, prefer:

```python
WORKSPACE = os.getcwd()
OUTPUT_PATH = os.path.join(WORKSPACE, "model_name.c4d")
PREVIEW_PATH = os.path.join(WORKSPACE, "model_name_preview.png")
```

Do not copy historical project paths into new tasks unless that path is the current workspace or the user explicitly named it.

## Core Workflow

Use Cinema 4D as a scripted geometry engine, not as a manual UI. Create or update project scripts in the resolved workspace, run them with C4D's `c4dpy.exe`, inspect the saved scene, then render a preview.

1. Locate `c4dpy.exe` from PATH or common Maxon install folders. The C4D executable path is only the interpreter location, not the project/output location.
2. Decompose the target into recognizable geometry: main silhouette, structural parts, functional details, materials, lighting, camera, and optional labels.
3. Write a project-specific `create_<model>_c4d.py` script in the resolved workspace. Use `c4d.documents.BaseDocument()`, insert objects/materials, set render settings, and save `.c4d` to the same workspace unless the user requested otherwise.
4. Run the create script with `c4dpy.exe`; do not use normal Python for `import c4d`.
5. Inspect the `.c4d` with `scripts/inspect_scene.py` or a project-specific variant. Verify object names, counts, polygon counts, and materials.
6. Render a PNG preview with `scripts/render_preview.py` or a project-specific render script.
7. Iterate from the preview. Fix silhouette and real geometry before adding labels or decorative text.

## Commands

Use PowerShell command form with placeholders:

```powershell
& '<c4dpy.exe>' '<workspace>\create_model_c4d.py'
```

Use bundled utilities:

```powershell
& '<c4dpy.exe>' '<skill_dir>\scripts\inspect_scene.py' --scene '<workspace>\model.c4d'
& '<c4dpy.exe>' '<skill_dir>\scripts\render_preview.py' --scene '<workspace>\model.c4d' --output '<workspace>\model_preview.png' --camera '<camera name>'
```

If C4D constants or behavior are uncertain, probe them with `c4dpy.exe -c "import c4d; print(...)"`.

## Modeling Guidance

- Start with the thing users recognize first. For an Allen key, model the L-shaped centerline, hexagonal cross-section, bend radius, and chamfered tips before scene decoration.
- Use parameter primitives for simple hard-surface parts: `Ocube`, `Oplane`, `Ocamera`, `Olight`.
- Use `PolygonObject` for precise hard-surface meshes, custom sections, rings, tubes, bevel-like tapering, gauges, and mechanical parts.
- Use `SplineObject + Osweep` for coils, hoses, cables, handlebars, and smooth routed paths.
- Use `Osplinetext + Oextrude` only for labels, markings, or display text. Do not let text replace modeled structure.
- Give every object semantic names, such as `Allen_Key_6mm_hex_body_chamfered`, `front_hydraulic_disc_caliper`, or `thin_translucent_polymer_film_between_platens`.
- Split materials by function and surface: dark steel, chrome, rubber, glass, display, warning red, film, workbench.
- Always add camera and lights for generated scenes unless the user explicitly only wants geometry.

## References

Read `references/c4d-python-patterns.md` when writing or debugging C4D Python scripts. It contains compact API patterns for documents, materials, polygon meshes, splines, rendering, and the Allen-key modeling pattern.

Existing project files may be useful as design references only when they are present in the active workspace. Do not use their directory as the output directory for unrelated tasks.

## Quality Bar

Before final response, report the `.c4d` path, preview path when rendered, and inspection highlights. Mention if rendering was skipped or failed. Prefer a working file and preview over a long abstract explanation.
