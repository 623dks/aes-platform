const API_BASE = window.MARE_API_BASE || "";

const scoreBtn        = document.getElementById("score-btn");
const examSelect      = document.getElementById("exam-select");
const essayInput      = document.getElementById("essay-input");
const wordCount       = document.getElementById("word-count");
const charCount       = document.getElementById("char-count");
const statusPill      = document.getElementById("status-pill");
const statusText      = document.getElementById("status-text");
const emptyState      = document.getElementById("empty-state");
const results         = document.getElementById("results");
const scoreNumber     = document.getElementById("score-number");
const scoreBand       = document.getElementById("score-band");
const scoreBar        = document.getElementById("score-bar");
const confValue       = document.getElementById("conf-value");
const justText        = document.getElementById("justification-text");
const traceGrid       = document.getElementById("trace-grid");
const teacherScore    = document.getElementById("teacher-score");
const teacherComments = document.getElementById("teacher-comments");
const feedbackBtn     = document.getElementById("feedback-btn");

let currentEssayId = null;

async function checkHealth() {
  try {
    const res  = await fetch(API_BASE + "/api/health");
    const data = await res.json();
    if (data.status === "healthy") {
      statusPill.className = "status-pill online";
      statusText.textContent = "Engine Online";
    } else {
      statusPill.className = "status-pill offline";
      statusText.textContent = "Engine Degraded";
    }
  } catch {
    statusPill.className = "status-pill offline";
    statusText.textContent = "Offline";
  }
}

checkHealth();
setInterval(checkHealth, 30000);

essayInput.addEventListener("input", () => {
  const text  = essayInput.value;
  const words = text.trim() === "" ? 0 : text.trim().split(/\s+/).length;
  wordCount.textContent = words + " word" + (words !== 1 ? "s" : "");
  charCount.textContent = text.length + " chars";
});

function getBand(score) {
  if (score <= 1) return "Below Basic";
  if (score <= 2) return "Basic";
  if (score <= 3) return "Developing";
  if (score <= 4) return "Proficient";
  if (score <= 5) return "Advanced";
  return "Exemplary";
}

function renderResults(data, latencyMs, promptId) {
  currentEssayId = data.id;
  const score      = data.score || 0;
  const confidence = data.confidence || 0.92;
  const pct        = Math.round((score / 6) * 100);

  scoreNumber.textContent = score;
  scoreBand.textContent   = getBand(score);
  confValue.textContent   = (confidence * 100).toFixed(1) + "%";
  justText.textContent    = data.justification || "No justification provided.";

  requestAnimationFrame(() => {
    scoreBar.style.width = pct + "%";
  });

  const examName = examSelect.options[examSelect.selectedIndex].text;
  const traceItems = [
    ["Base Model",  "Llama-3.1-8B (4-bit)"],
    ["Active LoRA", "Set " + promptId + " (~17MB)"],
    ["Engine",      "vLLM Continuous Batching"],
    ["Latency",     latencyMs + "ms"],
    ["Essay ID",    data.id],
    ["Exam",        examName.split("-")[0].trim()],
  ];
  traceGrid.innerHTML = traceItems.map(function(item) {
    return "<div class=\"trace-item\"><div class=\"trace-key\">" + item[0] + "</div><div class=\"trace-val\">" + item[1] + "</div></div>";
  }).join("");

  emptyState.classList.add("hidden");
  results.classList.remove("hidden");
  teacherScore.value    = "";
  teacherComments.value = "";
}

scoreBtn.addEventListener("click", async function() {
  const text     = essayInput.value.trim();
  const promptId = parseInt(examSelect.value);

  if (!text) {
    essayInput.style.borderColor = "#ff5555";
    setTimeout(function() { essayInput.style.borderColor = ""; }, 1200);
    return;
  }

  scoreBtn.disabled = true;
  scoreBtn.classList.add("loading");
  scoreBtn.querySelector(".btn-label").textContent = "Evaluating...";

  try {
    const t0  = Date.now();
    const res = await fetch(API_BASE + "/api/score", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        essay_id:  "web_" + t0,
        text:      text,
        prompt_id: promptId,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(function() { return { detail: res.statusText }; });
      throw new Error(err.detail || "Request failed");
    }

    const data    = await res.json();
    const latency = Date.now() - t0;
    renderResults(data, latency, promptId);

  } catch (err) {
    emptyState.classList.remove("hidden");
    results.classList.add("hidden");
    emptyState.querySelector("p").textContent = "Error: " + err.message;
    emptyState.querySelector("p").style.color = "#ff5555";
  } finally {
    scoreBtn.disabled = false;
    scoreBtn.classList.remove("loading");
    scoreBtn.querySelector(".btn-label").textContent = "Evaluate Essay";
  }
});

feedbackBtn.addEventListener("click", async function() {
  if (!currentEssayId) return;
  const ts = parseInt(teacherScore.value);
  if (!ts || ts < 1 || ts > 6) {
    teacherScore.style.borderColor = "#ff5555";
    setTimeout(function() { teacherScore.style.borderColor = ""; }, 1200);
    return;
  }
  try {
    await fetch(API_BASE + "/api/feedback", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        essay_id:         currentEssayId,
        is_validated:     1,
        teacher_score:    ts,
        teacher_comments: teacherComments.value,
      }),
    });
    feedbackBtn.textContent = "Saved!";
    feedbackBtn.style.color = "#c8f060";
    setTimeout(function() {
      feedbackBtn.textContent = "Save";
      feedbackBtn.style.color = "";
    }, 2000);
  } catch (err) {
    feedbackBtn.textContent = "Error";
    feedbackBtn.style.color = "#ff5555";
  }
});
