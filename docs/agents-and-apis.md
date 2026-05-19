# Microsoft Foundry Agent Service: Which API to Use?

> **Last updated: 2026-05-19** — synced with [Foundry Agent Service overview](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview) and [migration guide](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/migrate) docs.

This guide clarifies which Azure OpenAI API surfaces (Chat Completions, Responses, or Assistants) you should use when working with **Microsoft Foundry Agent Service**.

## TL;DR

**Microsoft Foundry Agent Service has a new developer experience** that replaces the classic threads/runs/messages pattern with a conversations/responses pattern built on the OpenAI Responses protocol.

- **New Agent Service SDK**: `azure-ai-projects` **2.x** (Python) — uses `project.get_openai_client()` for conversations and responses; agent creation/versioning stays on the project client (`project.agents.create_version()` with a `PromptAgentDefinition`). **Incompatible with 1.x**.
- **Three agent types**: **Prompt agents** (GA, no-code or via SDK/REST), **Workflow agents** (preview, YAML or visual builder for multi-step orchestration), **Hosted agents** (preview, your code in a container built with Agent Framework or LangGraph).
- **Classic pattern** (`azure-ai-agents` / Projects 1.x with `threads.create()`, `runs.create()`): kept available under Foundry Classic but receives no new features.
- **Not for direct use with agents**: Chat Completions API or Responses API are not called directly when using Agent Service (Agent Service wraps Responses internally).

- **Key Takeaway**: Microsoft Foundry Agent Service is a separate orchestration platform. The new API uses conversations and responses (OpenAI Responses protocol) for server-side agent orchestration, storing state in single-tenant Cosmos DB. This is distinct from the stateless Chat Completions API and unified Responses API, which are for direct model interaction.

## What is Microsoft Foundry Agent Service?

Foundry Agent Service is a **production-ready platform** for building and deploying intelligent agents with:

- **Stateful conversations** (conversation history managed server-side in Cosmos DB)
- **Tool orchestration** (automatic tool call execution and retry)
- **Enterprise trust & safety** (content filters, RBAC, network isolation)
- **Multi-agent coordination** (agent-to-agent messaging via A2A protocol, preview)
- **Full observability** (traces, logs, Application Insights integration)
- **Agent types**: prompt agents, workflow agents (preview), hosted agents (preview)
- **Publishing**: Expose agents as stable endpoints via Responses protocol or Activity Protocol; share through Teams, M365 Copilot, Entra Agent Registry

It's positioned as Microsoft's recommended approach for building agents, replacing the older Azure OpenAI Assistants API (preview).

> **Terminology note**: The new Foundry Agent Service documentation uses **"conversations"** (replacing "threads") and **"responses"** (replacing "runs"). The classic `threads/runs/messages` API paths are still supported for compatibility.

## Agent Service API Patterns

### New pattern: Conversations and Responses (v2 SDK)

The new developer experience uses the OpenAI client (obtained from the project client) for conversations and responses. Agent creation and versioning remain on the project client.

```python
import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity import DefaultAzureCredential

# Format: https://<resource-name>.ai.azure.com/api/projects/<project-name>
project = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# 1. Create a versioned prompt agent
agent = project.agents.create_version(
    agent_name="my-agent",
    definition=PromptAgentDefinition(
        model="gpt-5-mini",
        instructions="You are a helpful assistant.",
    ),
)
print(f"Agent created (id={agent.id}, version={agent.version})")

# 2. Chat with the agent via the OpenAI client + Responses API
openai = project.get_openai_client()
conversation = openai.conversations.create()

response = openai.responses.create(
    conversation=conversation.id,
    extra_body={"agent_reference": {"name": "my-agent", "type": "agent_reference"}},
    input="What is the size of France in square miles?",
)
print(response.output_text)

# Follow-up in the same conversation
response = openai.responses.create(
    conversation=conversation.id,
    extra_body={"agent_reference": {"name": "my-agent", "type": "agent_reference"}},
    input="And what is the capital city?",
)
print(response.output_text)
```

### Classic pattern: Threads, Runs, Messages (v1 SDK)

The classic pattern is still supported for compatibility but receives no new features.

```python
import os
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
        instructions="You are a helpful assistant",
    )

    thread = agents_client.threads.create()

    message = agents_client.messages.create(
        thread_id=thread.id,
        role="user",
        content="Hello, tell me a joke",
    )

    run = agents_client.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id,
    )

    messages = agents_client.messages.list(thread_id=thread.id)
    for msg in messages:
        if msg.text_messages:
            print(f"{msg.role}: {msg.text_messages[-1].text.value}")
```

> **Migration note**: `create_agent()` was removed in SDK v2.0.0. Replace with `create_version()` and pass a `PromptAgentDefinition` object. See the [migration guide](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/migrate) for details.

## Comparison: Agent Service vs Chat Completions vs Responses

