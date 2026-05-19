# Azure AI Foundry SDK Landscape

> **Last updated: 2026-05-19** — synced with [supported languages](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/supported-languages?view=foundry&pivots=programming-language-python), [API version lifecycle](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/api-version-lifecycle?view=foundry), and [migration guide](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/migrate) docs.

This guide explains the **SDK ecosystem** for Azure AI Foundry and how each SDK relates to the APIs (Chat Completions, Responses, Agent Service) documented in this repo.

## Overview: SDKs and Endpoints

Creating a Foundry resource unlocks access to models, agents, and tools through a unified set of SDKs and endpoints:

| SDK | What it's for | Endpoint Pattern | Key Package |
|---|---|---|---|
| **Foundry SDK** | Foundry-specific capabilities with OpenAI-compatible interfaces. Access to Foundry direct models through Responses API (not Chat Completions). | `https://<resource-name>.services.ai.azure.com/api/projects/<project-name>` | `azure-ai-projects` |
| **OpenAI SDK** | Latest OpenAI models and features with full OpenAI API surface. Foundry direct models available through Chat Completions API (not Responses). | `https://<resource-name>.openai.azure.com/openai/v1` | `openai` |
| **Foundry Tools SDKs** | Prebuilt solutions (Vision, Speech, Content Safety, Document Intelligence, etc.). | Tool-specific endpoints (varies by service) | Service-specific packages |
| **Agent Framework** | Multi-agent orchestration in code. Cloud-agnostic. | Uses project endpoint via Foundry SDK | Microsoft Agent Framework SDK |

**Key Note**: A Foundry resource provides all endpoints. An Azure OpenAI resource provides only the `/openai/v1` endpoint.

**Dual base URL**: The `/openai/v1` endpoint can be reached via two equivalent base URLs:
- `https://YOUR-RESOURCE-NAME.openai.azure.com/openai/v1/`
- `https://YOUR-RESOURCE-NAME.services.ai.azure.com/openai/v1/`

## Foundry SDK (`azure-ai-projects`)

The **Azure AI Projects client library** is a unified SDK that connects to a single project endpoint, simplifying application configuration.

### Installation

```bash
# v2 SDK (for new Foundry projects, conversations/responses pattern)
# Bundles openai and azure-identity as direct dependencies
pip install --pre azure-ai-projects

# v1 SDK (for Foundry classic projects)
pip install azure-ai-projects azure-identity openai
```

> **SDK consolidation note**: All Microsoft Foundry SDK development is consolidating into the `azure-ai-projects` v2 package. Agents, inference, evaluations, and memory operations that previously lived in separate packages (`azure-ai-agents`, etc.) are unified under the v2 beta line. The `azure-ai-agents` dependency has been dropped; agents now use the OpenAI Responses protocol directly via `AIProjectClient`.

### Two Client Types

The Foundry SDK exposes two client types because Foundry and OpenAI have different API shapes:

#### 1. Project Client
**Use for**: Foundry-native operations where OpenAI has no equivalent.

**Examples**:
- Listing connections
- Retrieving project properties
- Enabling tracing
- Managing connections to Foundry Tools

```python
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

project = AIProjectClient(
    endpoint="https://<resource-name>.services.ai.azure.com/api/projects/<project-name>",
    credential=DefaultAzureCredential()
)

# Get project properties, enable tracing, etc.
```

#### 2. OpenAI-Compatible Client
**Use for**: Foundry functionality that builds on OpenAI concepts.

**Examples**:
- Responses API
- Agent Service
- Evaluations
- Fine-tuning

This client gives you access to **Foundry direct models** (non-Azure-OpenAI models hosted in Foundry). The project endpoint serves this traffic on the `/openai` route.

```python
# Get OpenAI-compatible client scoped to your project
openai_client = project.get_openai_client()

# Use Responses API (works with Azure OpenAI models AND Foundry direct models)
response = openai_client.responses.create(
    model="gpt-4.1-nano",  # your deployment name
    input="What is the speed of light?",
)
print(response.output_text)
```

> In the v2 SDK, `get_openai_client()` returns an `openai.OpenAI` client pre-configured for your Foundry project endpoint. The older `inference.get_azure_openai_client(api_version=...)` method is from v1 classic.

### What You Can Do with Foundry SDK

- ✅ Access Foundry Models (including Azure OpenAI and Foundry direct models)
- ✅ Use the Foundry Agent Service (conversations and responses pattern in v2)
- ✅ Run cloud evaluations
- ✅ Enable app tracing (Application Insights integration with OpenTelemetry `gen_ai.*` conventions)
- ✅ Fine-tune models
- ✅ Get endpoints and keys for Foundry Tools
- ✅ Manage memory stores (v2)

## OpenAI SDK (`openai`)

Use the **OpenAI SDK** when you want the full OpenAI API surface and maximum client compatibility.

