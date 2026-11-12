# Delivery plan — Intelligent Ordering Platform RAG

## Objective
Deliver a local, demonstrable RAG baseline for an intelligent B2B ordering platform. The dataset is synthetic and contains clients, products, raw materials, orders, samples and RAG-ready documents.

## Required deliverables

1. **Usable dataset** — generated under `data/` and as `givaudan_data.txt` for direct ingestion by the starter repository.
2. **Representative baseline result** — baseline with `nomic-embed-text` and `qwen2.5:1.5b`; measured through a benchmark script.
3. **Feasibility proof** — ingestion, API health check and sample question scripts.
4. **Swagger/OpenAPI** — FastAPI automatically exposes `/docs` and `/openapi.json`.
5. **Dummy endpoint exposed through ngrok** — `GET /demo/ping`; it deliberately returns no business data.

## Recommended sequence

1. Fork `hmicn/example-rag` and clone the fork.
2. Install Python dependencies and Ollama models.
3. Add the dataset generator and generate the data.
4. Point `config.py` to `givaudan_data.txt`; ingest it with the starter repository pipeline.
5. Run the baseline benchmark and save its measured output.
6. Add the Swagger-described demo endpoint and publish it using ngrok.

## Security rule

Use synthetic/anonymised data only for the demo. Do not put real customer identities, proprietary formulations, raw-material composition, credentials, or internal order data in GitHub, ChromaDB or an ngrok-exposed endpoint.

## Minimum acceptance
- `python ingest.py givaudan_data.txt` completes.
- `python list.py` shows indexed chunks.
- `GET /health` returns the number of chunks and model names.
- `POST /search` returns relevant passages for a product/order question.
- `POST /ask` produces an answer grounded in returned context.
- `GET /demo/ping` is reachable locally and through ngrok.
