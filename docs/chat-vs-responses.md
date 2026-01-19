# Chat Completions vs Responses (Azure OpenAI v1)

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
| I need tool-style integrations (example: MCP tools) in the OpenAI v1 style. | Responses | Supported languages doc includes Responses + MCP examples. |
| I need a single API surface that spans “chat-like prompts” plus newer capabilities. | Responses | Described as a unified experience (chat + assistants-style capabilities). |

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
- Newer features show up here first (as indicated by Microsoft docs).
- Supports tool integrations (example shown: MCP tools).

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

## Notes that matter in practice

- **Auth options**: both APIs support API keys and Microsoft Entra ID in the supported-languages doc.
- **Endpoint & versioning**: the v1 GA experience uses `/openai/v1` and does not require `api-version` in the request.
- **Parsing**: Microsoft explicitly recommends being resilient to additional response fields and parsing only what you need.

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
