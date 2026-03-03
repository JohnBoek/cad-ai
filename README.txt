# cad-ai MVP

## Run
1) Convert DWG -> DXF using ODA File Converter into `data/raw_dxf/`
2) Run pipeline:

Windows PowerShell:
- Activate venv
- python -m src.run_pipeline --in data/raw_dxf --out data/output_generated --rules configs/rulesets/pneuman_house_v1.yaml --policy configs/layer_policies/pneuman_default.json