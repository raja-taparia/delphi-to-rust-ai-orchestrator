"""Delphi to Rust AI Orchestrator package.

This package provides a lightweight, opinionated orchestration layer for
migrating legacy Delphi code to Rust via an LLM (Anthropic Claude).

The project is intentionally minimal to keep the focus on the core pipeline
logic, while still being structured for easy extension.
"""

from .pipeline import execute_pipeline

__all__ = ["execute_pipeline"]
