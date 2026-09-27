# Course Materials Q&A

Upload my own course materials (PDFs of slides, notes, past papers I have the rights to), ask questions in natural language, and get answers grounded in those documents — with citations. Deployed on AWS, with a second user account demonstrating multi-tenant isolation.

**Status:** early development. See [progress.md](progress.md) for the build log.

## The Project: One-Sentence Spec

A web app where I upload my course materials (PDFs of slides, notes, past papers I have rights to) and query them in natural language to get answers grounded in my own materials, with citations, deployed on AWS, with a second user account demonstrating multi-tenant isolation.

## Stack (final, do not change without justification)

1. Frontend: Minimal React or plain HTML+JS. Not the focus.
2. Backend: FastAPI (Python).
3. Storage: S3 for raw documents.
4. Vector DB: pgvector on Amazon RDS (PostgreSQL). Why: cheapest reliable option in your budget.
5. Pinecone has a free tier but adds a vendor dependency.
6. Embeddings + LLM: Amazon Bedrock (Titan Embeddings + Claude Haiku or Nova Lite). Why: pay-per-call, no idle cost, fits the budget. Fall back to OpenAI API if Bedrock latency is bad in your region.
7. Compute: AWS App Runner or ECS Fargate. Why: no servers to manage, scales to zero or near-zero, fits the budget.
8. Auth: Amazon Cognito for week 6+. Single-user before that.
9. IaC: Terraform.
10. CI/CD: GitHub Actions.
11. Monitoring: CloudWatch (logs + basic metrics).

## How it works

Retrieval-augmented generation (RAG), end to end:

1. **Upload** — a PDF is posted to the API and the raw file is stored in S3.
2. **Extract** — text is pulled out of the PDF page by page.
3. **Chunk** — the text is split into overlapping chunks, each keeping its document and page number as metadata.
4. **Embed** — every chunk is turned into a vector with Titan Embeddings via Bedrock.
5. **Store** — the chunks and their vectors are written to pgvector on RDS.
6. **Retrieve** — a question is embedded the same way and the top-k nearest chunks are fetched.
7. **Answer** — the chat model is asked to answer *only* from those chunks, and the response comes back with citations (document + page).

Every row is scoped to a user (tenant), and retrieval filters on that scope — that is what makes the second account's isolation demonstrable rather than assumed.

## Project structure

```
.
├── main.py            # FastAPI app entrypoint
├── pyproject.toml     # dependencies and tool config
├── progress.md        # build log / running notes
└── .python-version    # pinned Python version
```

Terraform config, migrations and CI workflows land alongside these as the weeks go on (see the roadmap below).

## Getting started

### Prerequisites

- Python, at the version pinned in `.python-version`.
- An AWS account with Bedrock model access granted for Titan Embeddings and the chat model you pick.
- A PostgreSQL database with the `pgvector` extension available — either a local `pgvector/pgvector` Docker image or Amazon RDS.
- AWS credentials configured locally (`aws configure` or environment variables), and Terraform once infrastructure work starts.

### Install

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

Or use whatever tool owns `pyproject.toml` (`uv sync`, `poetry install`, ...) if a lockfile is present.

### Configure

Settings come from the environment:

| Variable | Purpose |
| --- | --- |
| `AWS_REGION` | Region used for Bedrock, S3 and RDS calls. |
| `S3_BUCKET` | Bucket holding the uploaded source PDFs. |
| `DATABASE_URL` | PostgreSQL connection string for the pgvector store. |
| `BEDROCK_EMBEDDING_MODEL_ID` | Titan Embeddings model id (e.g. `amazon.titan-embed-text-v2:0`). |
| `BEDROCK_LLM_MODEL_ID` | Claude Haiku or Nova Lite model id used to write answers. |
| `OPENAI_API_KEY` | Optional fallback if Bedrock latency is bad in your region. |
| `COGNITO_USER_POOL_ID` / `COGNITO_CLIENT_ID` | Only needed once auth lands (week 6+). |

### Run

```bash
uvicorn main:app --reload
```

The interactive API docs are then at http://127.0.0.1:8000/docs.

## Deployment

Terraform provisions the infrastructure (S3 bucket, RDS instance with pgvector, App Runner or ECS Fargate service), GitHub Actions builds and deploys on push, and CloudWatch collects logs and basic metrics. Bedrock and Cognito stay managed services — no infrastructure of my own to run for either.

## Roadmap

- [ ] Single-user ingestion: upload a PDF, chunk, embed, store in pgvector.
- [ ] Query endpoint returning an answer with citations.
- [ ] Minimal frontend for upload and asking questions.
- [ ] Terraform + deploy to App Runner/ECS Fargate.
- [ ] Cognito auth and a second account to prove tenant isolation.
- [ ] CI/CD via GitHub Actions, dashboards and alarms in CloudWatch.

Keep [progress.md](progress.md) updated as this moves — it is the source of truth for where the project actually is.

## License

Personal learning project; no license chosen yet.
