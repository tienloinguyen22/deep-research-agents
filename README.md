# Deep Research Agents

An agentic research pipeline that orchestrates multiple specialized AI agents to search, scrape, synthesize, and critique information into polished research outputs.

This repository uses AutoGen AgentChat to run a small team of collaborating agents:

- PlannerAgent
- SearchAgent
- WriterAgent
- CriticAgent

The agents communicate and hand off tasks to produce a structured research report that is saved to disk.

---

## Features

- Orchestrated multi-agent workflow using AutoGen AgentChat.
- Web search powered by DuckDuckGo via `ddgs`.
- Web scraping using `newspaper4k` or BeautifulSoup heuristics.
- Token-aware summarization of search and scrape results.
- File read/write tools for agent collaboration.
- Persisted artifacts:
  - Raw search JSON results in `search_results/`
  - Raw scraped text in `scrape_results/`
  - Final synthesized reports in `output_results/`

---

## Architecture

Key runtime defined in `main.py`:

- Initializes an Azure-compatible chat model client via `autogen_ext.models.azure.AzureAIChatCompletionClient` using the GitHub Models endpoint `https://models.github.ai/inference` with the environment variable `PERSONAL_GITHUB_TOKEN`.
- Defines four agents with role-specific prompts in `prompt.py`:
  - PlannerAgent: decomposes the user task and coordinates the team.
  - SearchAgent: uses tools to search and scrape, collecting and summarizing sources.
  - WriterAgent: synthesizes findings into a structured report and writes it to a file.
  - CriticAgent: reviews the output file and requests revisions if needed.
- Registers tools from `tools/`:
  - `web_search` (DuckDuckGo) in `tools/search.py`
  - `web_scrape` (BeautifulSoup/newspaper4k) in `tools/scrape.py`
  - `read_file` and `write_output_to_file` in `tools/files.py`
- Runs a `Swarm` team with a `TextMentionTermination("FINISHED")` condition.

Prompts and agent descriptions are in `prompt.py`, including a structured report template that the WriterAgent follows.

---

## Requirements

- Python 3.13+ (see `pyproject.toml`)
- A GitHub personal access token with access to GitHub Models (for the AzureAIChatCompletionClient):
  - Environment variable: `PERSONAL_GITHUB_TOKEN`

The project uses these key dependencies (see `pyproject.toml`):

- `autogen-agentchat`, `autogen-core`, `autogen-ext[azure]`
- `ddgs` (DuckDuckGo search)
- `newspaper4k`, `bs4`, `requests`, `lxml-html-clean`
- `nltk`
- `python-dotenv`

Note: `nltk` downloads tokenizers at runtime (`punkt`, `punkt_tab`). An internet connection is required the first time.

---

## Setup

1. Clone the repository and enter the project directory.
2. Create a virtual environment (recommended) and install dependencies.

Using uv:

```bash
# Install uv if needed: https://github.com/astral-sh/uv
uv venv
uv pip install -e .
```

Using pip:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e .
```

3. Configure environment variables. Copy `.env.sample` to `.env` and set the token.

```bash
cp .env.sample .env
echo "PERSONAL_GITHUB_TOKEN=<your_github_models_token>" >> .env
```

---

## Usage

Run the orchestration:

```bash
python main.py
```

By default, `main.py` runs the team with a sample task string:

```python
await Console(deep_research_team.run_stream(task="AI Coding Tool effect on the software job market"))
```

You can change the research topic by editing the `task` string in `main.py`.

Outputs are written to:

- `search_results/` for raw search results (JSON)
- `scrape_results/` for raw scraped content (TXT)
- `output_results/` for final reports (Markdown)

The WriterAgent prints the path of the final report file. The CriticAgent may request revisions before the PlannerAgent finalizes the report with a `FINISHED` message.

---

## Tools Overview

- `tools/search.py` — `web_search(query, max_results=5)`
  - Uses DuckDuckGo via `DDGS` to fetch results.
  - Returns summarized results and the path to the full JSON file.

- `tools/scrape.py` — `web_scrape(url, max_return_tokens=300, use_newspaper=None)`
  - Heuristically chooses `newspaper4k` for news-like URLs, otherwise uses BeautifulSoup.
  - Returns a token-limited text snippet and the path to the full scraped text file.

- `tools/files.py` — `read_file(file_path)` and `write_output_to_file(content)`
  - Utilities for reading artifacts and persisting agent outputs.

---

## Project Structure

```
deep-research-agents/
├─ main.py                 # Orchestrates model, agents, team, and run loop
├─ prompt.py               # Agent descriptions and prompts
├─ tools/
│  ├─ files.py             # read/write tools
│  ├─ scrape.py            # web scraping tool
│  └─ search.py            # web search tool
├─ output_results/         # Final reports (Markdown)
├─ scrape_results/         # Raw scraped text (TXT)
├─ search_results/         # Raw search results (JSON)
├─ pyproject.toml          # Project metadata and dependencies
├─ uv.lock                 # Lockfile (if using uv)
├─ .env.sample             # Environment variable template
└─ README.md               # This file
```

---

## Troubleshooting

- Missing or invalid token: Ensure `PERSONAL_GITHUB_TOKEN` is set and valid for GitHub Models.
- NLTK data errors: Ensure internet access on first run; `nltk` downloads `punkt` and `punkt_tab`.
- Network issues during scraping/search: The tools handle common errors, but rate limits and connectivity can still cause failures.
- Python version: Use Python 3.13+ per `pyproject.toml`.
