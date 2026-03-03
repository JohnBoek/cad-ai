from __future__ import annotations
from typing import Dict, Tuple, List
import math
from .ir import IRDocument, Entity

Point = Tuple[float, float]


def _snap_value(v: float, grid: float) -> float:
    return float(round(v / grid) * grid)


def _snap_point(p: Point, grid: float) -> Point:
    return (_snap_value(p[0], grid), _snap_value(p[1], grid))


def _dist(a: Point, b: Point) -> float:
    return float(math.hypot(a[0] - b[0], a[1] - b[1]))


def apply_rules(ir: IRDocument, rules: Dict) -> IRDocument:
    normalize = rules.get("normalize", {})

    grid = float(normalize.get("grid_snap_mm", 1.0))
    tol = float(normalize.get("endpoint_merge_tol_mm", 0.0))
    min_len = float(normalize.get("min_segment_length_mm", 0.0))

    print(f"[rules] start: entities={len(ir.entities)} grid={grid} tol={tol} min_len={min_len}", flush=True)

    fixes = {
        "snap_grid": 0,
        "remove_short": 0,
        "merge_endpoints_clusters": 0,
        "merge_endpoints_points_affected": 0,
    }

    # -----------------------------
    # 0) Transform: uniform scale
    # -----------------------------
    transform = rules.get("transform", {})
    scale = float(transform.get("scale_factor", 1.0))

    if abs(scale - 1.0) > 1e-12:
        print(f"[rules] doing: scale factor={scale}", flush=True)

        def scale_point(p: Point) -> Point:
            return (p[0] * scale, p[1] * scale)

        for e in ir.entities:
            if e.kind == "line":
                e.geom["start"] = scale_point(e.geom["start"])
                e.geom["end"] = scale_point(e.geom["end"])

            elif e.kind == "polyline":
                pts = e.geom.get("points", [])
                e.geom["points"] = [scale_point(p) for p in pts]

            elif e.kind in ("circle", "arc"):
                e.geom["center"] = scale_point(e.geom["center"])
                e.geom["radius"] = float(e.geom["radius"]) * scale

            elif e.kind == "text":
                e.geom["pos"] = scale_point(e.geom["pos"])
                if "height" in e.geom and e.geom["height"]:
                    e.geom["height"] = float(e.geom["height"]) * scale

        print("[rules] done: scale", flush=True)
        
    # -----------------------------
    # 1) Snap to grid
    # -----------------------------
    for e in ir.entities:
        if e.kind == "line":
            s = _snap_point(e.geom["start"], grid)
            t = _snap_point(e.geom["end"], grid)

            if s != e.geom["start"] or t != e.geom["end"]:
                fixes["snap_grid"] += 1

            e.geom["start"] = s
            e.geom["end"] = t

        elif e.kind == "polyline":
            pts = e.geom.get("points", [])
            new_pts = [_snap_point(p, grid) for p in pts]

            if new_pts != pts:
                fixes["snap_grid"] += 1

            e.geom["points"] = new_pts

        elif e.kind in ("circle", "arc"):
            c = _snap_point(e.geom["center"], grid)
            if c != e.geom["center"]:
                fixes["snap_grid"] += 1
            e.geom["center"] = c

        elif e.kind == "text":
            p = _snap_point(e.geom["pos"], grid)
            if p != e.geom["pos"]:
                fixes["snap_grid"] += 1
            e.geom["pos"] = p

    print("[rules] done: snap_grid", flush=True)

    # -----------------------------
    # 2) Remove short lines
    # -----------------------------
    kept: List[Entity] = []
    for e in ir.entities:
        if e.kind == "line":
            if _dist(e.geom["start"], e.geom["end"]) < min_len:
                fixes["remove_short"] += 1
                continue
        kept.append(e)

    ir.entities = kept
    print(f"[rules] done: remove_short -> entities={len(ir.entities)}", flush=True)

    # -----------------------------
    # 3) Merge endpoints (FAST: grid hashing)
    # -----------------------------
    if tol > 0.0:
        print("[rules] doing: merge_endpoints (fast)", flush=True)

        # Collect endpoints
        endpoints: List[Tuple[int, str, Point]] = []  # (entity_index, which, point)
        for idx, e in enumerate(ir.entities):
            if e.kind == "line":
                endpoints.append((idx, "start", e.geom["start"]))
                endpoints.append((idx, "end", e.geom["end"]))
            elif e.kind == "polyline":
                pts = e.geom.get("points", [])
                if len(pts) >= 2:
                    endpoints.append((idx, "p0", pts[0]))
                    endpoints.append((idx, "pN", pts[-1]))

        # Spatial binning
        cell = tol  # cell size ~ tol

        def cell_key(p: Point) -> Tuple[int, int]:
            return (int(math.floor(p[0] / cell)), int(math.floor(p[1] / cell)))

        buckets: Dict[Tuple[int, int], List[int]] = {}
        for ep_idx, (_ent_idx, _which, p) in enumerate(endpoints):
            k = cell_key(p)
            buckets.setdefault(k, []).append(ep_idx)

        used = [False] * len(endpoints)

        def neighbor_cells(k: Tuple[int, int]):
            cx, cy = k
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    yield (cx + dx, cy + dy)

        for i in range(len(endpoints)):
            if used[i]:
                continue

            used[i] = True
            cluster = [i]

            base_p = endpoints[i][2]
            base_k = cell_key(base_p)

            # Only compare to nearby cells (3x3)
            for nk in neighbor_cells(base_k):
                for j in buckets.get(nk, []):
                    if used[j]:
                        continue
                    if _dist(base_p, endpoints[j][2]) <= tol:
                        used[j] = True
                        cluster.append(j)

            if len(cluster) <= 1:
                continue

            # Centroid of cluster
            sx = 0.0
            sy = 0.0
            for k in cluster:
                sx += endpoints[k][2][0]
                sy += endpoints[k][2][1]
            c = (sx / len(cluster), sy / len(cluster))

            # Apply centroid back to geometry
            for k in cluster:
                ent_idx, which, _p = endpoints[k]
                ent = ir.entities[ent_idx]

                if ent.kind == "line":
                    if which == "start":
                        ent.geom["start"] = c
                    elif which == "end":
                        ent.geom["end"] = c

                elif ent.kind == "polyline":
                    pts = ent.geom.get("points", [])
                    if not pts:
                        continue
                    if which == "p0":
                        pts[0] = c
                    elif which == "pN":
                        pts[-1] = c
                    ent.geom["points"] = pts

            fixes["merge_endpoints_clusters"] += 1
            fixes["merge_endpoints_points_affected"] += len(cluster)

        print(
            f"[rules] done: merge_endpoints clusters={fixes['merge_endpoints_clusters']} "
            f"points={fixes['merge_endpoints_points_affected']}",
            flush=True,
        )

    ir.normalization = {
        "units": rules.get("units", "mm"),
        "grid_snap_mm": grid,
        "endpoint_merge_tol_mm": tol,
        "min_segment_length_mm": min_len,
        "applied": fixes,
    }

    print("[rules] finished", flush=True)
    return ir