from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

Point = Tuple[float, float]

@dataclass
class Entity:
    id: str
    kind: str  # "line" | "polyline" | "arc" | "circle" | "text" | ...
    geom: Dict[str, Any]
    props: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, Any] = field(default_factory=dict)
    semantic_type: Optional[str] = None  # later: "outer_wall_centerline", etc.

@dataclass
class IRDocument:
    schema_version: str = "cad-ir/1.0"
    source: Dict[str, Any] = field(default_factory=dict)
    entities: List[Entity] = field(default_factory=list)
    normalization: Dict[str, Any] = field(default_factory=dict)
    qa: Dict[str, Any] = field(default_factory=dict)