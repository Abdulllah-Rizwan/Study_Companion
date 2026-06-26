## The Project: One-Sentence Spec


A web app where I upload my course materials (PDFs of slides, notes, past papers I have rights to) and query them in natural language to get answers grounded in my own materials, with citations, deployed on AWS, with a second user account demonstrating multi-tenant isolation.



## Stack (final, do not change without justification):


1. Frontend: Minimal React or plain HTML+JS. Not the focus.
2. Backend: FastAPI (Python).
3. Storage: S3 for raw documents.
4. Vector DB: pgvector on Amazon RDS (PostgreSQL). Why: cheapest reliable option in your budget. 5. Pinecone has a free tier but adds a vendor dependency.
6. Embeddings + LLM: Amazon Bedrock (Titan Embeddings + Claude Haiku or Nova Lite). Why: pay-per-call, no idle cost, fits the budget. Fall back to OpenAI API if Bedrock latency is bad in your region.
7. Compute: AWS App Runner or ECS Fargate. Why: no servers to manage, scales to zero or near-zero, fits the budget.
8. Auth: Amazon Cognito for week 6+. Single-user before that.
9. IaC: Terraform.
10. CI/CD: GitHub Actions.
11. Monitoring: CloudWatch (logs + basic metrics).