| Aspect | Agent Service | Chat Completions | Responses API |
|---|---|---|---|
| **Use case** | Production agents with orchestration, state, tools, and governance | Simple stateless chat | Unified chat + assistants-style features |
| **State management** | Server-side (conversations stored in Cosmos DB) | Client-side (you manage history) | Mixed (can use conversation objects) |
| **Tool orchestration** | Automatic server-side execution + retry | Manual (you handle tool calls) | Server-side (similar to Agent Service) |
| **API pattern** | `conversations`, `responses` (new); `agents`, `threads`, `runs` (classic) | `chat.completions.create(messages=[...])` | `responses.create(input=...)` |
| **When to use** | Building production agents with enterprise requirements | Lightweight chat, simple Q&A | Modern chat apps, prototypes needing latest features |
| **SDK** | `azure-ai-projects` v2 (via `AIProjectClient` + `get_openai_client()`) | OpenAI SDK (`openai` package) | OpenAI SDK (`openai` package) |
| **Endpoint style** | `/agents/...`, `/conversations/...` | `/openai/v1/chat/completions` | `/openai/v1/responses` |

## Why Agent Service is NOT Chat Completions or Responses

### 1. Different API surfaces

- **Agent Service (new)**: uses conversations and responses via the OpenAI client obtained from `project.get_openai_client()`.
- **Agent Service (classic)**: uses a dedicated Agent API with operations like `create_agent`, `threads.create`, `runs.create_and_process`.
- **Chat Completions / Responses**: direct inference APIs that take a prompt and return text.

### 2. Server-side vs client-side orchestration

- **Agent Service**: handles tool calls, retries, and state management server-side.
- **Chat Completions**: you manually parse tool calls and manage conversation history.
- **Responses**: offers server-side orchestration but is not the same as Agent Service (different endpoints and patterns).

### 3. Enterprise features built-in

Agent Service includes:
- Structured **conversation objects** (not just message arrays)
- Automatic **tool orchestration** and **retry logic**
- **Content filters** and **RBAC** integration
- **Bring-your-own storage** (Cosmos DB, AI Search, VNets) — single-tenant Cosmos DB for state (required for BCDR)
- **Application Insights** and **trace logging** out of the box

These are not part of Chat Completions or Responses APIs.

## Agent Tool Availability

The new Foundry Agent Service supports a broader set of tools:

| Tool | Foundry (classic) | Foundry (new) |
|---|---|---|
| Agent to Agent (A2A) | ❌ | ✅ (Public Preview) |
| Azure AI Search | ✅ (GA) | ✅ (GA) |
| Browser Automation | ✅ (Public Preview) | ✅ (Public Preview) |
| Code Interpreter | ✅ (GA) | ✅ (GA) |
| Computer Use | ✅ (Public Preview) | ✅ (Public Preview) |
| Fabric Data Agent | ✅ (Public Preview) | ✅ (Public Preview) |
| File Search | ✅ (GA) | ✅ (GA) |
| Function | ✅ (GA) | ✅ (GA) |
| Grounding with Bing Search | ✅ (GA) | ✅ (GA) |
| Image Generation | ❌ | ✅ (Public Preview) |
| MCP | ✅ (Public Preview) | ✅ (GA) |
| OpenAPI | ✅ (GA) | ✅ (GA) |
| SharePoint Grounding | ✅ (Public Preview) | ✅ (Public Preview) |
| Web Search | ❌ | ✅ (Public Preview) |

## Migration: Classic Agent Service → New Developer Experience

Microsoft released a **new Foundry Agent Service API** that replaces the classic threads/runs/messages pattern.

### Key changes

| Classic (old) | New API | Details |
|---|---|---|
| `threads` | `conversations` | Supports streams of items, not only messages |
| `runs` | `responses` | Uses OpenAI Responses protocol; tool-call loops are explicitly managed |
| `assistants` / `agents` | `agents (new)` | Prompt agents, workflow agents, hosted agents with stateful context |
| `create_agent()` | `create_version()` | Pass a `PromptAgentDefinition` object |
| `azure-ai-agents` SDK | `azure-ai-projects` v2 | Unified package; `azure-ai-agents` dependency dropped |
| `project.agents.*` | `project.get_openai_client()` | Conversations/responses use the OpenAI client; agent creation stays on project client |

> **Deadline**: Standard deployments on the old platform are retiring by March 31, 2026. See the [migration guide](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/migrate).

The new Agent Service maintains **backward compatibility** with the threads/runs/messages pattern while adding new capabilities.

## Hosted Agents

**Hosted agents (preview)** are code-based agents built with a framework of your choice (**[Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/?pivots=programming-language-python)**, LangGraph, or your own code) and deployed as containers to Foundry Agent Service. You own the orchestration logic; Foundry manages the runtime, scaling, identity, and infrastructure.

