"""Entry point to run the orchestrator as a module."""

import argparse

from .pipeline import execute_pipeline


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m delphi_to_rust_ai_orchestrator",
        description="Orchestrate legacy Delphi -> Rust migrations using an LLM.",
    )

    parser.add_argument(
        "--legacy-dir",
        default="./legacy_delphi",
        help="Path to directory containing Delphi source files.",
    )
    parser.add_argument(
        "--target-dir",
        default="./src_rust",
        help="Base output directory for generated artifacts.",
    )
    parser.add_argument(
        "--rust-dir",
        default=None,
        help="Optional subdirectory (or absolute path) for generated Rust source files.",
    )
    parser.add_argument(
        "--tests-dir",
        default=None,
        help="Optional subdirectory (or absolute path) for generated test files.",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="Optional Anthropic API key. Defaults to $ANTHROPIC_API_KEY.",
    )
    parser.add_argument(
        "--config",
        default="config.yml",
        help="Optional path to a YAML config file.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the pipeline without writing generated artifacts to disk.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    execute_pipeline(
        legacy_dir=args.legacy_dir,
        target_dir=args.target_dir,
        api_key=args.api_key,
        write_output=not args.dry_run,
        rust_subdir=args.rust_dir,
        tests_subdir=args.tests_dir,
        config_path=args.config,
    )
