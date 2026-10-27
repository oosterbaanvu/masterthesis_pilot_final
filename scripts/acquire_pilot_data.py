import json
from pathlib import Path
from thesis_audit.acquire import acquire_one
R=Path(__file__).resolve().parents[1]
for manifest in ['datasets.json','external_datasets.json']:
 for item in json.loads((R/'manifests/thesis_pilot'/manifest).read_text()):print(acquire_one(item,R))
