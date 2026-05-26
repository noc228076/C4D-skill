# C4D Python Patterns

## C4D Python Entry Point

Run C4D scripts with `c4dpy.exe`, not normal Python. Use placeholders for examples; resolve real project paths from the current working directory or the user's requested output directory.

```powershell
& '<c4dpy.exe>' '<workspace>\script.py'
```

Probe API constants:

```powershell
& '<c4dpy.exe>' -c "import c4d; print(c4d.GetC4DVersion()); print(hasattr(c4d.documents, 'SaveDocument'))"
```

## Document and Save

```python
import os
import c4d
from c4d import documents

workspace = os.getcwd()
output_path = os.path.join(workspace, "model_name.c4d")

doc = documents.BaseDocument()
documents.InsertBaseDocument(doc)
documents.SetActiveDocument(doc)

output_dir = os.path.dirname(output_path)
if output_dir:
    os.makedirs(output_dir, exist_ok=True)
saved = documents.SaveDocument(
    doc,
    output_path,
    c4d.SAVEDOCUMENTFLAGS_0,
    c4d.FORMAT_C4DEXPORT,
)
print("saved=%s path=%s" % (saved, output_path))
```

## Materials

```python
def make_material(doc, name, color, specular=0.45, reflection=0.08):
    mat = c4d.BaseMaterial(c4d.Mmaterial)
    mat.SetName(name)
    mat[c4d.MATERIAL_COLOR_COLOR] = c4d.Vector(*color)
    mat[c4d.MATERIAL_USE_SPECULAR] = True
    mat[c4d.MATERIAL_SPECULAR_BRIGHTNESS] = specular
    mat[c4d.MATERIAL_USE_REFLECTION] = True
    mat[c4d.MATERIAL_REFLECTION_BRIGHTNESS] = reflection
    mat.Message(c4d.MSG_UPDATE)
    doc.InsertMaterial(mat)
    return mat


def assign_material(obj, mat):
    tag = obj.MakeTag(c4d.Ttexture)
    tag[c4d.TEXTURETAG_MATERIAL] = mat
    return tag
```

## Polygon Meshes

```python
def poly_object(name, points, polygons, mat=None):
    obj = c4d.PolygonObject(len(points), len(polygons))
    obj.SetName(name)
    obj.SetAllPoints(points)
    for i, poly in enumerate(polygons):
        obj.SetPolygon(i, poly)
    obj.Message(c4d.MSG_UPDATE)
    phong = obj.MakeTag(c4d.Tphong)
    phong[c4d.PHONGTAG_PHONG_ANGLELIMIT] = True
    phong[c4d.PHONGTAG_PHONG_ANGLE] = math.radians(32.0)
    if mat:
        assign_material(obj, mat)
    return obj
```

Align normals after inserting major polygon meshes:

```python
c4d.utils.SendModelingCommand(
    command=c4d.MCOMMAND_ALIGNNORMALS,
    list=[obj],
    mode=c4d.MODELINGCOMMANDMODE_ALL,
    doc=doc,
)
```

## Tube Along a Path

For a path `centers` and tangent list `tangents`, create one cross-section ring per center and connect adjacent rings with quads.

```python
up = c4d.Vector(0.0, 1.0, 0.0)
points = []
polygons = []

for center, tangent in zip(centers, tangents):
    tangent = tangent.GetNormalized()
    side = up.Cross(tangent).GetNormalized()
    for j in range(segments):
        angle = j * 2.0 * math.pi / segments
        p = center + side * math.cos(angle) * radius_x + up * math.sin(angle) * radius_y
        points.append(p)

for i in range(len(centers) - 1):
    for j in range(segments):
        a = i * segments + j
        b = i * segments + (j + 1) % segments
        c = (i + 1) * segments + (j + 1) % segments
        d = (i + 1) * segments + j
        polygons.append(c4d.CPolygon(a, b, c, d))
```

If `up.Cross(tangent)` is near zero, choose a fallback preferred axis before normalizing.

## Sweep From Spline

Use for coils, hoses, cables, and smooth route-like objects:

```python
path = c4d.SplineObject(point_count, c4d.SPLINETYPE_LINEAR)
path.SetName("Coil Path")
path.SetAllPoints(points)
path.Message(c4d.MSG_UPDATE)

profile = c4d.BaseObject(c4d.Osplinerectangle)
profile[c4d.PRIM_RECTANGLE_WIDTH] = 6.0
profile[c4d.PRIM_RECTANGLE_HEIGHT] = 2.2

sweep = c4d.BaseObject(c4d.Osweep)
profile.InsertUnder(sweep)
path.InsertUnder(sweep)
doc.InsertObject(sweep)
```

## Text Labels

```python
extrude = c4d.BaseObject(c4d.Oextrude)
extrude[c4d.EXTRUDEOBJECT_EXTRUSIONOFFSET] = 1.1

text = c4d.BaseObject(c4d.Osplinetext)
text[c4d.PRIM_TEXT_TEXT] = "AD350"
text[c4d.PRIM_TEXT_HEIGHT] = 18
text[c4d.PRIM_TEXT_ALIGN] = c4d.PRIM_TEXT_ALIGN_MIDDLE
text.InsertUnder(extrude)
doc.InsertObject(extrude)
```

Use text sparingly. If a detail is structurally important, model it as geometry.

## Lighting, Camera, Render Settings

```python
key = c4d.BaseObject(c4d.Olight)
key.SetName("large_softbox_key_light")
key[c4d.LIGHT_TYPE] = c4d.LIGHT_TYPE_AREA
key[c4d.LIGHT_BRIGHTNESS] = 1.5
key[c4d.LIGHT_AREADETAILS_SIZEX] = 90.0
key[c4d.LIGHT_AREADETAILS_SIZEY] = 60.0
key.SetAbsPos(c4d.Vector(-70.0, 115.0, -85.0))
doc.InsertObject(key)

camera = c4d.BaseObject(c4d.Ocamera)
camera.SetName("Camera_three_quarter_view")
camera.SetAbsPos(c4d.Vector(-100.0, 125.0, -230.0))
target = c4d.Vector(-10.0, 7.5, 36.0)
camera.SetAbsRot(c4d.utils.VectorToHPB(target - camera.GetAbsPos()))
doc.InsertObject(camera)

basedraw = doc.GetActiveBaseDraw() or doc.ForceCreateBaseDraw()
if basedraw:
    basedraw.SetSceneCamera(camera)

rd = doc.GetActiveRenderData()
rd[c4d.RDATA_XRES] = 1600
rd[c4d.RDATA_YRES] = 1000
rd[c4d.RDATA_RENDERENGINE] = c4d.RDATA_RENDERENGINE_STANDARD
rd[c4d.RDATA_ANTIALIASING] = c4d.RDATA_ANTIALIASING_BEST
```

## Allen-Key Pattern

For an L-shaped hex key:

1. Generate centerline points for long arm, quarter-arc bend, and short arm in the `XZ` plane.
2. Store one tangent per centerline point.
3. Generate six points around each center with `side = up.Cross(tangent)`.
4. Use `across_flats / sqrt(3)` for hex circumradius.
5. Taper the first and last few rings to imitate chamfered ends.
6. Connect rings with quads and cap both ends.

End taper:

```python
def chamfer_scale(distance_from_start, distance_from_end, chamfer_len=8.0):
    scale = 1.0
    if distance_from_start < chamfer_len:
        scale = min(scale, 0.72 + 0.28 * (distance_from_start / chamfer_len))
    if distance_from_end < chamfer_len:
        scale = min(scale, 0.72 + 0.28 * (distance_from_end / chamfer_len))
    return scale
```
