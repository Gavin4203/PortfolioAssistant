# Personal Career & Portfolio Assistant

An LLM-powered tool that treats your own professional documents, resume, cover letters, project READMEs, as a local, private knowledge base. No cloud servers. Everything runs against your own files, on your own machine.

**It's not built for one job.** The RAG layer pulls from whatever documents you point it at, and the drafting agent works off what your files say about what you do. A software engineer, a teacher, a nurse, a graphic designer, same tool, different answers. Nothing is hardcoded to a specific field or seniority level.

## What it does

**RAG over your own work.** Ingests your resume, past cover letters, project docs into a local Qdrant vector store via LlamaIndex. Allowing it to pull specific projects and details from your files rather than hallucinating a generic answer.

**Cover-letter drafting agent.** You paste in a job description, and a LangGraph agent loops: pulls matching skills and experience from your vector store, drafts a targeted pitch, and lets you iterate. It's not "write me a generic cover letter." It's "here's what you did that maps to this role."

**Output is CLI-first with a save dialog.** The whole flow is a terminal session. When the agent produces a final document, the code extracts the clean text and opens a save dialog so you can drop it wherever you want (see [Usage](#usage) for the full flow). You can also export to PDF (WeasyPrint), `.odt`, `.docx`, or `.md` depending on what you ask for.

## Model

Designed and tested against `llama3.2:8b` running locally via Ollama. The RAG retrieval depth and the agent's tool-loop structure all trade off against that model's context window and instruction-following ceiling. It will run on other Ollama models, but the prompts are tuned for 8b-class reasoning.

## How to run

**Prerequisites:**

- Python 3.11+
- [Ollama](https://ollama.com) running locally with your LLM and embedding model pulled
- `zenity` (Linux only): the output-save dialog — optional if you only need terminal output (see [Usage](#usage))

Qdrant runs as a local, file-based store via the `qdrant-client` pip package, your vectors live in a directory you point it at, and that's it.

**Install:**

```bash
git clone <repo-url>
cd <repo-dir>
python -m venv .venv && source .venv/bin/activate

pip install -r requirements.txt
```

**Start Ollama:**

```bash
ollama serve &
ollama pull llama3.2:8b
ollama pull nomic-embed-text
```

That's the only external process. Qdrant doesn't need one.

**Configure:**

Everything is set via a `.env` file (loaded by `python-dotenv`) with fallbacks in `config.py`. The ones you'll actually touch:

| Variable | What it does |
|---|---|
| `USER_DATA` | Path to the folder containing your resume, cover letters, project docs 
| `QDRANT_DATA` | Where the local Qdrant store lives (a directory, created on first run) |
| `COLLECTION_NAME` | Name of the Qdrant collection |

> **Note:** `QDRANT_DATA` is where embeddings of your files live. Treat that directory the same way you treat `USER_DATA`, it's sensitive. Both are in `.gitignore`. Don't un-ignore either.

**First run:**

```bash
python main.py
```

On first launch it will ask:

```
Run RAG Setup (Y/n)
 > y
Overwrite ALL Data (Y/n)
 > n
```

Saying `y` to setup reads every file in `USER_DATA`, chunks it, embeds it with `nomic-embed-text`, and writes the vectors into the local Qdrant store at `QDRANT_DATA`. On subsequent runs you can skip setup (type `n`) and it just loads the existing collection.

The overwrite prompt only matters if you've restructured your docs and want a clean re-embed. It deletes the collection and rebuilds from scratch.

**Usage:**

It's a terminal loop, not a subcommand CLI. After setup (or skipping it) you get:

```
--- Your Question Below (Enter '/end' to process input OR '/bye' to exit) ---
```

Type your question. It can be multi-line — keep typing until you're done, then hit the terminator:

| Command | What it does |
|---|---|
| `/end` | Sends your input to the LangGraph agent and prints the response |
| `/end-t` | Same, but also prints the retrieved source chunks (useful for checking that the RAG layer pulled the right stuff) |
| `/bye` | Closes the Qdrant client and exits |

If the agent's output is a cover letter or resume (i.e. the model wrapped it in the expected tag), the code intercepts it and fires the `zenity` save dialog so you can pick a folder and filename. The file is written out in the format you requested. The response is also printed to the terminal, so if you can't use `zenity` (or are on a non-Linux system), you can still copy the outcome directly.

## Platform

**Linux only, for now.** The file-save dialog uses `zenity` (GTK). Windows and macOS support is on the list but hasn't been built.

If you're on Linux and want the save dialog, install `zenity`. That's the only external binary dependency.

```bash
# Fedora / RHEL
sudo dnf install zenity

# Debian / Ubuntu
sudo apt install zenity

# Arch
sudo pacman -S zenity
```

Everything else is Python + Ollama + Qdrant.

### Key libraries

The full pinned list lives in `requirements.txt`. The ones that actually do the work:

| What | Library |
|---|---|
| Local LLM runtime | `ollama` |
| RAG pipeline (chunking, embedding, retrieval) | `llama-index-core`, `llama-index-embeddings-ollama`, `llama-index-llms-ollama` |
| Vector store | `qdrant-client` |
| Agent orchestration / tool loops | `langgraph`, `langchain-core`, `langchain-ollama` |
| Document parsing / conversion | `pypandoc`, `nltk`, `filetype` |
| PDF output | `weasyprint` |
| Templating (cover letters) | `Jinja2` |
| Data validation / settings | `pydantic`, `pydantic-settings`, `python-dotenv` |
| Async HTTP (Ollama API, etc.) | `aiohttp`, `httpx` |
| Retries / async glue | `tenacity`, `nest-asyncio` |
| Testing | `pytest`, `pytest-asyncio` |

## Status

RAG and the agent are functional. The third planned piece, fine-tuning a small model on samples of your writing so the output sounds like you instead of "I am excited to leverage my synergistic expertise", **never got built.** I got to that point, and decided I would use a stronger model, so I can have this do more than just write cover letters or resumes.

So: this repo has two working features and a gap where the third was going to be. I'm rebuilding the core in a new repo, with the same goals, and more power to complete new goals. But *this* repo is the one where the RAG and agent code actually exists and is readable.

## Notes

- The `Data/` directory is the parent folder for both your source documents (`USER_DATA`) and the local Qdrant vector store (`QDRANT_DATA`). It's in `.gitignore`. Don't un-ignore it. Point `USER_DATA` and `QDRANT_DATA` to subdirectories under it (e.g. `Data/documents/` and `Data/qdrant/`).
- `zenity` is the only external binary dependency. Everything else is Python + Ollama + Qdrant.
