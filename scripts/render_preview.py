import argparse
import os

import c4d
from c4d import bitmaps, documents


def walk(obj):
    while obj:
        yield obj
        child = obj.GetDown()
        if child:
            for child_obj in walk(child):
                yield child_obj
        obj = obj.GetNext()


def find_camera(doc, name):
    for obj in walk(doc.GetFirstObject()):
        if obj.CheckType(c4d.Ocamera) and (not name or obj.GetName() == name):
            return obj
    return None


def main():
    parser = argparse.ArgumentParser(description="Render a Cinema 4D PNG preview.")
    parser.add_argument("--scene", required=True, help="Path to the .c4d scene.")
    parser.add_argument("--output", required=True, help="Path to the output .png.")
    parser.add_argument("--camera", default="", help="Optional camera object name.")
    parser.add_argument("--width", type=int, default=1000, help="Preview width.")
    parser.add_argument("--height", type=int, default=625, help="Preview height.")
    args = parser.parse_args()

    doc = documents.LoadDocument(
        args.scene,
        c4d.SCENEFILTER_OBJECTS | c4d.SCENEFILTER_MATERIALS,
    )
    if not doc:
        raise RuntimeError("Could not load scene: %s" % args.scene)

    documents.InsertBaseDocument(doc)
    documents.SetActiveDocument(doc)

    camera = find_camera(doc, args.camera)
    basedraw = doc.GetActiveBaseDraw() or doc.ForceCreateBaseDraw()
    if basedraw and camera:
        basedraw.SetSceneCamera(camera)

    rd = doc.GetActiveRenderData()
    rd[c4d.RDATA_XRES] = args.width
    rd[c4d.RDATA_YRES] = args.height

    bmp = bitmaps.MultipassBitmap(args.width, args.height, c4d.COLORMODE_RGB)
    result = documents.RenderDocument(
        doc,
        rd.GetData(),
        bmp,
        c4d.RENDERFLAGS_EXTERNAL | c4d.RENDERFLAGS_DONTANIMATE,
    )
    if result != c4d.RENDERRESULT_OK:
        raise RuntimeError("Render failed with result code: %s" % result)

    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    save_result = bmp.Save(args.output, c4d.FILTER_PNG, None, c4d.SAVEBIT_0)
    print("preview_saved=%s path=%s" % (save_result, args.output))


if __name__ == "__main__":
    main()
