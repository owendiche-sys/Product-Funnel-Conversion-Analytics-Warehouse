from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "config" / "project_config.json"


def load_config() -> dict[str, Any]:
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def project_path(relative_path: str) -> Path:
    return ROOT_DIR / relative_path


def database_path() -> Path:
    return project_path(load_config()["database_path"])


def raw_data_dir() -> Path:
    return project_path(load_config()["raw_data_dir"])


def model_dir() -> Path:
    path = project_path(load_config()["model_dir"])
    path.mkdir(parents=True, exist_ok=True)
    return path


def report_dir() -> Path:
    path = project_path(load_config()["report_dir"])
    path.mkdir(parents=True, exist_ok=True)
    return path
