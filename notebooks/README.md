# Cobalt Advisory Co-Pilot — Notebook Series

A hands-on walkthrough of the four-layer Microsoft AI agents stack, grounded in one running scenario: an AI co-pilot for advisers at a fictional wealth-management firm, **Cobalt Advisory Co.** Each notebook adds one capability and revisits the same client persona (`Avery Chen`, age 47, moderate-aggressive, $1.42M AUM).

> **All auth is Microsoft Entra ID via `DefaultAzureCredential`.** No API keys anywhere. Run `az login` once before any notebook.

## How the notebooks map to the README diagrams

| # | Notebook | Stack layer demonstrated | Story beat |
|---|---|---|---|
| 0 | [`00_setup_and_auth.ipynb`](00_setup_and_auth.ipynb) | Shared scaffolding | Verify env, credentials, and meet `Avery Chen`. |
| 1 | `01_chat_completions.ipynb` *(planned)* | Layer 1 — Chat Completions | Adviser asks one-off market questions. |
| 2 | `02_responses_api.ipynb` *(planned)* | Layer 1 — Responses API | Multi-turn portfolio Q&A + web search tool + PDF prospectus input. |
| 3 | `03_foundry_agent_service.ipynb` *(planned)* | Layer 2 — Foundry Agent Service | Hosted **Portfolio Review Agent** with `file_search` over the firm's research library. |
| 4 | `04_maf_single_agent.ipynb` *(planned)* | Layer 3 — MAF | Same agent re-authored in code; swap providers in one line. |
| 5 | `05_maf_multi_agent_workflow.ipynb` *(planned)* | Layer 3 — MAF workflows | Market analyst → tax optimizer → compliance reviewer → client-brief writer. |
| 6 | `06_maf_deploy_as_hosted_agent.ipynb` *(planned)* | Layer 2 + 3 | Deploy the MAF workflow as a Foundry Hosted Agent (~2 LOC). |
| 7 | `07_agent_365_governance.ipynb` *(planned)* | **Layer 4 — Microsoft Agent 365** | Wrap the hosted agent with Entra Agent Identity + Work IQ MCP (Outlook / SharePoint / Teams) + Purview DLP + OTel traces + blueprint approval. **The cherry on top.** |

## Conventions

- **Shared module** — every notebook imports from [`_common`](./_common/):
  - `env.load_env()` → typed `Config` from `.env`
  - `clients.get_openai_client(cfg)` / `get_project_client(cfg)` / `get_project_openai_client(cfg)`
  - `scenario.CLIENT_PROFILE` / `HOLDINGS` / `portfolio_summary()`
  - `patches.apply_maf_gzip_workaround()` (MAF notebooks only)
- **Pinned versions** — install cells pin packages explicitly (especially MAF rc1, which has known incompatibilities with the agentserver adapter).
- **Synthetic data only** — `Avery Chen` is fictional; holdings and prices are illustrative.
- **`gpt-5.4` with `reasoning_effort="low"`** by default — see `.env`.

## Setup (once per machine)

```bash
# 1. Authenticate to Azure (interactive)
az login

# 2. Create the env file
cp .env.example .env       # then edit if your endpoints differ

# 3. Activate venv and install base dependencies (notebook #0 also does this)
source .venv/bin/activate
pip install --upgrade openai azure-ai-projects --pre azure-identity python-dotenv
```

Then open `00_setup_and_auth.ipynb` and run it top-to-bottom. If both smoke tests pass, you're ready for notebook #1.
