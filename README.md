# 🎙️ Multi-Agent Financial Assistant

A production-ready, voice-powered financial assistant that delivers spoken market briefs using multi-agent orchestration, Retrieval-Augmented Generation (RAG), and real-time data analysis.

---

## 🚀 Features

- **🎤 Voice I/O**: Ask financial questions via browser microphone.
- **📊 Real-Time Analysis**: Summarizes risk exposure, earnings surprises, and market events.
- **🧠 Multi-Agent Architecture**: Decoupled agents for scraping, retrieval, reasoning, and voice synthesis.
- **🧾 RAG Pipeline**: Retrieves real-time earnings/risk data from multiple APIs and web sources.
- **📈 Quantitative Reasoning**: Supports exposure % breakdowns and sentiment-based interpretations.
- **📺 Streamlit UI**: Low-latency interface for spoken and typed interaction.

---

## 🧠 Architecture Overview

```
                ┌────────────────────┐
                │ Streamlit Frontend │
                └────────┬───────────┘
                         │
            ┌────────────▼────────────┐
            │   FastAPI Orchestrator  │
            └────────────┬────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
 ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
 │  RAG Agent  │  │ Voice Agent │  │ NLP Agent   │
 │ (LLM + DB)  │  │ TTS + STT   │  │ Fin. Parsing│
 └─────────────┘  └─────────────┘  └─────────────┘
        │                │                │
 ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
 │  Web Agent  │  │ API Agent   │  │ Analysis    │
 │  (Scraping) │  │ (News/Stock)│  │ Engine      │
 └─────────────┘  └─────────────┘  └─────────────┘
```

---

## 🧰 Tech Stack & Toolkits

| Agent Type        | Toolkits Used                                                                 |
|-------------------|-------------------------------------------------------------------------------|
| **Web Agent**     | `Selenium`, `BeautifulSoup`, `Playwright`                                     |
| **Retrieval Agent**| `FAISS`, `Chroma`, `LangChain`, `OpenAI Embeddings`                          |
| **Language Agent**| `GPT-4`, `transformers`, `LangChain`, `Prompt Templates`                      |
| **Voice Agent**   | `SpeechRecognition`, `pyttsx3`, `st_audiorec`, `gTTS`                         |
| **Frontend**      | `Streamlit`, `st_audiorec`, `Matplotlib`, `Plotly`, `Altair`                  |
| **Backend/API**   | `FastAPI`, `Uvicorn`, `pydantic`                                               |
| **CI/CD**         | `GitHub Actions`, `Black`, `flake8`, `pytest`                                 |

---


## 🛠️ Setup Instructions

### 1. Clone and Install
```bash
git clone https://github.com/your-org/finance-voice-agent.git
cd finance-voice-agent
pip install -r requirements.txt
```

### 2. Launch Backend (FastAPI)
```bash
uvicorn backend.orchestrator.main:app --host 0.0.0.0 --port 8000
```

### 3. Run Streamlit Frontend
```bash
cd streamlit_app
streamlit run app.py
```

### 4. Deploy on Render

Use `uvicorn` in the Render `start command`:
```bash
uvicorn backend.orchestrator.main:app --host 0.0.0.0 --port 8000
```

---

## 🧪 Testing

```bash
pytest tests/
black . --check
flake8 .
```

---

## 🧠 Prompt Engineering & RAG

- **System prompt**: Guides the LLM to structure briefs concisely (e.g., “Summarize risk exposure, then earnings surprises...”)
- **Chunking strategy**: 500-token overlapping windows
- **Similarity Search**: FAISS with cosine distance
- **Sources**: Alpha Vantage, Yahoo Finance, Reuters

---

## 🧑‍🔬 Evaluation Criteria Mapping

| Criteria             | Evidence                                                                      |
|----------------------|--------------------------------------------------------------------------------|
| Technical Depth       | Multi-agent orchestration, RAG pipeline, sentiment & risk analysis            |
| Framework Breadth     | ≥2 toolkits per agent type: `LangChain`, `Selenium`, `TTS`, `Chroma`, etc.    |
| Code Quality          | Modular design, test suite, CI-ready                                          |
| Documentation         | Clear setup, agent explanation, AI-tool use transparency                      |
| UX & Performance      | Fast Streamlit UI, live transcription, voice synthesis, error handling        |

---

## 🔍 AI Tool Assistance Disclosure

- **Code generation**: Initial agent scaffolding, RAG configs, and response formatting aided by GPT-4.
- **Manual refinement**: All prompts, agent logic, and architecture were manually tuned and tested.
- **Voice tuning**: TTS/STT behavior iteratively improved based on real feedback.

---

## 📢 Demo Query Examples

- “What’s our risk exposure in Asia tech stocks today?”
- “Summarize any earnings surprises from last night.”
- “Which sectors are driving today's US market performance?”

---

