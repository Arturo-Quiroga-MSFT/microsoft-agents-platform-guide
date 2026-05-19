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
    """OpenAI-compatible client bound to the Azure OpenAI v1 GA surface.

    Uses the plain `OpenAI` client (not `AzureOpenAI`) because `AzureOpenAI` still
    inserts `/deployments/{name}/` into the path even when given a v1 base_url —
    which yields 404 on the new GA route. The plain client posts to
    `/openai/v1/chat/completions` with the deployment name in the `model` field.

    Auth is via Entra bearer token; we wrap a token provider so tokens refresh
    on every request rather than going stale after an hour.
    """
    from openai import OpenAI

    cred = credential or get_credential()
    token_provider = get_bearer_token_provider(cred, OPENAI_SCOPE)

    endpoint = cfg.azure_openai_endpoint.rstrip("/")
    if not endpoint.endswith("/openai/v1"):
        endpoint = f"{endpoint}/openai/v1"
    base_url = endpoint + "/"

    # Custom httpx client that injects a fresh bearer token on every request.
    import httpx

    class _BearerAuth(httpx.Auth):
        def auth_flow(self, request):
            request.headers["Authorization"] = f"Bearer {token_provider()}"
            yield request

    return OpenAI(
        base_url=base_url,
        api_key="unused-entra-id-only",  # required by SDK constructor; overridden by auth below
        http_client=httpx.Client(auth=_BearerAuth()),
        default_query={"api-version": "preview"},
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
