# CAD-AI – Roadmap

## Phase 1 – Geometry Stabilization (CURRENT)

✔ DXF importer
✔ IR model
✔ Snap to grid
✔ Remove short segments
✔ Fast endpoint merge
✔ DXF export
✔ QA report
✔ Git integration

---

## Phase 2 – Semantics v0

Goal: deterministic recognition without ML

Planned:
- Read INSERT (blocks)
- Detect block names (stairs/lifts)
- Layer-based regex classification
- semantic_type field in IR
- Layer policy mapping applied in exporter

Output:
- Walls separated
- Stairs recognized
- Lifts recognized

---

## Phase 3 – Single-Line Walls

Goal:
Convert double-line walls to centerlines.

Steps:
- Detect parallel line pairs
- Check overlap and thickness range
- Generate centerline polylines
- Merge into continuous walls
- Tag as outer_wall / inner_wall

---

## Phase 4 – Panel Composition

Goal:
Combine multiple floors into panel layout (e.g. 800x600).

Features:
- Bounding box calculation
- Grid placement
- Legend area reservation
- Uniform scaling
- Optional 90° rotation
- Output combined panel DXF

---

## Phase 5 – Rule Validation

Add checks:
- Stair tread min spacing (1mm in output)
- Zone overlap detection
- Snap compliance score
- Floor alignment score

---

## Phase 6 – ML Assistance (Optional)

Use ML only for:
- Entity classification
- Pattern recognition
- Robustness across architect styles

ML will not:
- Replace geometry rules
- Replace deterministic transformations

---

## Long-Term Vision

A configurable CAD compiler
usable by third parties via rule configs.

Config-driven.
Deterministic.
Auditable.
Extendable.