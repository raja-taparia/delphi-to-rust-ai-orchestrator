"""Translation helpers that call the Anthropic API.

This module keeps the LLM interaction isolated from the orchestration logic.
"""

from typing import Any

from .prompts import RUST_SYSTEM_PROMPT


def translate_to_rust(
    client: Any,
    delphi_code: str,
    module_name: str,
    *,
    model: str,
    max_tokens: int,
    temperature: float,
) -> str:
    """Call the LLM to translate Delphi business logic into idiomatic Rust.

    This function does not hardcode model/token defaults; the caller is
    responsible for providing configuration (e.g. from config.yml).
    """

    print(f"🚀 Initializing AI-Assisted Extraction for module: {module_name}...")

    prompt = (
        "Translate the following Delphi network polling logic to Rust. Preserve all business logic.\n\n"
        f"Code:\n{delphi_code}"
    )

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=RUST_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    content = response.content
    if isinstance(content, list):
        content = content[0]

    if hasattr(content, "text"):
        return content.text
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        return content.get("text") or content.get("message") or str(content)

    return str(content)


def generate_golden_master_tests(
    client: Any,
    rust_code: str,
    *,
    model: str,
    max_tokens: int,
    temperature: float,
) -> str:
    """Generate characterization tests to ensure zero-regression."""

    print("🛡️ Generating Golden Master / Characterization Tests...")

    prompt = (
        "Generate exhaustive Rust unit tests for the following code to ensure 1:1 input/output parity "
        "with the legacy system:\n\n"
        f"{rust_code}"
    )

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )

    content = response.content
    if isinstance(content, list):
        content = content[0]

    if hasattr(content, "text"):
        return content.text
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        return content.get("text") or content.get("message") or str(content)

    return str(content)