### When to Use

- ✅ You want the complete OpenAI API surface
- ✅ Maximum compatibility with OpenAI-native code
- ✅ Working with Azure OpenAI models or Foundry direct models via **Chat Completions API**
- ❌ You don't need Foundry-specific features (agents, evaluations, etc.)

### Two Ways to Use It

#### Option 1: Via AIProjectClient (Recommended for Foundry Projects)

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project = AIProjectClient(
    endpoint="https://<resource-name>.services.ai.azure.com/api/projects/<project-name>",
    credential=DefaultAzureCredential()
)

# Get OpenAI client scoped to your project
openai_client = project.get_openai_client()

response = openai_client.responses.create(
    model="gpt-4.1-nano",  # your deployment name
    input="What is the size of France in square miles?",
)
print(response.output_text)
```

#### Option 2: Direct Azure OpenAI Endpoint

```python
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), 
    "https://ai.azure.com/.default"
)

client = OpenAI(  
    base_url="https://<resource-name>.openai.azure.com/openai/v1/",  
    api_key=token_provider,
)

response = client.responses.create(
    model="model_deployment_name",
    input="What is the size of France in square miles?" 
)
print(response.model_dump_json(indent=2))
```

> **Foundry direct models**: The Responses API (and Chat Completions API) also works with non-Azure-OpenAI models hosted in Foundry — such as **DeepSeek R1** (deployed as `MAI-DS-R1`), **Grok**, and other Microsoft AI models.

### OpenAI SDK Capabilities

| API | Available via OpenAI SDK | Available via Foundry SDK |
|---|---|---|
| **Chat Completions** | ✅ Yes | ✅ Yes (via `get_openai_client()`) |
| **Responses** | ✅ Yes | ✅ Yes (via `get_openai_client()`) |
| **Embeddings** | ✅ Yes | ✅ Yes |
| **Fine-tuning** | ✅ Yes | ✅ Yes |
| **Agent Service** | ❌ No | ✅ Yes (conversations/responses in v2; classic `project.agents` in v1) |
| **Evaluations** | ❌ No | ✅ Yes |
| **Tracing** | ❌ No | ✅ Yes |

## Microsoft Agent Framework (MAF)

**[Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/?pivots=programming-language-python)** ([microsoft/agent-framework](https://github.com/microsoft/agent-framework)) is the open-source, production-grade SDK for building and orchestrating AI agents and multi-agent workflows in **Python** and **.NET**. It is the direct successor to **Semantic Kernel** and **AutoGen** — built by the same teams — unifying AutoGen's simple agent abstractions with Semantic Kernel's enterprise features (sessions, middleware, telemetry, type safety) and adding **graph-based workflows** for explicit multi-agent control.

### Where MAF fits relative to Azure OpenAI APIs and Foundry Agent Service

| Layer | Concern | What you use |
|---|---|---|
| Model API | Raw inference (text, tools, structured output) | OpenAI SDK → Chat Completions / Responses |
| Hosted runtime | Server-managed conversations, tool execution, identity | Foundry SDK → Foundry Agent Service |
| **Orchestration framework** | **Define agents in code, compose multi-agent workflows, run locally or hosted** | **Microsoft Agent Framework** |

MAF is **not** a replacement for the Responses API or Foundry Agent Service — it sits **above** them. An MAF agent is a thin abstraction that delegates inference to a `ChatClient` (Azure OpenAI, Foundry, OpenAI, Anthropic, Ollama, …) and adds session state, tools, middleware, observability, and workflow orchestration.

### Installation

```bash
pip install agent-framework        # meta-package, all sub-packages
# or just the pieces you need:
pip install agent-framework-core   # core + Azure OpenAI + OpenAI clients
pip install agent-framework-azure-ai           # Azure AI Foundry integration
pip install agent-framework-orchestrations    # Sequential, Concurrent, Handoff, GroupChat, Magentic
```

.NET equivalents are published as `Microsoft.Agents.AI`, `Microsoft.Agents.AI.Foundry`, `Microsoft.Agents.AI.Workflows`, etc.

### Quickstart — Foundry-backed agent (Python)

```python
import asyncio
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential

async def main():
    agent = Agent(
        client=FoundryChatClient(
            credential=AzureCliCredential(),
            project_endpoint="https://<resource>.services.ai.azure.com/api/projects/<project>",
            model="gpt-5.1-mini",
        ),
        name="HaikuAgent",
        instructions="You are an upbeat assistant that writes beautifully.",
    )
    print(await agent.run("Write a haiku about Microsoft Agent Framework."))

