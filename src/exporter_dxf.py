from __future__ import annotations
import ezdxf
from typing import Dict
from .ir import IRDocument, Entity

def export_dxf(ir: IRDocument, out_path: str, layer_policy: Dict) -> None:
    doc = ezdxf.new(dxfversion="R2013")
    msp = doc.modelspace()

    # create layers
    layers_out = layer_policy.get("layers_out", {})
    for key, spec in layers_out.items():
        name = spec.get("name", str(key))
        if name in doc.layers:
            continue
        doc.layers.new(
            name=name,
            dxfattribs={
                "color": int(spec.get("color", 7)),
                "linetype": spec.get("linetype", "CONTINUOUS")
            }
        )

    fallback_layer_key = layer_policy.get("fallback", {}).get("unclassified_layer_out", "0")
    fallback_layer_name = layers_out.get(str(fallback_layer_key), {}).get("name", str(fallback_layer_key))

    def pick_layer(e: Entity) -> str:
        # MVP: nog geen semantiek -> alles naar fallback
        # later: match semantic_type met policy.map
        return fallback_layer_name

    for e in ir.entities:
        layer_name = pick_layer(e)

        if e.kind == "line":
            msp.add_line(e.geom["start"], e.geom["end"], dxfattribs={"layer": layer_name})

        elif e.kind == "polyline":
            pts = e.geom.get("points", [])
            closed = bool(e.geom.get("closed", False))
            if not pts:
                continue
            msp.add_lwpolyline(pts, format="xy", close=closed, dxfattribs={"layer": layer_name})

        elif e.kind == "circle":
            msp.add_circle(e.geom["center"], e.geom["radius"], dxfattribs={"layer": layer_name})

        elif e.kind == "arc":
            msp.add_arc(
                e.geom["center"],
                e.geom["radius"],
                e.geom["start_angle"],
                e.geom["end_angle"],
                dxfattribs={"layer": layer_name},
            )

        elif e.kind == "text":
            text = e.geom.get("text", "")
            pos = e.geom.get("pos", (0.0, 0.0))
            height = float(e.geom.get("height", 2.5) or 2.5)

            msp.add_text(
                text,
                dxfattribs={
                    "layer": layer_name,
                    "height": height,
                    "insert": pos,
                },
            )

    doc.saveas(out_path)