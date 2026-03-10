"""Configuration loader for the Delphi to Rust AI Orchestrator.

Configuration is loaded from `config.yml` by default, and is used to control
model selection, token limits, and output layout.
"""

from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_CONFIG: Dict[str, Any] = {
    "llm": {
        "model": "claude-2.1",
        "high_quality_model": "claude-3-5-sonnet-20241022",
        "temperature": 0.1,
        "translate_max_tokens": 1200,
        "tests_max_tokens": 800,
    },
    "paths": {
        "legacy_dir": "./legacy_delphi",
        "target_dir": "./src_rust",
        "rust_subdir": "src",
        "tests_subdir": "tests",
    },
}


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from YAML file.

    If the config file is missing or invalid, this returns sensible defaults.
    """

    path = Path(config_path or "config.yml")
    if not path.exists():
        return DEFAULT_CONFIG.copy()

    try:
        contents = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return DEFAULT_CONFIG.copy()

    merged = DEFAULT_CONFIG.copy()
    # Merge at shallow levels so missing keys still inherit defaults.
    for key, value in (contents or {}).items():
        if isinstance(value, dict) and key in merged:
            merged[key].update(value)
        else:
            merged[key] = value

    return merged
