"""Oracle for creating authenticated Anthropic clients."""

import os
from typing import Any, Optional

from dotenv import load_dotenv


# Load `.env` automatically when the package is imported.
# This allows users to configure `ANTHROPIC_API_KEY` without exporting it manually.
load_dotenv()


def get_anthropic_client(api_key: Optional[str] = None) -> Any:
    """Return a configured Anthropic client.

    The API key is read from the provided value first, then falls back to the
    environment variable `ANTHROPIC_API_KEY` (populated from `.env` if present).

    Importing the `anthropic` package is deferred until runtime to allow the
    package to be imported in environments where the dependency is not installed
    (e.g., during unit tests).
    """

    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY must be set in your environment or .env file."
        )

    try:
        import anthropic  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "The 'anthropic' package is required to run the pipeline. "
            "Install it with `pip install -r requirements.txt`."
        ) from exc

    return anthropic.Anthropic(api_key=key)
