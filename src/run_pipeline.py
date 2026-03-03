from __future__ import annotations
import os
import json
import argparse
from pathlib import Path
import yaml

from .importer_dxf import import_dxf
from .rules_engine import apply_rules
from .exporter_dxf import export_dxf
from .qa import qa_report

def load_yaml(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_one(in_dxf: str, out_dir: str, ruleset_path: str, policy_path: str) -> None:
    print(f"[1] Importing: {in_dxf}", flush=True)

    rules = load_yaml(ruleset_path)
    policy = load_json(policy_path)

    ir = import_dxf(in_dxf)
    print(f"[2] Imported entities: {len(ir.entities)}", flush=True)
    ir = apply_rules(ir, rules)
    print("[3] Rules applied", flush=True)

    out_dir_p = Path(out_dir)
    out_dir_p.mkdir(parents=True, exist_ok=True)

    base = Path(in_dxf).stem
    out_dxf = str(out_dir_p / f"{base}.out.dxf")
    out_qa = str(out_dir_p / f"{base}.qa.json")

    print(f"[4] Exporting: {out_dxf}", flush=True)
    export_dxf(ir, out_dxf, policy)
    print("[5] Export done", flush=True)

    report = qa_report(ir)
    with open(out_qa, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"[OK] {in_dxf} -> {out_dxf}")
    print(f"     QA -> {out_qa}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_path", required=True, help="Input DXF file or folder")
    ap.add_argument("--out", dest="out_dir", required=True, help="Output folder")
    ap.add_argument("--rules", dest="ruleset", required=True, help="Ruleset YAML")
    ap.add_argument("--policy", dest="policy", required=True, help="Layer policy JSON")
    args = ap.parse_args()

    in_path = Path(args.in_path)
    if in_path.is_file() and in_path.suffix.lower() == ".dxf":
        run_one(str(in_path), args.out_dir, args.ruleset, args.policy)
        return

    if in_path.is_dir():
        for p in sorted(in_path.glob("*.dxf")):
            run_one(str(p), args.out_dir, args.ruleset, args.policy)
        return

    raise SystemExit("Input must be a .dxf file or a folder containing .dxf files")

if __name__ == "__main__":
    main()