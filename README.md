---
title: Microsoft AI Agents Platform Guide (2026)
description: A developer's map of the Microsoft AI agents stack in 2026 — Azure OpenAI APIs (Chat Completions, Responses), Foundry Agent Service, Microsoft Agent Framework (MAF), and Microsoft Agent 365 governance.
author: Arturo-Quiroga-MSFT
ms.date: 2026-05-19
ms.topic: overview
keywords:
  - microsoft ai agents
  - azure ai foundry
  - azure openai
  - responses api
  - chat completions
  - foundry agent service
  - microsoft agent framework
  - microsoft agent 365
---

# Microsoft AI Agents Platform Guide (2026)

> **Covers:** `Chat Completions` · `Responses` · `Foundry Agent Service` · `Microsoft Agent Framework (MAF)` · `Microsoft Agent 365`
>
> **Last updated: 2026-05-19** — all docs synced against official Microsoft Learn sources.

A developer's map of the **Microsoft AI agents stack** as it stands in May 2026. The platform now spans four layers, and picking the right entry point depends on what you're building:

1. **Model APIs** — Chat Completions and Responses on `/openai/v1` for direct model calls.
2. **Hosted agent runtime** — Foundry Agent Service for server-managed conversations, tools, and identity.
3. **Code-first orchestration** — Microsoft Agent Framework (MAF) for multi-agent workflows in Python and .NET.
4. **Enterprise control plane** — Microsoft Agent 365 (GA May 1, 2026) for Observe / Govern / Secure across every agent in your tenant, regardless of framework.

This repo breaks each layer down, compares them side by side, and gives you the code patterns to get started. **Who it's for:** developers and architects deciding which API, SDK, or governance surface to adopt for a new or existing agent workload on Microsoft Foundry.

## The landscape at a glance

