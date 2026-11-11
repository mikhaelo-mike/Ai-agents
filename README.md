# Company Info Assistant

A small learning project: ask questions about one company's information and get grounded answers. It uses LangChain for document splitting, embeddings, retrieval, and prompting; LangGraph connects retrieval and answering; FastAPI exposes one endpoint.

## How it works

1. `data/company_info.md` is split into small text chunks.
2. Gemini embeddings put the chunks into an in-memory vector store.
3. The retriever finds relevant chunks for a question.
4. A two-step LangGraph retrieves context and asks the chat model to answer from it.
5. `POST /ask` returns the answer and source filenames.

The vector store is rebuilt in memory when the app starts answering questions. This keeps the project simple; it is not persistent between restarts.

## Run locally

Requires Python 3.11+ and a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

Add your `GEMINI_API_KEY` to `.env`, then run:

```powershell
python -m uvicorn company_assistant.api:app --reload --app-dir src
```

Open <http://localhost:8000/docs> to try `POST /ask`. Example body:

```json
{"question": "How long does delivery take?"}
```

`GET /health` checks that the API is running. Without a Gemini API key, `/ask` responds with a clear setup error.

## Run with Docker

Set `GEMINI_API_KEY` in your shell, then run:

```powershell
$env:GEMINI_API_KEY = "your-key"
docker compose up --build
```

The API is available at <http://localhost:8000/docs>.

## Deploy to Render

1. Push this project, including `render.yaml`, to a GitHub repository.
2. In Render, choose **New → Blueprint**, connect that repository, and deploy the `company-info-assistant` service.
3. Set `GEMINI_API_KEY` as a secret in Render. Do not commit the key to GitHub.
4. Open the service's `/docs` URL to try `POST /ask`.

The Blueprint uses Render's free plan. Free web services can sleep when idle and may take a little time to respond after waking.
This learning demo leaves `/ask` public and unauthenticated. Anyone with the URL can use it, which can incur Gemini API charges; don't use this setup for sensitive or production workloads.

## Run tests

```powershell
python -m pytest
```

Tests use a fake retriever and chat model, so they do not need an API key.

## Project map

- `src/company_assistant/api.py` — HTTP endpoints and model wiring
- `src/company_assistant/knowledge.py` — load, split, and index company information
- `src/company_assistant/graph.py` — retrieval and answer workflow
- `src/company_assistant/config.py` — environment configuration
- `data/company_info.md` — sample company facts; replace with your own
- `.github/workflows/test.yml` — run tests on GitHub Actions
- `render.yaml` — Render Blueprint deployment settings
