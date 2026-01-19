# Microsoft Foundry Agent Service: Which API to Use?

This guide clarifies which Azure OpenAI API surfaces (Chat Completions, Responses, or Assistants) you should use when working with **Microsoft Foundry Agent Service**.

## TL;DR

**Microsoft Foundry Agent Service uses its own Agent API** (threads, runs, messages pattern) — **not** Chat Completions or Responses directly. 

- **Agent Service SDK**: `azure-ai-agents` (Python) — has its own `agents.create_agent()`, `threads.create()`, `messages.create()`, `runs.create()` operations.
- **Not for direct use with agents**: Chat Completions API or Responses API are not called directly when using Agent Service.

## What is Microsoft Foundry Agent Service?

Foundry Agent Service is a **production-ready platform** for building and deploying intelligent agents with:

- **Stateful threads** (conversation history managed server-side)
- **Tool orchestration** (automatic tool call execution and retry)
- **Enterprise trust & safety** (content filters, RBAC, network isolation)
- **Multi-agent coordination** (agent-to-agent messaging)
- **Full observability** (traces, logs, Application Insights integration)

It's positioned as Microsoft's recommended approach for building agents, replacing the older Azure OpenAI Assistants API (preview).

## Agent Service API Pattern (Threads, Runs, Messages)

The Agent Service uses a **threads/runs/messages** pattern similar to OpenAI's Assistants API:

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:
    agents_client = project_client.agents

    # 1. Create an agent
    agent = agents_client.create_agent(
        model="gpt-4o",  # your deployment name
        name="my-agent",
        instructions="You are a helpful assistant",
    )

    # 2. Create a thread (conversation)
    thread = agents_client.threads.create()

    # 3. Add a message to the thread
    message = agents_client.messages.create(
        thread_id=thread.id,
        role="user",
        content="Hello, tell me a joke",
    )

    # 4. Run the agent on the thread
    run = agents_client.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id,
    )

    # 5. Retrieve messages (agent responses are appended to thread)
    messages = agents_client.messages.list(thread_id=thread.id)
    for msg in messages:
        if msg.text_messages:
            print(f"{msg.role}: {msg.text_messages[-1].text.value}")
```

## Comparison: Agent Service vs Chat Completions vs Responses

| Aspect | Agent Service | Chat Completions | Responses API |
|---|---|---|---|
| **Use case** | Production agents with orchestration, state, tools, and governance | Simple stateless chat | Unified chat + assistants-style features |
| **State management** | Server-side (threads stored in Cosmos DB) | Client-side (you manage history) | Mixed (can use conversation objects) |
| **Tool orchestration** | Automatic server-side execution + retry | Manual (you handle tool calls) | Server-side (similar to Agent Service) |
| **API pattern** | `agents`, `threads`, `runs`, `messages` | `chat.completions.create(messages=[...])` | `responses.create(input=...)` |
| **When to use** | Building production agents with enterprise requirements | Lightweight chat, simple Q&A | Modern chat apps, prototypes needing latest features |
| **SDK** | `azure-ai-agents` (via `AIProjectClient`) | OpenAI SDK (`openai` package) | OpenAI SDK (`openai` package) |
| **Endpoint style** | `/agents/...`, `/threads/...`, `/runs/...` | `/openai/v1/chat/completions` | `/openai/v1/responses` |

## Why Agent Service is NOT Chat Completions or Responses

### 1. Different API surfaces

- **Agent Service**: uses a dedicated Agent API with operations like `create_agent`, `threads.create`, `runs.create_and_process`.
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
- **Bring-your-own storage** (Cosmos DB, AI Search, VNets)
- **Application Insights** and **trace logging** out of the box

These are not part of Chat Completions or Responses APIs.

## Migration Note: Assistants API → Agent Service

Microsoft's **Azure OpenAI Assistants API** (preview) is being superseded by **Foundry Agent Service** (GA).

### Key changes from Assistants to Agent Service:

| Assistants API (old) | Agent Service (new) |
|---|---|
| `assistants` | `agents` |
| `threads` | `conversations` (in some new APIs) or `threads` (for compatibility) |
| `runs` | `responses` (in newer patterns) or `runs` (for compatibility) |
| Messages only | Items (messages, tool calls, outputs, etc.) |

The Agent Service maintains **backward compatibility** with the threads/runs/messages pattern while adding new capabilities.

## When to Use What?

### Use **Foundry Agent Service** when:
- Building production agents with state, tools, and governance
- Need multi-agent orchestration
- Require enterprise trust & safety (content filters, RBAC, network isolation)
- Want server-side tool orchestration and automatic retries
- Need full conversation visibility and tracing

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

### Agent Service (stateful, orchestrated)

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient(
    endpoint="https://YOUR-PROJECT.api.azureml.ms",
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
    
    # Server automatically appends agent response to thread
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

- **Agent Service overview**: https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview?view=foundry
- **Threads, runs, messages concept**: https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/threads-runs-messages?view=foundry
- **Azure SDK for Python (agents)**: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects
- **Agent samples**: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-agents/samples
- **Assistants API (being replaced)**: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/assistants?view=foundry
