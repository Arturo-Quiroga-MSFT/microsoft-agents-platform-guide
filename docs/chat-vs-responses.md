# Chat Completions vs Responses (Azure OpenAI v1)

> **Last updated: 2026-05-19** — synced with [Responses API how-to](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/responses?view=foundry) and [API version lifecycle](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/api-version-lifecycle?view=foundry) docs.

This page summarizes the practical differences between the **Chat Completions API** and the **Responses API** when using **Azure OpenAI v1** (`/openai/v1`) through Azure AI Foundry / Microsoft Foundry.

> Source of truth for examples and auth patterns: the Azure OpenAI “supported languages” article (Python pivot).

## Quick decision guide

### Recommended default

If you are starting a new application today, prefer **Responses** unless you have a concrete reason to stay on **Chat Completions**.

### Decision table

| Question | Pick | Why |
|---|---|---|
| I need a simple chat interface and already have code using `messages[]` + `choices[]`. | Chat Completions | Lowest migration cost; simple mental model. |
| I want the “forward path” API that gets new features first. | Responses | Microsoft docs position Responses as the API to use for latest features. |
| I need tool-style integrations (remote MCP tools). | Responses | Remote MCP server integration is GA on Responses. |
| I need image generation or async background tasks. | Responses | Both are GA on the Responses API. |
| I want multi-turn state without managing history myself. | Responses | Use `previous_response_id` to chain calls; server stores context for 30 days. |
| I need a single API surface that spans “chat-like prompts” plus newer capabilities. | Responses | Described as a unified experience (chat + assistants-style capabilities). || I need the newest features (developer messages, history compaction, WebSocket realtime). | Responses | New capabilities land exclusively on Responses. |
## Conceptual differences

### 1) Request shape

- **Chat Completions**: send `messages` (role/content transcript) and receive `choices`.
- **Responses**: send `input` (and optional `instructions`, tools, reasoning options, etc.) and receive an `output` array (with helpers like `output_text`).

### 2) Feature velocity

- **Responses** is presented as the API that supports the newest capabilities.
- **Chat Completions** remains supported, but is framed as the older surface.

### 3) Stateful vs transcript-based

- **Chat Completions** is fundamentally transcript-based: you provide the conversation history every call.
- **Responses** is described as a newer, more stateful-style API in Azure OpenAI documentation (while still allowing simple one-shot calls).

## Pros / cons

### Chat Completions

**Pros**
- Straightforward for multi-turn chat: `messages` in, `choices[0].message.content` out.
- Very common in existing codebases and older samples.

**Cons**
- Older API surface; fewer “latest” features compared to Responses.
- Less aligned with where Microsoft’s newer examples are heading.

### Responses

**Pros**
- Unified API that combines chat-style prompting with newer capabilities.
- **Generally Available (GA)** — `/openai/v1/responses` is in the GA status table.
- Newer features land here first: remote MCP tools, async background tasks, image generation, encrypted reasoning.
- Server-side response storage: retrieve or delete past responses; chain calls with `previous_response_id` (30-day default retention).
- Supports **multi-provider models** (Azure OpenAI, DeepSeek/MAI-DS-R1, Grok, Microsoft AI) deployed in Foundry.

**Cons**
- Response object is richer and can be more complex to parse if you want full fidelity.
- Migration requires mapping `messages`/`choices` patterns to `input`/`output` patterns.

## Side-by-side: Python (OpenAI SDK)

All examples assume Azure OpenAI v1 base URL:

- `OPENAI_BASE_URL=https://YOUR-RESOURCE-NAME.openai.azure.com/openai/v1/`

And either:

- Entra ID token provider, or
- `OPENAI_API_KEY` / `AZURE_OPENAI_API_KEY`

### Responses API (recommended)

```python
from openai import OpenAI

client = OpenAI()  # uses OPENAI_BASE_URL + OPENAI_API_KEY

resp = client.responses.create(
    model="gpt-4.1-nano",  # your deployment name
    input="This is a test.",
)

print(resp.output_text)
```

### Chat Completions API (classic)

```python
from openai import OpenAI

client = OpenAI()  # uses OPENAI_BASE_URL + OPENAI_API_KEY

chat = client.chat.completions.create(
    model="gpt-4o",  # your deployment name
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "When was Microsoft founded?"},
    ],
)

print(chat.choices[0].message.content)
```

## New Responses API capabilities (May 2026)

