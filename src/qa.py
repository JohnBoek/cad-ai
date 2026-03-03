from __future__ import annotations
from typing import Dict, Any
import math
from .ir import IRDocument

def _is_on_grid(v: float, grid: float) -> bool:
    return abs(v / grid - round(v / grid)) < 1e-6

def qa_report(ir: IRDocument) -> Dict[str, Any]:
    grid = float(ir.normalization.get("grid_snap_mm", 1.0) or 1.0)
    snap_violations = 0
    entity_count = len(ir.entities)

    for e in ir.entities:
        if e.kind == "line":
            for p in (e.geom["start"], e.geom["end"]):
                if not (_is_on_grid(p[0], grid) and _is_on_grid(p[1], grid)):
                    snap_violations += 1
        elif e.kind == "polyline":
            for p in e.geom.get("points", []):
                if not (_is_on_grid(p[0], grid) and _is_on_grid(p[1], grid)):
                    snap_violations += 1

    return {
        "entities": entity_count,
        "snap_grid_mm": grid,
        "snap_violations": snap_violations,
        "normalization": ir.normalization
    }