# CAD-AI – Architecture Overview

## Purpose

This project builds a deterministic CAD processing engine for transforming
architectural drawings (DWG/DXF) into optimized, rule-compliant drawings
for fire alarm panels.

Target output:
- Single-line wall representation
- Recognized stairs and lifts
- Fire zones colored
- Strict layer policy (e.g. 50 = outer wall, 35 = inner wall, 25 = stairs/lift)
- Multi-floor panel composition (e.g. 800x600 layouts)

The system is designed as a compiler pipeline, not as a black-box AI.

---

## High-Level Pipeline

DWG
  → ODA File Converter
DXF
  → Importer
  → Internal Representation (IR)
  → Rule Engine (transform + normalize)
  → (future) Semantics
  → (future) Single-line generation
  → Exporter
  → QA Report

---

## Internal Representation (IR)

Entities are converted into a simplified intermediate model:

Supported:
- LINE
- LWPOLYLINE / POLYLINE
- CIRCLE
- ARC
- TEXT / MTEXT

Each entity has:
- kind
- geometry
- layer
- optional semantic_type (future)

The IR allows deterministic geometry operations independent of DXF format.

---

## Rule Engine

Current active rules:

1. Optional uniform scaling
2. Snap to grid (default 1mm)
3. Remove short segments
4. Fast endpoint merge (grid hashing)
5. QA metadata output

Design goals:
- No O(n²) operations
- Deterministic behavior
- Config-driven
- Stable on large drawings (30k+ entities tested)

---

## Separation of Concerns

Geometry Processing (compiler layer)
  - deterministic
  - performance critical
  - config driven

Semantics (classification layer – future)
  - heuristic based (v0)
  - ML assisted (future)
  - assigns semantic_type

Panel Composition (layout layer – future)
  - multiple floors
  - fit-to-canvas scaling
  - legend placement

---

## Philosophy

This system is not “AI drawing stuff”.

It is:

A CAD Compiler
+ Rule Engine
+ Configurable Policy Layer
+ Optional ML classification later

AI will assist in classification,
not in generating geometry blindly.