asyncio.run(main())
```

Provider clients also exist for Azure OpenAI Chat Completions / Responses, OpenAI, Anthropic, Ollama, and others — swap the `client=` and the rest of your code is unchanged.

### Key capabilities

- **Agents** — LLM + tools + MCP servers + session state, with a consistent API across providers.
- **Workflows** — graph-based orchestration with **sequential**, **concurrent**, **handoff**, and **group-chat / Magentic** patterns; supports checkpointing, streaming, human-in-the-loop, and time-travel.
- **Foundry Hosted Agents** — deploy any MAF agent as a Foundry Hosted Agent with ~2 extra lines of code. See `python/samples/04-hosting/foundry-hosted-agents` in the upstream repo.
- **Middleware** — intercept agent runs for logging, guardrails, retry, caching, RAG injection, etc.
- **Declarative agents** — define agents in YAML for faster setup and versioning.
- **Observability** — OpenTelemetry built in (`gen_ai.*` conventions) for distributed tracing through Application Insights, Aspire, or any OTLP backend.
- **DevUI** — interactive local UI for developing, testing, and debugging agents and workflows.
- **Migration paths** — dedicated guides for moving from [Semantic Kernel](https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-semantic-kernel) and [AutoGen](https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen).

### MAF vs Foundry Agent Service — when to use which

| Choose | When |
|---|---|
| **Foundry Agent Service alone** (Prompt or Workflow agent) | You want a server-managed agent, prefer no-code / low-code authoring, are happy with the built-in tools (file search, code interpreter, MCP, Bing, etc.), and don't need custom orchestration logic. |
| **MAF, running locally / self-hosted** | You need fine-grained orchestration (multi-agent workflows, custom middleware, durable checkpointing) and want to deploy to your own infra (Azure Functions, Container Apps, AKS, on-prem). |
| **MAF → Foundry Hosted Agent** | You author the agent / workflow in MAF and want Foundry to host it: managed conversations, dedicated agent identity, BYO VNet, and a Responses-compatible endpoint. This is the recommended path for production code-first agents. |
| **MAF + multiple providers** | You want provider portability (Azure OpenAI today, OpenAI / Anthropic / Ollama tomorrow) without rewriting orchestration. |

### Resources

- Overview (Python pivot): https://learn.microsoft.com/en-us/agent-framework/overview/?pivots=programming-language-python
- GitHub: https://github.com/microsoft/agent-framework
- Python samples: https://github.com/microsoft/agent-framework/tree/main/python/samples
- Foundry Hosted Agents samples: https://github.com/microsoft/agent-framework/tree/main/python/samples/04-hosting/foundry-hosted-agents
- Migration from Semantic Kernel: https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-semantic-kernel
- Migration from AutoGen: https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen

## Foundry Tools SDKs

Foundry Tools (formerly Azure AI Services) are **prebuilt point solutions** with dedicated SDKs:

- **Speech**: Speech-to-text, text-to-speech, translation
- **Language**: NER, sentiment analysis, key phrase extraction
- **Translator**: Text and document translation
- **Vision**: Image analysis, OCR, face detection
- **Document Intelligence**: Form and document processing
- **Content Safety**: Content moderation
- **Azure AI Search**: Vector search, RAG

### Endpoint Patterns

Most tools use the Azure AI Services endpoint:

```
https://<your-resource-name>.cognitiveservices.azure.com/
```

Speech and Translation have specialized endpoints:

| Service | Endpoint |
|---|---|
| Speech-to-Text | `https://<region>.stt.speech.microsoft.com` |
| Text-to-Speech | `https://<region>.tts.speech.microsoft.com` |
| Text Translation | `https://api.cognitive.microsofttranslator.com/` |

### Python Packages (Examples)

```bash
# Speech
pip install azure-cognitiveservices-speech

# Language
pip install azure-ai-textanalytics

# Translator
pip install azure-ai-translation-text

# Vision
pip install azure-ai-vision-imageanalysis

# Document Intelligence
pip install azure-ai-documentintelligence

# Content Safety
pip install azure-ai-contentsafety

# Azure AI Search
pip install azure-search-documents
```

