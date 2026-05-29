# Ascendic Workflow 🤖

An advanced **Retrieval-Augmented Generation (RAG)** pipeline designed to answer customer queries for merchants about their products — built specifically to eliminate hallucinations that plague standard RAG systems.

---

## 💡 Why I Built This

My first RAG chatbot kept giving wrong answers. Instead of accepting it, I analysed *why* hallucinations happen in RAG systems and rebuilt the entire pipeline from scratch with a multi-stage architecture that brings hallucinations down to near zero.

---

## 🧠 Architecture

Most RAG systems just retrieve and respond. **Ascendic Workflow uses a 6-stage intelligent pipeline:**

```
User Query
    │
    ▼
┌─────────────────────────┐
│   1. Intent Analysis     │  ── Understands what the user really means
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│   2. Query Rewriting     │  ── Rewrites query based on conversation history
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│   3. Retrieval           │  ── Fetches top 9 relevant results from Supabase
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│   4. Cross-Encoder       │  ── Reranks top 9 → extracts best 3 results
│      Reranking           │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│   5. Context Compression │  ── Removes noise, keeps only what matters
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│   6. Response Generation │  ── Clean, grounded, accurate answer via Groq
└─────────────────────────┘
    │
    ▼
Final Answer → Near-Zero Hallucinations ✅
```

---

## 🚀 Why This Architecture?

Standard RAG fails because of 3 core problems. This pipeline solves all of them:

| Problem | Solution |
|---|---|
| Vague or poorly worded queries | **Query Rewriting** based on conversation history |
| Wrong documents retrieved | **Cross-Encoder Reranking** (Top 9 → Top 3) |
| Too much noisy context sent to LLM | **Context Compression** before generation |
| System doesn't understand user intent | **Intent Analysis** at the very first stage |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| LLM | [Groq](https://groq.com) (fast inference) |
| Database | [Supabase](https://supabase.com) (vector + relational) |
| Reranking | Cross-Encoder model |
| Backend | Python / FastAPI |
| RAG Orchestration | Custom pipeline |

---

## 💼 Use Case

Built for **merchants** who need an intelligent assistant that can:
- Answer customer questions about their products accurately
- Handle vague or conversational queries using history-aware rewriting
- Retrieve and rank large product catalogs to find the most relevant answers
- Deliver responses with near-zero hallucinations

---

## ⚙️ Getting Started

### Prerequisites
- Python 3.11
- Groq API key
- Supabase project (URL + API key)

### Installation

```bash
git clone https://github.com/yourusername/ascendic-workflow.git
cd ascendic-workflow
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_api_key
```

### Run

```bash
uvicorn main:app --reload
```

---

## 📂 Project Structure

```
ascendic-workflow/
├── main.py                  # FastAPI entry point
├── pipeline/
│   ├── intent_analysis.py   # Stage 1: Intent detection
│   ├── query_rewriter.py    # Stage 2: History-aware query rewriting
│   ├── retriever.py         # Stage 3: Supabase vector retrieval
│   ├── reranker.py          # Stage 4: Cross-encoder reranking
│   ├── compressor.py        # Stage 5: Context compression
│   └── responder.py         # Stage 6: Response generation
├── models/
├── requirements.txt
└── .env.example
```

---

## 🔮 Roadmap

- [ ] Tool calling integration (agent can take real actions)
- [ ] Multi-merchant support
- [ ] Conversation memory
- [ ] Analytics dashboard for merchants
- [ ] Evaluation metrics (faithfulness, relevancy scores)

---

## 👤 Author

Built with 🔥 by [Amal Gafoor](https://github.com/amal-gafoor/agentic-workflow)

