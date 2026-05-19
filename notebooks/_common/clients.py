"""Pre-authenticated client factories. Entra ID only — no API keys.

All clients use DefaultAzureCredential, which works with `az login`,
managed identity, VS Code sign-in, GitHub Codespaces, etc.
"""

from __future__ import annotations

from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from .env import Config

# Two distinct Entra scopes — using the wrong one returns 401/404.
#  - Azure OpenAI resource (the *.openai.azure.com host) → cognitiveservices scope
#  - Foundry project (the *.services.ai.azure.com host)  → ai.azure.com scope
OPENAI_SCOPE = "https://cognitiveservices.azure.com/.default"
FOUNDRY_SCOPE = "https://ai.azure.com/.default"


def get_credential() -> DefaultAzureCredential:
    """Single DefaultAzureCredential instance — reuse across clients."""
    return DefaultAzureCredential()


def get_openai_client(cfg: Config, *, credential: DefaultAzureCredential | None = None):
    """Azure OpenAI client (openai SDK) bound to the resource's /openai/v1 surface.

    The SDK appends the /openai/v1 route automatically — pass only the resource hostname.
    Uses a bearer-token provider so tokens auto-refresh.
    """
    from openai import AzureOpenAI

    cred = credential or get_credential()
    token_provider = get_bearer_token_provider(cred, OPENAI_SCOPE)

    # Strip a trailing /openai/v1 if the user pasted the full v1 URL in .env — keep the helper forgiving.
    endpoint = cfg.azure_openai_endpoint.rstrip("/")
    if endpoint.endswith("/openai/v1"):
        endpoint = endpoint[: -len("/openai/v1")]

    return AzureOpenAI(
        azure_endpoint=endpoint,
        azure_ad_token_provider=token_provider,
        api_version="preview",
    )


def get_project_client(cfg: Config, *, credential: DefaultAzureCredential | None = None):
    """Foundry project client (azure-ai-projects v2)."""
    from azure.ai.projects import AIProjectClient

    cred = credential or get_credential()
    return AIProjectClient(endpoint=cfg.project_endpoint, credential=cred)


def get_project_openai_client(cfg: Config, *, credential: DefaultAzureCredential | None = None):
    """OpenAI-compatible client routed through the Foundry project.

    Use this when you want the Responses API to address Foundry-direct models
    or use server-side agent_reference. The project handles auth scoping.
    """
    project = get_project_client(cfg, credential=credential)
    return project.get_openai_client()
