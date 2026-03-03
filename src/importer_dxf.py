from __future__ import annotations
import ezdxf
from ezdxf.entities import DXFGraphic
from typing import List
from .ir import IRDocument, Entity

def _next_id(prefix: str, n: int) -> str:
    return f"{prefix}-{n:05d}"

def import_dxf(path: str) -> IRDocument:
    doc = ezdxf.readfile(path)
    msp = doc.modelspace()

    ir = IRDocument()
    ir.source = {
        "original_filename": path,
        "importer": "ezdxf",
        "units": "unknown"
    }

    entities: List[Entity] = []
    i = 1

    for e in msp:  # type: ignore
        if not isinstance(e, DXFGraphic):
            continue

        dxftype = e.dxftype()
        layer = getattr(e.dxf, "layer", None)
        color = getattr(e.dxf, "color", None)
        linetype = getattr(e.dxf, "linetype", None)

        props = {"layer_in": layer, "color_in": color, "linetype_in": linetype}

        if dxftype == "LINE":
            start = (float(e.dxf.start.x), float(e.dxf.start.y))
            end = (float(e.dxf.end.x), float(e.dxf.end.y))
            entities.append(Entity(
                id=_next_id("e", i),
                kind="line",
                geom={"start": start, "end": end},
                props=props,
                tags={"source": "dxf", "confidence": 1.0},
            ))
            i += 1

        elif dxftype in ("LWPOLYLINE", "POLYLINE"):
            pts = []
            try:
                for p in e.get_points():  # LWPOLYLINE
                    pts.append((float(p[0]), float(p[1])))
                closed = bool(e.closed)
            except Exception:
                # Fallback for POLYLINE-like
                try:
                    pts = [(float(v.dxf.location.x), float(v.dxf.location.y)) for v in e.vertices]  # type: ignore
                except Exception:
                    continue
                closed = False

            entities.append(Entity(
                id=_next_id("e", i),
                kind="polyline",
                geom={"points": pts, "closed": closed},
                props=props,
                tags={"source": "dxf", "confidence": 1.0},
            ))
            i += 1

        elif dxftype == "CIRCLE":
            center = (float(e.dxf.center.x), float(e.dxf.center.y))
            radius = float(e.dxf.radius)
            entities.append(Entity(
                id=_next_id("e", i),
                kind="circle",
                geom={"center": center, "radius": radius},
                props=props,
                tags={"source": "dxf", "confidence": 1.0},
            ))
            i += 1

        elif dxftype == "ARC":
            center = (float(e.dxf.center.x), float(e.dxf.center.y))
            radius = float(e.dxf.radius)
            start_angle = float(e.dxf.start_angle)
            end_angle = float(e.dxf.end_angle)
            entities.append(Entity(
                id=_next_id("e", i),
                kind="arc",
                geom={
                    "center": center,
                    "radius": radius,
                    "start_angle": start_angle,
                    "end_angle": end_angle
                },
                props=props,
                tags={"source": "dxf", "confidence": 1.0},
            ))
            i += 1

        elif dxftype in ("TEXT", "MTEXT"):
            try:
                text = e.dxf.text if dxftype == "TEXT" else e.plain_text()  # type: ignore
                pos = (float(e.dxf.insert.x), float(e.dxf.insert.y))
                height = float(getattr(e.dxf, "height", 0.0) or 0.0)
            except Exception:
                continue
            entities.append(Entity(
                id=_next_id("e", i),
                kind="text",
                geom={"pos": pos, "height": height},
                props=props,
                tags={"source": "dxf", "confidence": 1.0},
            ))
            entities[-1].geom["text"] = text
            i += 1

        else:
            # MVP: negeren we andere types; later uitbreiden (HATCH, INSERT, SPLINE, etc.)
            continue

    ir.entities = entities
    return ir