"""Environment + configuration loader.

Every notebook starts with:

    from _common.env import load_env
    cfg = load_env()
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def _find_repo_root(start: Path) -> Path:
    for parent in (start, *start.parents):
        if (parent / ".git").exists() or (parent / ".env.example").exists():
            return parent
    return start


@dataclass(frozen=True)
class Config:
    project_endpoint: str
    azure_openai_endpoint: str
    model_deployment: str
    reasoning_effort: str
    app_insights_connection_string: str | None

    def __repr__(self) -> str:  # readable in notebook output, hides nothing sensitive
        return (
            "Config(\n"
            f"  project_endpoint        = {self.project_endpoint!r},\n"
            f"  azure_openai_endpoint   = {self.azure_openai_endpoint!r},\n"
            f"  model_deployment        = {self.model_deployment!r},\n"
            f"  reasoning_effort        = {self.reasoning_effort!r},\n"
            f"  app_insights_configured = {self.app_insights_connection_string is not None}\n"
            ")"
        )


def load_env() -> Config:
    """Load .env from the repo root and return a typed Config."""
    repo_root = _find_repo_root(Path.cwd())
    env_path = repo_root / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=False)
    else:
        # still read environment in case the user exported vars manually
        load_dotenv(override=False)

    def _require(name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise RuntimeError(
                f"Missing required env var: {name}. "
                f"Copy {repo_root / '.env.example'} to {env_path} and fill it in."
            )
        return value

    return Config(
        project_endpoint=_require("PROJECT_ENDPOINT"),
        azure_openai_endpoint=_require("AZURE_OPENAI_ENDPOINT"),
        model_deployment=_require("MODEL_DEPLOYMENT"),
        reasoning_effort=os.getenv("REASONING_EFFORT", "low"),
        app_insights_connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"),
    )
