import argparse

import c4d
from c4d import documents


def walk(obj):
    while obj:
        yield obj
        child = obj.GetDown()
        if child:
            for child_obj in walk(child):
                yield child_obj
        obj = obj.GetNext()


def main():
    parser = argparse.ArgumentParser(description="Inspect a Cinema 4D scene.")
    parser.add_argument("--scene", required=True, help="Path to the .c4d scene.")
    args = parser.parse_args()

    doc = documents.LoadDocument(
        args.scene,
        c4d.SCENEFILTER_OBJECTS | c4d.SCENEFILTER_MATERIALS,
    )
    print("loaded=%s" % bool(doc))
    if not doc:
        raise SystemExit(1)

    objects = list(walk(doc.GetFirstObject()))
    polygon_objects = [
        obj for obj in objects if isinstance(obj, c4d.PolygonObject)
    ]

    print("object_count=%d" % len(objects))
    print("objects=%s" % ", ".join(obj.GetName() for obj in objects))
    print("polygon_objects=%d" % len(polygon_objects))
    print("points=%d" % sum(obj.GetPointCount() for obj in polygon_objects))
    print("polygons=%d" % sum(obj.GetPolygonCount() for obj in polygon_objects))

    materials = []
    mat = doc.GetFirstMaterial()
    while mat:
        materials.append(mat.GetName())
        mat = mat.GetNext()
    print("materials=%s" % ", ".join(materials))


if __name__ == "__main__":
    main()
