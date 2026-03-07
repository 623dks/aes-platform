# DeepTest
## Automated Essay Scoring Platform

Production-grade automated essay scoring system built on **Llama 3.1 8B with prompt-specific LoRA adapters**, deployed on **Google Cloud GPU infrastructure** with a **teacher audit portal, human review loop, and continuous QWK evaluation tracking**.

Students submit essays through a web interface. The system evaluates them using a fine-tuned language model, generates written justification, and routes the results to teachers for verification. Human feedback continuously measures how closely the model aligns with human scoring.

---

# Live System

| Component | Link |
|-----------|------|
| Student Portal | https://623dks.github.io/aes-platform |
| API Health | https://deep-aes-platform.duckdns.org/api/health |
| Author | https://www.linkedin.com/in/deep-shukla-b4035220a/ |
| Contact | deep.shukla@colorado.edu |

---

# System Architecture

```mermaid
flowchart LR

A[Student Web Portal<br>GitHub Pages] -->|POST /api/score| B[Nginx Reverse Proxy<br>HTTPS + SSL]

B --> C[FastAPI Backend<br>GPU Inference Server]

C --> D[vLLM Engine]

D --> E[Llama 3.1 8B Base Model]

E --> F[Multi-LoRA Adapter Router]

F --> G1[Prompt 1<br>Persuasive]
F --> G2[Prompt 2<br>Source Based]
F --> G3[Prompt 3<br>Informative]
F --> G4[Prompt 4<br>Narrative]
F --> G5[Prompt 5<br>Analytical]
F --> G6[Prompt 6<br>Descriptive]
F --> G7[Prompt 7<br>Compare Contrast]

C --> H[Groq API<br>Justification Generation]

C --> I[PostgreSQL Database]

I --> J[Teacher Audit Portal]

J --> K[Human Review]

K --> L[QWK Agreement Tracker]
Platform Workflow
Core Platform Features
Automated Essay Scoring

Fine tuned language model scores essays from 1 to 6 using rubric aligned evaluation.

Prompt Specific Model Adapters

Each essay type uses a dedicated LoRA adapter trained for its scoring rubric.

Human Audit Pipeline

Teachers validate AI scores, override incorrect predictions, and provide feedback.

Continuous Evaluation

Human feedback is used to compute Quadratic Weighted Kappa between AI and human scores.

Justification Generation

Each score is accompanied by a written explanation generated through Groq inference.

Confidence Based Review

Low confidence predictions automatically trigger human review.

Prompt Categories
ID	Prompt Type
1	Persuasive / Argumentative
2	Source Based / Evidence
3	Informative / Explanatory
4	Narrative / Creative
5	Analytical / Critical
6	Descriptive / Observational
7	Compare and Contrast
Scoring Rubric
Score	Description
6	Sophisticated language control with strong argument and evidence
5	Clear argument with developed reasoning
4	Adequate writing with some development
3	Partial development and limited clarity
2	Minimal structure and weak reasoning
1	Very limited content and language control
Model Training
Parameter	Value
Base Model	meta-llama/Llama-3.1-8B-Instruct
Dataset	ASAP Automated Student Assessment Prize
Training Method	QLoRA
LoRA Rank	16
LoRA Alpha	16
Dropout	0.05
Target Modules	q_proj, k_proj, v_proj, o_proj
Epochs	5
Batch Size	4 per device
Gradient Accumulation	4
Effective Batch	16
Learning Rate	2e-4 cosine decay
Precision	bfloat16
Quantization	4 bit NF4
Max Sequence Length	1024 tokens

Each adapter is trained independently for its prompt category.

Inference System
Parameter	Value
Runtime	vLLM 0.11.0
GPU	NVIDIA L4
GPU Memory	24GB
Max Model Length	4096 tokens
Concurrent LoRA Adapters	8
Adapter Selection	prompt_id routing

The base model loads once and LoRA adapters are dynamically swapped during inference.

API Reference

Base URL

https://deep-aes-platform.duckdns.org
Health Check
GET /api/health

Response

{
 "status": "healthy",
 "engine": "loaded",
 "db": "connected"
}
Score Essay
POST /api/score

Request

{
 "text": "essay content",
 "prompt_id": 1,
 "essay_id": "optional_student_id"
}

Response

{
 "id": "ESSAY_xxx",
 "score": 4,
 "justification": "...",
 "confidence": 0.9
}
Essay History
GET /api/history

Returns all scored essays ordered by submission time.

Teacher Feedback
POST /api/feedback
{
 "essay_id": "ESSAY_xxx",
 "is_validated": true,
 "teacher_score": 4,
 "teacher_comments": "..."
}
Teacher Portal Features

• Review AI scored essays
• Override AI score with human score
• Submit feedback and comments
• Flag essays for appeal
• Track agreement metrics between AI and human raters

Dashboard analytics include

• Average AI score
• Average human score
• QWK agreement metric
• Essay confidence tracking

Bias Considerations
Length Bias

Longer essays may receive slightly higher scores independent of quality. The portal enforces a 200 word minimum.

Vocabulary Bias

Rare vocabulary can sometimes influence scores disproportionately.

Confidence Threshold

Predictions below 0.75 confidence require human review.

Infrastructure
Component	Technology
Cloud Provider	Google Cloud Platform
Instance	g2-standard-4
GPU	NVIDIA L4
OS	Ubuntu 24
Backend	FastAPI
Model Runtime	vLLM
Reverse Proxy	Nginx
Database	PostgreSQL 15
Containerization	Docker
Frontend Hosting	GitHub Pages
SSL	Certbot with DuckDNS
Process Manager	systemd
Backups	Daily pg_dump
CI/CD	GitHub Actions
CI/CD Pipeline

Deployment time typically under two minutes.

Repository Structure
aes-platform

backend
  main.py

config
  default.yaml

docs
  home.html
  index.html
  reviewer.html

outputs
  adapters

src
  serving
    multi_lora.py

scripts
Local Setup

Clone repository

git clone https://github.com/623dks/aes-platform.git
cd aes-platform

Create environment

conda create -n aes-llama-310 python=3.10
conda activate aes-llama-310

Install dependencies

pip install vllm fastapi uvicorn asyncpg groq PyPDF2 python-docx pyyaml

Run PostgreSQL container

docker run -d \
 --name aes_postgres \
 -e POSTGRES_USER=aes_user \
 -e POSTGRES_PASSWORD=aes_password \
 -e POSTGRES_DB=aes_db \
 -p 5432:5432 \
 postgres:15

Run API server

DATABASE_URL="postgresql://aes_user:aes_password@localhost:5432/aes_db" \
GROQ_API_KEY="your_key_here" \
uvicorn backend.main:app --host 0.0.0.0 --port 8000
Evaluation Methodology

Model performance is evaluated using Quadratic Weighted Kappa (QWK) between AI predictions and human scores.

QWK penalizes large scoring disagreements more heavily and is widely used in standardized educational testing.

Model Performance

Average QWK across prompts: 0.633
Average adjacent agreement: 87%

Prompt Type	QWK	MAE	Exact Match	Adjacent Agreement
Persuasive	0.727	0.60	45%	95%
Source Based	0.665	0.65	45%	90%
Informative	0.607	0.80	35%	85%
Narrative	0.571	0.85	30%	85%
Analytical	0.740	0.55	50%	95%
Descriptive	0.413	1.05	20%	75%
Compare Contrast	0.705	0.75	40%	85%
Average	0.633	0.75	38%	87%

Prompt 6 currently underperforms and is flagged for adapter retraining.

Author

Deep Shukla
University of Colorado Boulder

LinkedIn
https://www.linkedin.com/in/deep-shukla-b4035220a/

Email
deep.shukla@colorado.edu


---

### Small comment after the README

This version improves three things:

1. **Mermaid architecture diagrams** which render visually on GitHub  
2. **Sequence diagram of the workflow** which makes reviewers understand the pipeline instantly  
3. **Clear professional ordering** similar to engineering repos from large companies

If you want, I can also give you a **very advanced architecture diagram (GPU serving + LoRA router + 
