from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
import os

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_real_justification(essay_text, score, prompt_id):
    try:
        msg = "Essay (Category {}): {}\n\nThis essay scored {} out of 6. Give a 2-3 sentence specific justification.".format(prompt_id, essay_text[:600], score)
        chat = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an expert essay grader. Be specific about strengths and weaknesses."},
                {"role": "user", "content": msg}
            ],
            max_tokens=150
        )
        return chat.choices[0].message.content.strip()
    except Exception as e:
        return "Score {}/6 assigned based on essay analysis.".format(score)

import io
import json
import time
import random
import asyncio
from contextlib import asynccontextmanager
from typing import Optional
import PyPDF2
import docx
import yaml
import asyncpg
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

class ScoreRequest(BaseModel):
    essay_id: Optional[str] = None
    text: str
    prompt_id: int

class FeedbackRequest(BaseModel):
    essay_id: str
    is_validated: bool
    teacher_score: int
    teacher_comments: str

DB_URL = os.getenv("DATABASE_URL", "postgresql://aes_user:aes_password@localhost:5432/aes_db")
db_pool = None
engine = None

async def init_db(pool):
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS essays (
                id TEXT PRIMARY KEY,
                prompt_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                ai_score INTEGER,
                ai_justification TEXT,
                ai_confidence FLOAT,
                is_validated INTEGER DEFAULT 0,
                teacher_score INTEGER,
                teacher_comments TEXT,
                created_at DOUBLE PRECISION
            )
        """)

def load_engine(config):
    global engine
    try:
        import sys
        sys.path.insert(0, "/home/g623dks")
        from src.serving.multi_lora import MultiLoRAEngine
        adapters_dir = config["paths"]["adapters_dir"]
        base_model = config["model"]["name"]
        adapters_config = {}
        if os.path.exists(adapters_dir):
            for dirname in os.listdir(adapters_dir):
                if dirname.startswith("set_") and dirname.endswith("_llama"):
                    try:
                        prompt_id = int(dirname.split("_")[1])
                        adapters_config[prompt_id] = {"name": dirname, "path": os.path.join(adapters_dir, dirname)}
                    except:
                        continue
        if adapters_config:
            engine = MultiLoRAEngine(base_model, adapters_config)
            print(f"Engine loaded with {len(adapters_config)} adapters.")
        else:
            print("WARNING: No adapters found.")
    except Exception as e:
        print(f"Engine load error: {e}")

@asynccontextmanager
async def lifespan(app):
    global db_pool
    db_pool = await asyncpg.create_pool(DB_URL, min_size=2, max_size=10)
    await init_db(db_pool)
    print("PostgreSQL connected.")
    config_path = "/home/g623dks/config/default.yaml"
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = yaml.safe_load(f)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, load_engine, config)
    yield
    await db_pool.close()

app = FastAPI(title="Multi-LoRA AES API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/score")
async def score_essay(request: ScoreRequest):
    if engine is None:
        raise HTTPException(status_code=503, detail="Engine not ready.")
    if not request.text:
        raise HTTPException(status_code=400, detail="No essay text.")

    # Word count guardrails
    word_count = len(request.text.strip().split())

    if word_count > 800:
        return {"id": None, "prompt_id": request.prompt_id, "score": 0,
                "justification": "Essay exceeds the 800-word limit ({} words). Please shorten your essay to between 350 and 700 words for accurate scoring.".format(word_count),
                "confidence": 1.0}

    if word_count < 150:
        return {"id": None, "prompt_id": request.prompt_id, "score": 0,
                "justification": "Essay is too short ({} words). A minimum of 150 words is required for scoring.".format(word_count),
                "confidence": 1.0}

    if word_count < 200:
        return {"id": None, "prompt_id": request.prompt_id, "score": 1,
                "justification": "Essay is below the recommended minimum length ({} words). Note: essay length is below the recommended minimum which may affect score reliability.".format(word_count),
                "confidence": 0.95}

    try:
        req_data = {"essay_id": request.essay_id or f"U_{random.randint(1000,9999)}", "text": request.text, "prompt_id": request.prompt_id}
        results = engine.generate_batch([req_data])
        res = results[0]
        score = res.get("score")

        justification = get_real_justification(request.text, score, request.prompt_id)
        confidence = res.get("confidence", 0.9)
        db_id = f"ESSAY_{int(time.time())}_{random.randint(100,999)}"
        async with db_pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO essays (id,prompt_id,text,ai_score,ai_justification,ai_confidence,is_validated,teacher_score,teacher_comments,created_at) VALUES ($1,$2,$3,$4,$5,$6,0,NULL,NULL,$7)",
                db_id, request.prompt_id, request.text, score, justification, confidence, time.time()
            )
        return {"id": db_id, "prompt_id": request.prompt_id, "score": score, "justification": justification, "confidence": confidence}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_history():
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM essays ORDER BY created_at DESC")
    return [dict(r) for r in rows]

@app.post("/api/feedback")
async def save_feedback(req: FeedbackRequest):
    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE essays SET is_validated=$1, teacher_score=$2, teacher_comments=$3 WHERE id=$4",
            req.is_validated, req.teacher_score, req.teacher_comments, req.essay_id)
    return {"status": "success"}

@app.get("/api/health")
async def health_check():
    try:
        async with db_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        db_status = "connected"
    except:
        db_status = "error"
    return {"status": "healthy" if engine else "degraded", "engine": "loaded" if engine else "not_loaded", "db": db_status}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False)

@app.post("/api/score-file")
async def score_file(file: UploadFile = File(...), prompt_id: int = Form(...), essay_id: str = Form(None)):
    if engine is None:
        raise HTTPException(status_code=503, detail="Engine not ready.")
    text = extract_text_from_file(file)
    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from file.")
    req_data = {"essay_id": essay_id or f"U_{random.randint(1000,9999)}", "text": text, "prompt_id": prompt_id}
    results = engine.generate_batch([req_data])
    res = results[0]
    score = res.get("score")
    justification = get_real_justification(text, score, prompt_id)
    confidence = res.get("confidence", 0.9)
    db_id = f"ESSAY_{int(time.time())}_{random.randint(100,999)}"
    async with db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO essays (id,prompt_id,text,ai_score,ai_justification,ai_confidence,is_validated,teacher_score,teacher_comments,created_at) VALUES ($1,$2,$3,$4,$5,$6,0,NULL,NULL,$7)",
            db_id, prompt_id, text, score, justification, confidence, time.time()
        )
    return {"id": db_id, "prompt_id": prompt_id, "score": score, "justification": justification, "confidence": confidence}
