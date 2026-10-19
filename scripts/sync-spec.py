#!/usr/bin/env python3
"""Refresh openapi.json from the API and fold guide.md into it.

    scripts/sync-spec.py                      # from production
    scripts/sync-spec.py http://localhost:5186/api/v1/openapi.json
"""
import json
import pathlib
import sys
import urllib.request

PUBLIC_API = "https://calf-lenient-officially.ngrok-free.app"
ROOT = pathlib.Path(__file__).resolve().parent.parent

source = sys.argv[1] if len(sys.argv) > 1 else f"{PUBLIC_API}/api/v1/openapi.json"
request = urllib.request.Request(source, headers={"ngrok-skip-browser-warning": "1"})
with urllib.request.urlopen(request, timeout=60) as response:
    spec = json.load(response)

if not any(path.startswith("/api/v1/") for path in spec.get("paths", {})):
    sys.exit(f"{source} has no /api/v1 paths; refusing to overwrite openapi.json")

# The API names whatever host served the spec; the docs always point at the public one.
spec["servers"] = [{"url": PUBLIC_API, "description": "Production"}]
spec["info"]["description"] = (ROOT / "guide.md").read_text().replace("{{API_URL}}", PUBLIC_API)
spec["tags"] = [
    {"name": "Search", "description": "Find NSNs by name, number, part number, FSC or manufacturer."},
    {"name": "NSNs", "description": "One item's full record and its DLA award history."},
    {"name": "Solicitations", "description": "Open DIBBS RFQs and solicitations DLA got no bids on."},
    {"name": "Companies", "description": "CAGE code lookups."},
]
unknown = {t for ops in spec["paths"].values() for op in ops.values() for t in op.get("tags", [])} - {t["name"] for t in spec["tags"]}
if unknown:
    sys.exit(f"add {sorted(unknown)} to spec['tags'] in this script")

# Real responses captured from the API (examples/<operationId>.json), so the reference shows data, not nulls.
for ops in spec["paths"].values():
    for op in ops.values():
        for response in op.get("responses", {}).values():
            # ASP.NET also lists text/plain and text/json; the API answers JSON.
            if "application/json" in response.get("content", {}):
                response["content"] = {"application/json": response["content"]["application/json"]}
        example = ROOT / "examples" / f"{op.get('operationId')}.json"
        if example.exists():
            media = op.get("responses", {}).get("200", {}).get("content", {}).get("application/json")
            if media is None:
                sys.exit(f"{example.name}: {op['operationId']} has no 200 application/json response to attach it to")
            media["example"] = json.loads(example.read_text())

(ROOT / "openapi.json").write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n")
print(f"openapi.json: {len(spec['paths'])} paths from {source}")
