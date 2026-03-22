# Azure AI Foundry SDK Landscape

> **Last updated: 2026-03-22** — synced with [supported languages](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/supported-languages?view=foundry&pivots=programming-language-python), [API version lifecycle](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/api-version-lifecycle?view=foundry), and [migration guide](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/migrate) docs.

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

## Agent Framework (Multi-Agent Orchestration)

**Microsoft Agent Framework** is an open-source SDK for building multi-agent systems in code (.NET, Python) with a **cloud-provider-agnostic** interface.

### When to Use

- ✅ Define and orchestrate agents **locally** (in your code)
- ✅ Multi-agent coordination with complex workflows
- ✅ Cloud-agnostic design (not tied to Azure)

**Pair with Foundry SDK** when you want:
- Agent Framework agents to run against Foundry models
- Agent Framework to orchestrate agents hosted in Foundry (deploy as hosted agents)

**Note**: Agent Framework is **different** from Foundry Agent Service (which is a hosted platform for server-side orchestration). However, Agent Framework agents can now be deployed as **hosted agents** in Foundry.

### Resources

- [Microsoft Agent Framework Overview](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview)
- [Official Python agent SDK samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects)

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
│  ✅ Multi-agent coordination                                │
│  🔗 Can integrate with Foundry SDK for hosted models        │
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