> [!TIP]
> **MAF is the recommended path** for code-first agents on Foundry. Any `Agent` or `Workflow` you build with `agent-framework` (Python) or `Microsoft.Agents.AI` (.NET) can be promoted to a Foundry Hosted Agent with ~2 extra lines of hosting code. See the [MAF section in the SDK Overview](sdk-overview.md#microsoft-agent-framework-maf) and the [foundry-hosted-agents samples](https://github.com/microsoft/agent-framework/tree/main/python/samples/04-hosting/foundry-hosted-agents).

Key capabilities:

- **Durable conversations** — Foundry creates conversation objects with unique IDs; previous messages, tool calls, outputs, and metadata persist across sessions.
- **Dedicated agent identity** — each agent can have its own Microsoft Entra identity for scoped resource access; supports OAuth On-Behalf-Of (OBO) passthrough to downstream APIs and MCP servers.
- **BYO VNet** — each session runs in a VM-isolated sandbox connected to your Azure Virtual Network.
- **Built-in lifecycle** — build/push to ACR, register an agent version, poll until `active`, then invoke the dedicated endpoint.

Deploy via the Azure Developer CLI (`azd`) or VS Code extension for the fastest path, or via the Python SDK / REST API for programmatic control. See the [hosted agents quickstart](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/quickstart-hosted-agent) and [deploy a hosted agent](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/deploy-hosted-agent).

## Toolbox (preview)

**Toolbox** lets you define a curated set of tools once, manage them centrally in Foundry, and expose them through a single MCP-compatible endpoint. Any MCP-compatible agent runtime or client can consume a toolbox, regardless of framework. Toolbox versioning gives you explicit control over when changes propagate: create a new version, test it, then promote it to default.

## Agent Applications (Publishing)

Agents can be published as **Agent Applications** with stable endpoints:

- **Responses protocol**: OpenAI-compatible endpoint at `https://{accountName}.services.ai.azure.com/api/projects/{projectName}/applications/{applicationName}/protocols/openai`
- **Activity Protocol**: Azure Bot Service protocol for Teams/M365 integration
- **Authentication**: Microsoft Entra ID (RBAC) or Channels (Azure Bot Service). API key auth is **not** supported for applications.

Publish to Microsoft Teams, M365 Copilot, and the Entra Agent Registry.

## When to Use What?

### Use **Foundry Agent Service** when:
- Building production agents with state, tools, and governance
- Need multi-agent orchestration (including A2A protocol)
- Require enterprise trust & safety (content filters, RBAC, network isolation)
- Want server-side tool orchestration and automatic retries
- Need full conversation visibility and tracing
- Want to publish agents to Teams, M365 Copilot, or as stable API endpoints

> **Getting started**: [Quickstart: Get started with agents in code](https://learn.microsoft.com/en-us/azure/foundry/quickstarts/get-started-code) or [Build a hosted agent](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/quickstart-hosted-agent).

### Use **Responses API** when:
- Building modern chat apps or prototypes
- Want the latest features (e.g., MCP tools, reasoning options)
- Need a unified API surface for chat + assistants-style features
- Don't need the full enterprise orchestration of Agent Service

### Use **Chat Completions API** when:
- Building lightweight stateless chat flows
- Already have code using `messages[]` / `choices[]` pattern
- Don't need server-side orchestration or state management
- Working on simple Q&A or text generation tasks

## Code Example: Agent Service vs Responses API

### Agent Service (new pattern, stateful, orchestrated)

```python
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

openai = project.get_openai_client()
conversation = openai.conversations.create()

response = openai.responses.create(
    conversation=conversation.id,
    extra_body={"agent_reference": {"name": "my-agent", "type": "agent_reference"}},
    input="Hello!",
)
print(response.output_text)
```

### Agent Service (classic pattern)

```python
import os
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

### Responses API (stateless or use conversation objects)

```python
from openai import OpenAI

client = OpenAI(
    api_key="...",
    base_url="https://YOUR-RESOURCE-NAME.openai.azure.com/openai/v1/",
)

# Simple one-shot call
response = client.responses.create(
    model="gpt-4.1-nano",
    input="Hello!",
)

print(response.output_text)
```

## Sources

- **Agent Service overview**: https://learn.microsoft.com/en-us/azure/foundry/agents/overview
- **Migration guide (classic → new)**: https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/migrate
- **Hosted agents**: https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/hosted-agents
- **Publishing agents**: https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/publish-agent
- **Foundry IQ (preview)**: https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/what-is-foundry-iq
- **Azure SDK for Python (agents)**: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects
- **Agent samples**: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-agents/samples
- **Assistants API (deprecated)**: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/assistants?view=foundry

## See Also

- [SDK Overview (Foundry SDK, OpenAI SDK, Foundry Tools)](sdk-overview.md)
- [Chat Completions vs Responses (detailed guide)](chat-vs-responses.md)
- [Quick Reference](quick-reference.md)

