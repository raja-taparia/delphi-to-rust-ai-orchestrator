"""Orchestration pipeline for the Delphi to Rust AI modernization project."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Optional

from .client import get_anthropic_client
from .config import load_config
from .legacy import read_legacy_module
from .translator import generate_golden_master_tests, translate_to_rust


def _discover_legacy_units(legacy_dir: str) -> Iterable[Path]:
    """Discover legacy Delphi source units in a directory."""

    base = Path(legacy_dir)
    if not base.exists() or not base.is_dir():
        return []

    # Common Delphi extensions. This can be expanded as needed.
    return sorted(base.glob("**/*.[pP][aA][sS]"))


def _write_output(
    base_dir: str,
    module_name: str,
    rust_code: str,
    tests: str,
    rust_subdir: str | None = "src",
    tests_subdir: str | None = "tests",
) -> None:
    """Write generated Rust + test artifacts to disk.

    The output structure is configurable so that projects can keep generated
    source and tests in separate directories.
    """

    base = Path(base_dir)
    base.mkdir(parents=True, exist_ok=True)

    if rust_subdir:
        rust_path_parent = base / rust_subdir
    else:
        rust_path_parent = base

    if tests_subdir:
        test_path_parent = base / tests_subdir
    else:
        test_path_parent = base

    rust_path_parent.mkdir(parents=True, exist_ok=True)
    test_path_parent.mkdir(parents=True, exist_ok=True)

    rust_path = rust_path_parent / f"{module_name}.rs"
    test_path = test_path_parent / f"{module_name}_golden_tests.rs"

    rust_path.write_text(rust_code, encoding="utf-8")
    test_path.write_text(tests, encoding="utf-8")

    print(f"✅ Wrote: {rust_path} and {test_path}")


def execute_pipeline(
    legacy_dir: Optional[str] = None,
    target_dir: Optional[str] = None,
    api_key: Optional[str] = None,
    write_output: bool = True,
    rust_subdir: Optional[str] = "src",
    tests_subdir: Optional[str] = "tests",
    config_path: Optional[str] = None,
    translate_func: Callable[..., str] = translate_to_rust,
    tests_func: Callable[..., str] = generate_golden_master_tests,
) -> None:
    """Run the end-to-end modernization pipeline.

    This is intentionally a lightweight orchestrator for demonstration purposes.

    Args:
        legacy_dir: Path containing legacy Delphi sources.
        target_dir: Path where Rust sources will be emitted.
        api_key: Optional Anthropic API key; falls back to `ANTHROPIC_API_KEY`.
        write_output: If True, writes generated artifacts to disk.
        rust_subdir: Subdirectory under `target_dir` for generated Rust.
        tests_subdir: Subdirectory under `target_dir` for generated tests.
        config_path: Optional path to a YAML configuration file.
        translate_func: Callable to translate Delphi -> Rust (injected for testing).
        tests_func: Callable to generate test output (injected for testing).
    """

    config = load_config(config_path)

    # Apply default values from config if not explicitly provided.
    legacy_dir = legacy_dir or config["paths"]["legacy_dir"]
    target_dir = target_dir or config["paths"]["target_dir"]
    rust_subdir = rust_subdir or config["paths"]["rust_subdir"]
    tests_subdir = tests_subdir or config["paths"]["tests_subdir"]

    client = get_anthropic_client(api_key)

    print("--- Starting Delphi to Rust Migration Pipeline ---")

    units = list(_discover_legacy_units(legacy_dir))
    if not units:
        print("⚠️  No legacy Delphi sources found. Falling back to a mocked example.")
        units = [Path("mocked_ping_sensor.pas")]

    llm_cfg = config.get("llm", {})
    model = llm_cfg.get("model")
    fallback_models = llm_cfg.get("fallback_models", []) or []
    temperature = llm_cfg.get("temperature")
    translate_max_tokens = llm_cfg.get("translate_max_tokens")
    tests_max_tokens = llm_cfg.get("tests_max_tokens")

    try:
        from anthropic import NotFoundError
    except Exception:
        NotFoundError = Exception

    for unit_path in units:
        module_name = unit_path.stem

        if unit_path.exists():
            legacy_code = read_legacy_module(str(unit_path))
        else:
            legacy_code = """
            unit PingSensor;
            interface
            uses SysUtils, Classes, IdIcmpClient;
            function ExecutePing(IP: string): Integer;
            implementation
            function ExecutePing(IP: string): Integer;
            begin
              // Legacy synchronous ping logic
              Result := 42; // ms response
            end;
            end.
            """

        # 1. Extract & Analyze
        def _call_translate(model_name: str):
            return translate_func(
                client,
                legacy_code,
                module_name,
                model=model_name,
                max_tokens=translate_max_tokens,
                temperature=temperature,
            )

        # 1. Extract & Analyze
        try:
            rust_translation = _call_translate(model)
        except NotFoundError as err:
            # If the configured model is not available, try fallbacks.
            if not fallback_models:
                raise RuntimeError(
                    "Model not found. Please update `config.yml` with a model that exists in your Anthropic account. "
                    f"Error: {err}"
                ) from err

            last_err = err
            for alt in fallback_models:
                try:
                    print(f"⚠️  Model '{model}' not found; trying fallback '{alt}'...")
                    rust_translation = _call_translate(alt)
                    model = alt
                    break
                except NotFoundError as err2:
                    last_err = err2
            else:
                raise RuntimeError(
                    "None of the configured models were available. Please update `config.yml` with a valid model. "
                    f"Last error: {last_err}"
                ) from last_err

        # 2. Generate Validation Guardrails
        tests = tests_func(
            client,
            rust_translation,
            model=model,
            max_tokens=tests_max_tokens,
            temperature=temperature,
        )

        # 3. Write to target directory (default behavior)
        if write_output:
            _write_output(
                target_dir,
                module_name,
                rust_translation,
                tests,
                rust_subdir=rust_subdir,
                tests_subdir=tests_subdir,
            )

    print("\n✅ AI Extraction Complete. Ready for Human Architectural Review.")
    print("Preview of generated Rust (Async Tokio implementation):")
    print("-" * 40)
    print("use tokio::net::TcpStream;\nuse std::net::SocketAddr;\n\npub async fn execute_ping(ip: &str) -> Result<u32, Error> {... }")
