#!/usr/bin/env python3
"""Generate src/data.generated.js from data/*.json.

Why this exists: opening index.html from disk (file://) blocks fetch() of local
JSON by CORS, and a fetch failure at demo time looks like a bug in front of
judges. Generating an ES module removes the network entirely — the game runs
from any static host AND from a plain file:// open.

Run after any change to data/*.json:
    python scripts/build_data.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "src" / "data.generated.js"

FILES = {
    "instruments": "instruments.json",
    "orbits": "orbits.json",
    "launchers": "launch_vehicles.json",
    "events": "events.json",
    "scenarios": "scenarios.json",
}

parts = []
for key, filename in FILES.items():
    with open(DATA / filename, encoding="utf-8") as f:
        raw = json.load(f)
    parts.append(f"  {key}: {json.dumps(raw, ensure_ascii=False, indent=2)}")

header = (
    "// AUTO-GENERATED — do not edit. Source of truth: data/*.json\n"
    "// Regenerate: python scripts/build_data.py\n"
    "export const DATA = {\n"
)
OUT.write_text(header + ",\n".join(parts) + "\n};\n", encoding="utf-8")
print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size} bytes)")
