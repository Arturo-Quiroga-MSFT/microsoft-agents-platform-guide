# Azure OpenAI API Quick Reference (2026)

> **Last updated: 2026-03-22** — synced with [API version lifecycle](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/api-version-lifecycle?view=foundry), [supported languages](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/supported-languages?view=foundry&pivots=programming-language-python), and [migration guide](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/migrate) docs.

A concise comparison of the main API surfaces for Azure OpenAI usage in Microsoft Foundry.

## API Surface Summary

| API | Endpoint Pattern | Use Case | State | SDK |
|---|---|---|---|---|
| **Chat Completions** | `/openai/v1/chat/completions` | Lightweight stateless chat | Client-managed | `openai` (Python) |
| **Responses** | `/openai/v1/responses` | Modern unified chat + features | Optional server-side | `openai` (Python) |
| **Foundry Agent Service** | `/agents/...`, `/conversations/...` | Production agents with orchestration | Server-managed (Cosmos DB) | `azure-ai-projects` v2 (via `AIProjectClient`) |

## Decision Tree

```
Do you need stateful agents with tool orchestration and enterprise governance?
├─ YES → Use Foundry Agent Service
└─ NO → Are you building a new app that needs the latest features?
    ├─ YES → Use Responses API
    └─ NO → Use Chat Completions API (simple and familiar)
```

## Code Patterns at a Glance

### Chat Completions (stateless)

```python
from openai import OpenAI

client = OpenAI()  # uses env vars

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hello!"},
    ],
)

print(completion.choices[0].message.content)
```

### Responses (modern unified)

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-4.1-nano",
    input="Hello!",
)

print(response.output_text)
```

### Foundry Agent Service (stateful agents)

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:
    agents_client = project_client.agents
    
    agent = agents_client.create_agent(
        model="gpt-4o",
        name="my-agent",
        instructions="You are helpful",
    )
    
    thread = agents_client.threads.create()
    
    agents_client.messages.create(
        thread_id=thread.id,
        role="user",
        content="Hello!",
    )
    
    run = agents_client.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id,
    )
    
    messages = agents_client.messages.list(thread_id=thread.id)
```

## Environment Setup

### For Chat Completions & Responses (OpenAI v1 API)

```bash
export OPENAI_BASE_URL="https://YOUR-RESOURCE-NAME.openai.azure.com/openai/v1/"
export OPENAI_API_KEY="your-api-key"
```

Or use Microsoft Entra ID:

```python
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://ai.azure.com/.default"
)

client = OpenAI(
    base_url="https://YOUR-RESOURCE-NAME.openai.azure.com/openai/v1/",
    api_key=token_provider,
)
```

### For Foundry Agent Service

```bash
export PROJECT_ENDPOINT="https://YOUR-PROJECT.api.azureml.ms"
export MODEL_DEPLOYMENT_NAME="gpt-4o"
```

Use Microsoft Entra ID (API keys not recommended):

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)
```

## Feature Matrix

| Feature | Chat Completions | Responses | Agent Service |
|---|---|---|---|
| **Stateless chat** | ✅ | ✅ | ✅ |
| **Server-side state** | ❌ | Optional (conversations) | ✅ (conversations in Cosmos) |
| **Tool orchestration** | Manual | Server-side | Server-side + retry |
| **MCP tools (remote)** | ❌ | ✅ (GA) | ✅ (GA) |
| **Multi-agent coordination** | ❌ | ❌ | ✅ (incl. A2A preview) |
| **Content filters** | ✅ | ✅ | ✅ (enforced by default) |
| **Enterprise RBAC** | ✅ | ✅ | ✅ (built-in) |
| **Observability** | Basic | Basic | Full (traces, logs, App Insights) |
| **Reasoning options** | ✅ | ✅ | ✅ |
| **Image generation** | ❌ | ✅ (GA) | ✅ |
| **Response chaining** | ❌ | ✅ (`previous_response_id`) | N/A |
| **Server-side retrieve/delete** | ❌ | ✅ (30-day retention) | N/A |
| **Async background tasks** | ❌ | ✅ | N/A |
| **Multi-provider models** (DeepSeek, Grok) | ✅ | ✅ | ✅ |

## API Version Notes

### OpenAI v1 GA (Chat Completions & Responses)

- **Base URL**: `/openai/v1` — two equivalent forms:
  - `https://YOUR-RESOURCE-NAME.openai.azure.com/openai/v1/`
  - `https://YOUR-RESOURCE-NAME.services.ai.azure.com/openai/v1/`
