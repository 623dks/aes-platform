# Multi-LoRA Automated Essay Scoring (AES)

This repository contains the complete, working codebase to validate the claims made in the Pearson Technical Proposal (*Multi-LoRA for Scalable Automated Essay Scoring*).

## The Core Argument Supported by this Code
Instead of training 50 separate 14GB models for 50 different exams, this architecture uses **one shared 4GB base model** (Llama-3.1-8B quantized) and loads **50 separate 17MB LoRA adapters**. 

This reduces GPU memory requirements by **>99%** while maintaining state-of-the-art Generative AI explainability (each essay receives a holistic score and a rubric-aligned justification).

## Architecture Overview

1. **AI Layer**: Llama-3.1-8B-Instruct (Decoder) *vs* Flan-T5-XL (Encoder-Decoder comparison)
2. **Serving**: vLLM with PagedAttention and Multi-LoRA continuous batching
3. **Data**: ASAP 2.0 & PERSUADE Corpus (human-scored essays, multiple prompts)
4. **Platform**: Designed for SLURM scheduling on CURC GPU clusters (A100s)

## Getting Started on CURC

### 1. Environment Setup (Alpine Cluster)
If using Open OnDemand or a Jupyter Terminal, first run initialization:
```bash
module load anaconda
conda init bash
source ~/.bashrc
```
Then create the environment:
```bash
conda create -n aes python=3.10
conda activate aes
pip install -r requirements.txt
```

### 2. Download Training Data
Downloads the ASAP 2.0 dataset via the Kaggle API. Note: you must have `~/.kaggle/kaggle.json` configured.
```bash
python scripts/download_data.py
```

### 3. Parallel Training (SLURM)
Trains 7 separate LoRA adapters (one for each essay set prompt) simultaneously across 7 A100s.
```bash
sbatch slurm/train.sh
```

### 4. Evaluation (QWK Metric)
Evaluates the trained adapters against the held-out test sets using the Quadratic Weighted Kappa metric, the AES industry standard.
```bash
sbatch slurm/evaluate.sh
```

### 5. Multi-LoRA Web Dashboard Demo
Launch the vLLM inference engine and the FastAPI gateway on a compute node:
```bash
sbatch slurm/serve.sh
```
Check the SLURM output log to find the node name (e.g., `cnode01`). Then set up port forwarding from your laptop:
```bash
ssh -L 8000:cnode01:8000 your_username@login.rc.colorado.edu
```
Finally, open a browser on your laptop and go to `http://localhost:8000` to use the UI.

## File Map

* `config/default.yaml` — All hyperparameters (rank=8, batch size, learning rates)
* `slurm/` — Batch submission scripts for CURC
* `src/model/setup.py` — QLoRA configuration (fp4 base model loading)
* `src/evaluation/qwk.py` — Cohen's Kappa implementation from scratch
* `src/serving/multi_lora.py` — The vLLM continuous batching magic
* `backend/` and `frontend/` — The demonstration UI
