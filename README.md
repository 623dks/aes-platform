# DeepTest: Automated Essay Scoring Platform

A production-grade automated essay scoring system built on Llama 3.1 8B with prompt-specific LoRA adapters, deployed on GCP with a live teacher audit portal and CI/CD via GitHub Actions.

**Live Demo:** [https://623dks.github.io/aes-platform](https://623dks.github.io/aes-platform)  
**API:** [https://deep-aes-platform.duckdns.org/api/health](https://deep-aes-platform.duckdns.org/api/health)  
**Author:** [Deep Shukla](https://www.linkedin.com/in/deep-shukla-b4035220a/) | deep.shukla@colorado.edu

---

## Overview

Students submit essays through a web portal. The system scores each essay from 1 to 6 using a fine-tuned language model, generates a written justification via Groq inference, and routes the result to a teacher audit queue. Teachers can approve the AI score, override it with a human score, flag essays for appeal, and leave feedback. All interactions feed a QWK (Quadratic Weighted Kappa) tracker that measures how closely the model aligns with human judgment over time.

---

## System Architecture

\`\`\`
Student Portal (GitHub Pages, HTTPS)
        |
        | POST /api/score
        v
Nginx Reverse Proxy + Let's Encrypt SSL
        |
        v
FastAPI Backend  --  GCP g2-standard-4 (NVIDIA L4 24GB)
        |
        |-- vLLM Engine (multi-LoRA hot-swap, Llama 3.1 8B)
        |       |-- set_1_llama   Persuasive / Argumentative
        |       |-- set_2_llama   Source-Based / Evidence
        |       |-- set_3_llama   Informative / Explanatory
        |       |-- set_4_llama   Narrative / Creative
        |       |-- set_5_llama   Analytical / Critical
        |       |-- set_6_llama   Descriptive / Observational
        |       |-- set_7_llama   Compare and Contrast
        |
        |-- Groq API  (llama-3.1-8b-instant, justification text)
        |
        v
PostgreSQL 15 (Docker container, essay storage and feedback)
        |
        v
Teacher Portal (GitHub Pages, QWK tracking and audit queue)
\`\`\`

---

## CI/CD Pipeline

Every push to main triggers GitHub Actions to deploy the /docs folder to GitHub Pages automatically. No manual steps needed for frontend changes.

\`\`\`
git push origin main
        |
        v
GitHub Actions: pages-build-deployment
        |
        v
GitHub Pages live (under 2 minutes)
\`\`\`

---

## Model Training

| Parameter | Value |
|-----------|-------|
| Base model | meta-llama/Llama-3.1-8B-Instruct |
| Dataset | ASAP (Automated Student Assessment Prize) |
| Method | QLoRA fine-tuning |
| LoRA rank | 16 |
| LoRA alpha | 16 |
| Dropout | 0.05 |
| Target modules | q_proj, k_proj, v_proj, o_proj |
| Epochs | 5 |
| Batch size | 4 per device |
| Gradient accumulation | 4 steps (effective batch 16) |
| Learning rate | 2e-4 with cosine decay |
| Precision | bfloat16 |
| Quantization | 4-bit NF4 (BitsAndBytes) |
| Max sequence length | 1024 tokens |

One adapter is trained per essay prompt category. Each adapter learns the scoring rubric specific to its prompt type rather than a single generalized scoring function.

---

## Inference

| Parameter | Value |
|-----------|-------|
| Runtime | vLLM 0.11.0 |
| GPU | NVIDIA L4 23GB |
| GPU memory utilization | 90% |
| Max model length | 4096 tokens |
| Max concurrent LoRA adapters | 8 |
| LoRA rank at inference | 16 |
| Adapter selection | Automatic via prompt_id |

---

## API Reference

Base URL: https://deep-aes-platform.duckdns.org

### GET /api/health

\`\`\`json
{ "status": "healthy", "engine": "loaded", "db": "connected" }
\`\`\`

### POST /api/score

Request:
\`\`\`json
{ "text": "essay content", "prompt_id": 1, "essay_id": "STU_optional" }
\`\`\`

Response:
\`\`\`json
{ "id": "ESSAY_xxx", "score": 4, "justification": "...", "confidence": 0.9 }
\`\`\`

### GET /api/history
Returns all scored essays ordered by submission time.

### POST /api/feedback
\`\`\`json
{ "essay_id": "ESSAY_xxx", "is_validated": true, "teacher_score": 4, "teacher_comments": "..." }
\`\`\`

---

## Prompt Categories

| ID | Type |
|----|------|
| 1 | Persuasive / Argumentative |
| 2 | Source-Based / Evidence |
| 3 | Informative / Explanatory |
| 4 | Narrative / Creative |
| 5 | Analytical / Critical |
| 6 | Descriptive / Observational |
| 7 | Compare and Contrast |

---

## Scoring Rubric

| Score | Description |
|-------|-------------|
| 6 | Sophisticated control of language, well-developed argument, strong evidence |
| 5 | Clear control of language, developed argument, adequate evidence |
| 4 | Adequate control of language, some development, relevant evidence |
| 3 | Partial control of language, limited development, general evidence |
| 2 | Limited control of language, minimal development, weak evidence |
| 1 | Little or no control of language, undeveloped, little relevant content |

---

## Teacher Portal Features

- QWK score between AI and human reviewer scores
- Average AI and human scores across all reviewed submissions
- Per-essay trait breakdown across Content, Organization, Voice, Word Choice, and Conventions
- Low confidence flagging for essays below 0.75 confidence threshold
- Approve or reject AI score with optional human score override
- Appeal flagging for student-contested scores
- 200-word feedback limit with live word count

---

## Bias Considerations

**Length bias:** longer essays tend to receive higher scores independent of quality. Teacher review is recommended for short submissions. The portal enforces a 200-word minimum at submission time.

**Vocabulary bias:** the model may reward uncommon vocabulary. Teacher override is available for any score.

**Confidence threshold:** essays below 0.75 confidence are flagged for mandatory human review.

---

## Infrastructure

| Component | Stack |
|-----------|-------|
| Compute | GCP g2-standard-4 (4 vCPU, 16GB RAM) |
| GPU | NVIDIA L4 23GB, CUDA 12.4 |
| OS | Ubuntu 24 |
| Python | 3.10 (conda) |
| API framework | FastAPI + uvicorn |
| Reverse proxy | Nginx + Let's Encrypt |
| Database | PostgreSQL 15 via Docker |
| Frontend hosting | GitHub Pages |
| SSL | DuckDNS + Certbot auto-renewal |
| Backups | Daily pg_dump, 7-day retention |
| Process management | systemd with auto-restart |
| CI/CD | GitHub Actions |

---

## Repository Structure

\`\`\`
aes-platform/
├── backend/
│   └── main.py
├── config/
│   └── default.yaml
├── docs/
│   ├── home.html
│   ├── index.html
│   └── reviewer.html
├── outputs/
│   └── adapters/
├── src/
│   └── serving/
│       └── multi_lora.py
└── scripts/
\`\`\`

---

## Local Setup

\`\`\`bash
git clone https://github.com/623dks/aes-platform.git
cd aes-platform

conda create -n aes-llama-310 python=3.10
conda activate aes-llama-310
pip install vllm fastapi uvicorn asyncpg groq PyPDF2 python-docx pyyaml

docker run -d --name aes_postgres \
  -e POSTGRES_USER=aes_user \
  -e POSTGRES_PASSWORD=aes_password \
  -e POSTGRES_DB=aes_db \
  -p 5432:5432 postgres:15

DATABASE_URL="postgresql://aes_user:aes_password@localhost:5432/aes_db" \
GROQ_API_KEY="your_key_here" \
uvicorn backend.main:app --host 0.0.0.0 --port 8000
\`\`\`

---

## Evaluation

Model performance is measured using Quadratic Weighted Kappa against held-out test splits from each prompt category. QWK penalizes large score disagreements more than small ones, matching how human raters are evaluated in standardized testing contexts like those used by Pearson and ETS.

The teacher portal tracks live QWK as reviewers submit feedback, giving a continuous view of human-AI agreement across the deployed system.

---

Built by [Deep Shukla](https://www.linkedin.com/in/deep-shukla-b4035220a/)  
University of Colorado | deep.shukla@colorado.edu