- **No `api-version` required** (GA features)
- **Preview features**: opt-in via feature-specific headers or path segments
- **Status**: Generally Available (since August 2025)

#### v1 API endpoint status (Mar 2026)

| API Path | Status |
|---|---|
| `/openai/v1/chat/completions` | GA |
| `/openai/v1/embeddings` | GA |
| `/openai/v1/evals` | **GA** (previously required `"aoai-evals":"preview"` header; no longer needed) |
| `/openai/v1/files` | GA |
| `/openai/v1/fine_tuning/` | GA |
| `/openai/v1/models` | GA |
| `/openai/v1/responses` | **GA** |
| `/openai/v1/vector_stores` | GA |
| `/openai/v1/audio/speech` | Preview — requires `api-version=preview` query param |
| `/openai/v1/fine_tuning/.../copy` | Preview — requires header `"aoai-copy-ft-checkpoints":"preview"` |
| `/openai/v1/fine_tuning/alpha/graders/` | Preview (path signals preview; no extra header needed) |

### Agent Service

- **Endpoint**: Project-level (not model-level)
- **SDK**: `azure-ai-projects` v2 (via `AIProjectClient`); `azure-ai-agents` is deprecated
- **Status**: Generally Available (GA), with new developer experience (conversations/responses pattern)
- **State storage**: Server-side, backed by Cosmos DB (single-tenant; bring-your-own for BCDR)
- **API pattern**: Classic `threads/runs/messages` is supported for compatibility; new API uses `conversations` and `responses` (OpenAI Responses protocol)
- **Control plane**: GA `2025-06-01`, Preview `2025-07-01-preview`

## When to Migrate

### From Assistants API → Agent Service

If you're using Azure OpenAI **Assistants API** (preview), migrate to **Foundry Agent Service** (GA) for:
- Better enterprise features
- Improved tool orchestration
- Full observability and governance

### From Classic Agent Service → New Agent Developer Experience

Microsoft released a new Foundry Agent Service API that replaces the classic threads/runs/messages pattern:

| Classic (old) | New API | Details |
|---|---|---|
| `threads` | `conversations` | Supports streams of items, not only messages |
| `runs` | `responses` | Uses OpenAI Responses protocol; tool-call loops are explicitly managed |
| `assistants` / `agents` | `agents (new)` | Prompt agents, workflow agents, hosted agents with stateful context |

See the [official migration guide](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/migrate) for details.

> **Deadline**: Standard deployments on the old platform are retiring by March 31, 2026.
- Active support and feature updates

### From Chat Completions → Responses

Consider migrating if you:
- Want the latest features (remote MCP, async background tasks, image generation, response chaining)
- Need a unified API surface for chat + assistants-style features
- Are starting a new project

> **Note**: Both Chat Completions and Responses API now support **multi-provider models** (DeepSeek R1 / MAI-DS-R1, Grok) deployed in your Foundry resource alongside Azure OpenAI models.

### From Responses → Agent Service

Migrate if you need:
- Production-grade orchestration
- Multi-agent coordination
- Enterprise trust & safety requirements
- Server-side state management with full observability

## Links

- [SDK Overview (Foundry SDK, OpenAI SDK, Foundry Tools)](sdk-overview.md)
- [Chat Completions vs Responses Guide](chat-vs-responses.md)
- [Foundry Agent Service: Which API to Use?](agents-and-apis.md)
- [API Version Lifecycle (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/api-version-lifecycle?view=foundry)
- [Supported Languages (Python)](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/supported-languages?view=foundry&tabs=dotnet-secure%2Csecure%2Cpython-entra&pivots=programming-language-python)
- [Agent Service Overview](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview?view=foundry)