### Response chaining (`previous_response_id`)

```python
response = client.responses.create(
    model="gpt-4o",
    input="Define catastrophic forgetting."
)

# Continue conversation without re-sending history
second_response = client.responses.create(
    model="gpt-4o",
    previous_response_id=response.id,
    input=[{"role": "user", "content": "Explain that to a college freshman."}]
)
print(second_response.output_text)
```

### Retrieve and delete stored responses

```python
# Responses are stored server-side for 30 days by default
stored = client.responses.retrieve("resp_67cb32528d6881909eb2859a55e18a85")

# Explicitly delete a response
client.responses.delete("resp_67cb32528d6881909eb2859a55e18a85")
```

### History compaction (client-side or server-side)

Shrink the context window while preserving essential reasoning, messages, and tool calls.

```python
# Explicit compaction of a prior response
compacted = client.responses.compact(
    model="gpt-4.1",
    previous_response_id=prior.id,
)

# Or enable automatic server-side compaction during a long task
response = client.responses.create(
    model="gpt-5.3-codex",
    input=conversation,
    store=False,
    context_management=[{"type": "compaction", "compact_threshold": 200000}],
)
```

When the output crosses `compact_threshold`, the service emits an opaque compaction item that carries forward state in subsequent turns.

### Code Interpreter tool

Run sandboxed Python inside a Response, including file generation and image transformations (useful for visual reasoning with `o3` / `o4-mini`).

```python
response = client.responses.create(
    model="gpt-4.1",
    tools=[{"type": "code_interpreter", "container": {"type": "auto"}}],
    instructions="You are a personal math tutor. Use the python tool to answer.",
    input="I need to solve 3x + 11 = 14. Can you help me?",
)
```

Containers cost extra; idle timeout is 20 minutes, max session 1 hour.

### File input (PDFs)

PDFs can be supplied as Base64 (`input_file` with `file_data`) or via `file_id` after uploading with `purpose="assistants"` (the temporary workaround — `user_data` purpose is not yet supported on input PDFs).

### Remote MCP servers + approvals

The `mcp` tool type accepts custom auth headers and emits an `mcp_approval_request` item before sharing data. Respond with an `mcp_approval_response` (using `previous_response_id`) to authorize the call. Requires TLS 1.2+; mTLS and Azure service tags are not supported.

### Background tasks (durable, cancellable, resumable)

```python
response = client.responses.create(
    model="o3",
    input="Write me a very long story",
    background=True,   # requires store=True
    stream=True,       # optional; needed to resume a dropped stream
)
```

Poll with `client.responses.retrieve(id)`, cancel with `client.responses.cancel(id)`, and resume streaming via `?stream=true&starting_after=<sequence_number>`.

### Image generation (preview)

Responses API now exposes a built-in `image_generation` tool backed by the `gpt-image-1` family. Send the `x-ms-oai-image-generation-deployment` header and use any vision-capable orchestrator model (gpt-4o, gpt-4.1, o3, gpt-5/5.1).

### Developer messages

Developer-role messages can be sent inline with user input for more granular prompting control.
## Notes that matter in practice

- **Auth options**: both APIs support API keys and Microsoft Entra ID. Newer official samples use the `https://ai.azure.com/.default` scope for Entra ID (the legacy `https://cognitiveservices.azure.com/.default` scope still works).
- **Endpoint & versioning**: the v1 GA experience uses `/openai/v1` and does not require `api-version` in the request.
- **Parsing**: Microsoft explicitly recommends being resilient to additional response fields and parsing only what you need.
- **Multi-provider models**: both Chat Completions and Responses APIs work with non-Azure-OpenAI models deployed in Foundry (DeepSeek R1 as `MAI-DS-R1`, Grok, and other Microsoft AI models).

## Sources

- Supported languages (Python pivot):
  https://learn.microsoft.com/en-us/azure/ai-foundry/openai/supported-languages?view=foundry&tabs=dotnet-secure%2Csecure%2Cpython-entra&pivots=programming-language-python
- Responses API overview:
  https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/responses?view=foundry
- Chat completions overview:
  https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/chatgpt?view=foundry

## See Also

- [SDK Overview (Foundry SDK, OpenAI SDK, Foundry Tools)](sdk-overview.md)
- [Foundry Agent Service: Which API to Use?](agents-and-apis.md)
- [Quick Reference](quick-reference.md)