```mermaid
graph LR
    subgraph A365["Microsoft Agent 365 — Enterprise Control Plane (Observe • Govern • Secure)"]
        direction TB
        subgraph "Azure AI Foundry / Microsoft Foundry"
            direction TB
            MAF["Microsoft Agent Framework (MAF)<br/><i>code-first orchestration</i>"]
            CC["Chat Completions API<br/><code>/openai/v1/chat/completions</code>"]
            RA["Responses API<br/><code>/openai/v1/responses</code>"]
            AS["Foundry Agent Service<br/><code>/agents  /conversations</code>"]
        end
    end

    DEV((You)) --> MAF
    DEV --> CC
    DEV --> RA
    DEV --> AS

    MAF -. "calls" .-> CC
    MAF -. "calls" .-> RA
    MAF -. "hosted as" .-> AS

    CC -- "Stateless, simple" --> MODEL["OpenAI Models"]
    RA -- "Stateful, modern features" --> MODEL
    AS -- "Orchestrated agents" --> MODEL

    style DEV fill:#0078D4,color:#fff,stroke:#005A9E
    style A365 fill:#EEF2FF,stroke:#4F46E5,stroke-width:2px,color:#1E1B4B
    style MAF fill:#D4EDDA,stroke:#28A745
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

> [!NOTE]
> **Where does Microsoft Agent Framework (MAF) fit?** [MAF](https://learn.microsoft.com/en-us/agent-framework/overview/?pivots=programming-language-python) ([repo](https://github.com/microsoft/agent-framework)) is the **code-first orchestration SDK** (Python + .NET) that sits *above* these APIs. You write agents and graph-based multi-agent workflows in MAF; MAF calls Chat Completions / Responses under the hood and can deploy your agent as a **Foundry Hosted Agent** with ~2 extra lines of code. It is the direct successor to Semantic Kernel and AutoGen. See the [SDK Overview](docs/sdk-overview.md#microsoft-agent-framework-maf) for details.

> [!IMPORTANT]
> **Where does Microsoft Agent 365 fit?** [Microsoft Agent 365](https://learn.microsoft.com/en-us/microsoft-agent-365/overview) (**GA May 1, 2026**) is the enterprise **control plane** that wraps every agent in your tenant — regardless of which framework or cloud built it. Its three pillars are **Observe** (centralized agent registry, Agent Map, real-time telemetry), **Govern** (lifecycle, access control, and compliance via Entra + Purview + the M365 admin center), and **Secure** (Entra-backed Agent Identity, Purview DLP, Defender threat protection). Use the [Agent 365 SDK](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/) and CLI to layer governed Work IQ tool access, notifications, Entra Agent Identity, and OpenTelemetry observability on agents built with MAF, Foundry Agent Service, Copilot Studio, OpenAI Agents SDK, LangChain — or even Google Vertex / AWS Bedrock. Agent 365 **does not host or build agents**; it makes them enterprise-ready.

## Which API should you use?

```mermaid
flowchart TD
    START(["New project"]) --> Q0{"Writing multi-agent<br/>orchestration in code?"}
    Q0 -- Yes --> MAF["Use Microsoft Agent Framework (MAF)"]
    Q0 -- No --> Q1{"Need stateful agents<br/>with tool orchestration?"}
    Q1 -- Yes --> AGENT["Use Foundry Agent Service"]
    Q1 -- No --> Q2{"Building a new app<br/>that needs latest features?"}
    Q2 -- Yes --> RESP["Use Responses API"]
    Q2 -- No --> CHAT["Use Chat Completions API"]

    MAF --> SDK_M["SDK: <code>agent-framework</code><br/>(optionally deploy as Foundry Hosted Agent)"]
    AGENT --> SDK_A["SDK: <code>azure-ai-projects</code> v2"]
    RESP --> SDK_R["SDK: <code>openai</code>"]
    CHAT --> SDK_C["SDK: <code>openai</code>"]

    style START fill:#0078D4,color:#fff,stroke:#005A9E
    style Q0 fill:#FFF3CD,stroke:#856404
    style Q1 fill:#FFF3CD,stroke:#856404
    style Q2 fill:#FFF3CD,stroke:#856404
    style MAF fill:#D4EDDA,stroke:#28A745
    style AGENT fill:#D4EDDA,stroke:#28A745
    style RESP fill:#E6F2FF,stroke:#0078D4
    style CHAT fill:#E6F2FF,stroke:#0078D4
    style SDK_M fill:#f8f8f8,stroke:#666
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
        MAF["agent-framework<br/><i>MAF — multi-agent orchestration</i>"]
    end

    subgraph "Azure AI Foundry"
        PROJ["Project Endpoint"]
        OAIEP["OpenAI v1 Endpoint"]
        TOOLS["Foundry Tools<br/>(Vision, Speech, Safety, etc.)"]
        HOST["Foundry Hosted Agents<br/>(container runtime)"]
    end

    APP --> AIP
    APP --> OAI
    APP --> MAF

    AIP --> PROJ
    OAI --> OAIEP
    MAF --> PROJ
    MAF -. "deploy as" .-> HOST
    AIP -.-> TOOLS

    style APP fill:#0078D4,color:#fff,stroke:#005A9E
    style AIP fill:#E6F2FF,stroke:#0078D4
    style OAI fill:#E6F2FF,stroke:#0078D4
    style MAF fill:#D4EDDA,stroke:#28A745
    style PROJ fill:#FFF3CD,stroke:#856404
    style OAIEP fill:#FFF3CD,stroke:#856404
    style HOST fill:#D4EDDA,stroke:#28A745
    style TOOLS fill:#f8f8f8,stroke:#666
```

> [!TIP]
> All Microsoft Foundry SDK development is consolidating into `azure-ai-projects` v2. The separate `azure-ai-agents` package has been dropped. See the [SDK Overview](docs/sdk-overview.md) for installation details.

## Key dates and migration

> [!IMPORTANT]
> - **March 31, 2026** — Classic Foundry Agent Service (threads/runs/messages pattern) was retired. New code must use the conversations/responses pattern. See the [migration section](docs/agents-and-apis.md#migration-from-classic-to-new) in the agent guide.
> - **May 1, 2026** — **Microsoft Agent 365 reached General Availability** for the Commercial segment (per-user licensing). Recommended companion products: Entra P1/P2 or Entra Suite, plus Purview DLP, to take full advantage of governance and protection. See the [Agent 365 overview](https://learn.microsoft.com/en-us/microsoft-agent-365/overview).

## Primary sources

* [Supported languages (Python pivot)](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/supported-languages?view=foundry&tabs=dotnet-secure%2Csecure%2Cpython-entra&pivots=programming-language-python)
* [API version lifecycle](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/api-version-lifecycle?view=foundry)
* [Foundry Agent Service overview](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview)
* [Agent Service migration guide](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/migrate)
* [Responses API how-to](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/responses?view=foundry)
* [Microsoft Agent 365 overview](https://learn.microsoft.com/en-us/microsoft-agent-365/overview)
* [Microsoft Agent 365 SDK and CLI (developer landing)](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/)

## Contributing

Found something outdated or incorrect? Open an issue or submit a PR. These docs are maintained by checking them against Microsoft Learn sources and updating as APIs evolve.
