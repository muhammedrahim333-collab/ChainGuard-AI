from __future__ import annotations

import json
from pathlib import Path

from models.supplier import Supplier


def load_demo_suppliers(base_dir: Path | None = None) -> list[Supplier]:
    root = base_dir or Path(__file__).resolve().parents[1]
    path = root / "data" / "sample_suppliers.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [Supplier(**item) for item in payload]


def custom_suppliers_path(base_dir: Path | None = None) -> Path:
    root = base_dir or Path(__file__).resolve().parents[1]
    return root / "data" / "custom_suppliers.json"


def load_all_suppliers(base_dir: Path | None = None) -> list[Supplier]:
    root = base_dir or Path(__file__).resolve().parents[1]
    suppliers = load_demo_suppliers(root)
    extra_path = custom_suppliers_path(root)
    if extra_path.exists():
        payload = json.loads(extra_path.read_text(encoding="utf-8"))
        suppliers.extend(Supplier(**item) for item in payload)
    return suppliers


def save_custom_supplier(supplier: Supplier, base_dir: Path | None = None) -> None:
    root = base_dir or Path(__file__).resolve().parents[1]
    path = custom_suppliers_path(root)
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))
    else:
        payload = []
    payload.append(supplier.model_dump())
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
