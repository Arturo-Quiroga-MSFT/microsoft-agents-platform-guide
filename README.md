---
title: Azure OpenAI API Guide (2026)
description: A practical guide to Azure OpenAI API surfaces, SDKs, and the Foundry Agent Service for developers building on Microsoft Foundry.
author: Arturo-Quiroga-MSFT
ms.date: 2026-03-22
ms.topic: overview
keywords:
  - azure openai
  - responses api
  - chat completions
  - foundry agent service
  - azure ai foundry
---

# Azure OpenAI API Guide (2026)

> **Last updated: 2026-03-22** — all docs synced against official Microsoft Learn sources.

Azure AI Foundry exposes multiple API surfaces for interacting with OpenAI models. Choosing the right one depends on your use case: a stateless chat, a feature-rich conversation, or a fully orchestrated agent. This repo breaks down the options, compares them side by side, and provides the code patterns you need to get started.

## The landscape at a glance

```mermaid
graph LR
    subgraph "Azure AI Foundry / Microsoft Foundry"
        direction TB
        CC["Chat Completions API<br/><code>/openai/v1/chat/completions</code>"]
        RA["Responses API<br/><code>/openai/v1/responses</code>"]
        AS["Foundry Agent Service<br/><code>/agents  /conversations</code>"]
    end

    DEV((You)) --> CC
    DEV --> RA
    DEV --> AS

    CC -- "Stateless, simple" --> MODEL["OpenAI Models"]
    RA -- "Stateful, modern features" --> MODEL
    AS -- "Orchestrated agents" --> MODEL

    style DEV fill:#0078D4,color:#fff,stroke:#005A9E
    style CC fill:#E6F2FF,stroke:#0078D4
    style RA fill:#E6F2FF,stroke:#0078D4
    style AS fill:#D4EDDA,stroke:#28A745
    style MODEL fill:#FFF3CD,stroke:#856404
```

Three API surfaces, one platform. Each serves a different complexity tier:

| API Surface              | State Management | Best For                                    |
|--------------------------|------------------|---------------------------------------------|
| **Chat Completions**     | Client-managed   | Simple stateless chat, existing codebases   |
| **Responses**            | Optional server  | New apps, latest features, multi-turn state |
| **Foundry Agent Service** | Server-managed  | Production agents with tool orchestration   |

## Which API should you use?

```mermaid
flowchart TD
    START(["New project"]) --> Q1{"Need stateful agents<br/>with tool orchestration?"}
    Q1 -- Yes --> AGENT["Use Foundry Agent Service"]
    Q1 -- No --> Q2{"Building a new app<br/>that needs latest features?"}
    Q2 -- Yes --> RESP["Use Responses API"]
    Q2 -- No --> CHAT["Use Chat Completions API"]

    AGENT --> SDK_A["SDK: <code>azure-ai-projects</code> v2"]
    RESP --> SDK_R["SDK: <code>openai</code>"]
    CHAT --> SDK_C["SDK: <code>openai</code>"]

    style START fill:#0078D4,color:#fff,stroke:#005A9E
    style Q1 fill:#FFF3CD,stroke:#856404
    style Q2 fill:#FFF3CD,stroke:#856404
    style AGENT fill:#D4EDDA,stroke:#28A745
    style RESP fill:#E6F2FF,stroke:#0078D4
    style CHAT fill:#E6F2FF,stroke:#0078D4
    style SDK_A fill:#f8f8f8,stroke:#666
    style SDK_R fill:#f8f8f8,stroke:#666
    style SDK_C fill:#f8f8f8,stroke:#666
```

## Docs in this repo

This repo contains four deep-dive guides, each covering a different angle of the Azure OpenAI API story. Read them in order for a narrative flow, or jump directly to what you need.

| #  | Guide                                                                      | What You Learn                                                                           |
|----|----------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| 1  | [Quick Reference](docs/quick-reference.md)                                | Endpoint matrix, feature status, code snippets for all three APIs. **Start here.**       |
| 2  | [Chat Completions vs Responses](docs/chat-vs-responses.md)                | Detailed comparison of request shape, state handling, feature velocity, and capabilities. |
| 3  | [SDK Overview](docs/sdk-overview.md)                                      | Foundry SDK, OpenAI SDK, Foundry Tools, and Microsoft Agent Framework side by side.      |
| 4  | [Foundry Agent Service: Which API?](docs/agents-and-apis.md)              | Agent types, tool availability, hosted agents, publishing, and migration guidance.        |

## SDK ecosystem

```mermaid
graph TB
    subgraph "Your Application"
        APP["Python / C# App"]
    end

    subgraph "SDKs"
        AIP["azure-ai-projects v2<br/><i>Foundry SDK</i>"]
        OAI["openai<br/><i>OpenAI SDK</i>"]
        MAF["Microsoft Agent Framework<br/><i>Multi-agent orchestration</i>"]
    end

    subgraph "Azure AI Foundry"
        PROJ["Project Endpoint"]
        OAIEP["OpenAI v1 Endpoint"]
        TOOLS["Foundry Tools<br/>(Vision, Speech, Safety, etc.)"]
    end

    APP --> AIP
    APP --> OAI
    APP --> MAF

    AIP --> PROJ
    OAI --> OAIEP
    MAF --> PROJ
    AIP -.-> TOOLS

    style APP fill:#0078D4,color:#fff,stroke:#005A9E
    style AIP fill:#E6F2FF,stroke:#0078D4
    style OAI fill:#E6F2FF,stroke:#0078D4
    style MAF fill:#D4EDDA,stroke:#28A745
    style PROJ fill:#FFF3CD,stroke:#856404
    style OAIEP fill:#FFF3CD,stroke:#856404
    style TOOLS fill:#f8f8f8,stroke:#666
```

> [!TIP]
> All Microsoft Foundry SDK development is consolidating into `azure-ai-projects` v2. The separate `azure-ai-agents` package has been dropped. See the [SDK Overview](docs/sdk-overview.md) for installation details.

## Key dates and migration

> [!IMPORTANT]
> The classic Foundry Agent Service platform (threads/runs/messages pattern) retires **March 31, 2026**. Migrate to the new conversations/responses pattern before that date. See the [migration section](docs/agents-and-apis.md#migration-from-classic-to-new) in the agent guide.

## Primary sources

* [Supported languages (Python pivot)](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/supported-languages?view=foundry&tabs=dotnet-secure%2Csecure%2Cpython-entra&pivots=programming-language-python)
* [API version lifecycle](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/api-version-lifecycle?view=foundry)
* [Foundry Agent Service overview](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview)
* [Agent Service migration guide](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/migrate)
* [Responses API how-to](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/responses?view=foundry)

## Contributing

Found something outdated or incorrect? Open an issue or submit a PR. These docs are maintained by checking them against Microsoft Learn sources and updating as APIs evolve.
