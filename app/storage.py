from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path
from typing import Any

from .config import DATA_DIR


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def new_project_dir(prefix: str = "project") -> Path:
    ensure_data_dir()
    project_id = f"{prefix}_{uuid.uuid4().hex[:10]}"
    project_dir = DATA_DIR / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "uploads").mkdir(exist_ok=True)
    (project_dir / "frames").mkdir(exist_ok=True)
    (project_dir / "faces").mkdir(exist_ok=True)
    return project_dir


def save_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def list_projects() -> list[str]:
    ensure_data_dir()
    return sorted([p.name for p in DATA_DIR.iterdir() if p.is_dir()], reverse=True)


def copy_into_project(src: Path, project_dir: Path, name: str | None = None) -> Path:
    target = project_dir / "uploads" / (name or src.name)
    shutil.copy2(src, target)
    return target
