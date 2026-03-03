# CAD-AI – Rule System

## Overview

Rules are defined in YAML configuration files.

Example:

transform:
  scale_factor: 0.015

normalize:
  grid_snap_mm: 1.0
  endpoint_merge_tol_mm: 1.0
  min_segment_length_mm: 2.0
  merge_collinear: false

---

## Transform Rules

### scale_factor
Uniform scale applied before normalization.

Used for:
- Adapting architectural scale to panel scale
- Ensuring consistent tread spacing

---

## Normalize Rules

### grid_snap_mm
Snaps all coordinates to nearest grid.

Ensures:
- Clean geometry
- Consistent panel behavior
- Rule compliance

---

### endpoint_merge_tol_mm
Merges nearby endpoints using spatial hashing.

Purpose:
- Close small gaps
- Improve contour continuity
- Enable later loop detection

---

### min_segment_length_mm
Removes small artifacts and noise.

Prevents:
- Visual clutter
- False positive wall detection

---

## Future Rules

- Parallel wall detection thresholds
- Stair tread spacing enforcement
- Zone hatch generation
- Layer enforcement policy
- Centerline generation config

---

## Design Principles

- Rules must be deterministic
- Rules must be configurable
- Rules must not depend on UI state
- Rules must be auditable

This is a compiler.
Not a guessing machine.