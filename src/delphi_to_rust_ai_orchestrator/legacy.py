"""Helpers for reading/parsing legacy Delphi source artifacts."""

from pathlib import Path


def read_legacy_module(file_path: str) -> str:
    """Read a legacy Delphi source file.

    This is currently a thin wrapper around file I/O; future work can add AST
    parsing, tokenization, or other extraction logic.
    """

    return Path(file_path).read_text(encoding="utf-8")