For full SDK reference, see:
- [C# Foundry Tools](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/sdk-overview?view=foundry&pivots=programming-language-csharp#c-supported-foundry-tools)
- [Java Foundry Tools](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/sdk-overview?view=foundry&pivots=programming-language-java#java-supported-foundry-tools)
- [JavaScript Foundry Tools](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/sdk-overview?view=foundry&pivots=programming-language-javascript#javascript-supported-foundry-tools)
- [Python Foundry Tools](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/sdk-overview?view=foundry&pivots=programming-language-python#python-supported-foundry-tools)

## SDK Decision Matrix

| Scenario | SDK to Use | Key Package |
|---|---|---|
| **Build agents with Foundry Agent Service** | Foundry SDK | `azure-ai-projects` → `project.agents` |
| **Call Azure OpenAI Chat Completions** | OpenAI SDK or Foundry SDK | `openai` (direct) or `azure-ai-projects` → `get_openai_client()` |
| **Call Azure OpenAI Responses API** | OpenAI SDK or Foundry SDK | `openai` (direct) or `azure-ai-projects` → `get_openai_client()` |
| **Enable tracing and observability** | Foundry SDK | `azure-ai-projects` |
| **Run cloud evaluations** | Foundry SDK | `azure-ai-projects` |
| **Use Speech, Vision, Language, etc.** | Foundry Tools SDKs | Service-specific packages |
| **Multi-agent orchestration in code** | Agent Framework | Microsoft Agent Framework SDK |
| **Fine-tune models** | OpenAI SDK or Foundry SDK | `openai` or `azure-ai-projects` |
| **Maximum OpenAI compatibility** | OpenAI SDK | `openai` |

## Authentication Patterns

All SDKs support **two authentication methods**:

### 1. API Key (Simple)

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://<resource-name>.openai.azure.com/openai/v1/",
    api_key="YOUR_API_KEY"
)
```

### 2. Microsoft Entra ID (Recommended for Production)

```python
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://ai.azure.com/.default"
)

client = OpenAI(
    base_url="https://<resource-name>.openai.azure.com/openai/v1/",
    api_key=token_provider
)
```

> **Scope note**: Newer official samples use `https://ai.azure.com/.default`. The legacy scope `https://cognitiveservices.azure.com/.default` still works.

## Relationship to API Surfaces

This table shows how SDKs map to the three main API surfaces covered in this repo:

| API Surface | Accessible via OpenAI SDK | Accessible via Foundry SDK | SDK Method |
|---|---|---|---|
| **Chat Completions** | ✅ Yes | ✅ Yes | `client.chat.completions.create()` |
| **Responses API** | ✅ Yes | ✅ Yes | `client.responses.create()` |
| **Agent Service** | ❌ No | ✅ Yes | `project.get_openai_client()` → `conversations.create()`, `responses.create()` (v2); `project.agents.create_agent()`, `threads.create()` (v1 classic) |

**Key Insight**:
- **OpenAI SDK** → Chat Completions + Responses API (stateless/inference)
- **Foundry SDK v2** → All three (Chat + Responses + Agent Service + Foundry-native features)
- **Foundry SDK v1 classic** → All three via the older `project.agents` pattern

## Summary: When to Use Each SDK

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure AI Foundry SDK                     │
│                   (azure-ai-projects v2)                    │
│                                                             │
│  ✅ Agent Service (conversations, responses pattern)         │
│  ✅ Evaluations, tracing, fine-tuning, memory stores         │
│  ✅ Foundry direct models (via Responses API)               │
│  ✅ Project-level operations                                │
│                                                             │
│  📦 Includes: OpenAI-compatible client                      │
└─────────────────────────────────────────────────────────────┘
                           ▲
                           │
                    (or use directly)
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                       OpenAI SDK                            │
│                        (openai)                             │
│                                                             │
│  ✅ Chat Completions API                                    │
│  ✅ Responses API                                           │
│  ✅ Embeddings, fine-tuning                                 │
│  ✅ Maximum OpenAI compatibility                            │
│                                                             │
│  ❌ No Agent Service                                        │
│  ❌ No Foundry-native features                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  Foundry Tools SDKs                         │
│     (Speech, Vision, Language, Content Safety, etc.)        │
│                                                             │
│  ✅ Prebuilt AI capabilities                                │
│  ✅ Service-specific endpoints                              │
│  📦 Separate packages per service                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Microsoft Agent Framework                      │
│         (Cloud-agnostic multi-agent orchestration)          │
│                                                             │
│  ✅ Define agents in code (.NET, Python)                    │
│  ✅ Multi-agent workflows (sequential, concurrent,           │
│     handoff, group-chat / Magentic, with checkpointing)     │
│  ✅ Provider-agnostic (Foundry, Azure OpenAI, OpenAI,        │
│     Anthropic, Ollama, ...)                                 │
│  ✅ Deploy as Foundry Hosted Agent in ~2 extra lines         │
│  ✅ Built-in OpenTelemetry, middleware, DevUI                │
│  📦 pip install agent-framework                              │
└─────────────────────────────────────────────────────────────┘
```

## Resources

- **Foundry SDK Overview**: https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/sdk-overview?view=foundry&pivots=programming-language-python
- **Azure AI Projects Python SDK**: https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme?view=azure-python-preview
- **OpenAI Python SDK**: https://github.com/openai/openai-python
- **Agent Framework**: https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview
- **Azure OpenAI Supported Languages**: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/supported-languages?view=foundry&tabs=dotnet-secure%2Csecure%2Cpython-entra&pivots=programming-language-python

## See Also

- [Chat Completions vs Responses API](chat-vs-responses.md)
- [Foundry Agent Service: Which API to Use?](agents-and-apis.md)
- [Quick Reference](quick-reference.md)
