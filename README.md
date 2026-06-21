# ⚖ LexWarden — Contract Intelligence Engine

> Automated legal contract analysis using RAG, Gemini embeddings, Pinecone vector search, and MongoDB — with a full browser-based UI.

---

## What It Does

LexWarden ingests a PDF or DOCX contract, splits it into clauses, runs each clause through a RAG pipeline against a library of "golden standard" safe clauses, and uses Gemini to assess risk level (🔴 RED / 🟡 YELLOW / 🟢 GREEN) with explanations and suggested rewrites.

---

## Architecture

```
[Browser UI]
     │  POST /api/v1/analyze-contract  (multipart PDF/DOCX)
     ▼
[FastAPI Backend]
     │
     ├─ OCRService      → extract text (pypdf for digital, pytesseract for scanned)
     │                    also supports .docx via python-docx
     │
     ├─ VectorService   → Gemini text-embedding-004 → query Pinecone for nearest safe clause
     │
     ├─ LLMService      → Gemini 2.5 Flash → structured JSON risk assessment per clause
     │
     └─ MongoDB         → persist full report document
```

---

## Project Structure

```
LexWarden/
├── app/
│   ├── main.py                   # FastAPI app, CORS, rate limiting, lifespan
│   ├── config.py                 # Pydantic settings (reads .env)
│   ├── api/
│   │   └── endpoints/
│   │       ├── uploads.py        # POST /analyze-contract
│   │       └── reports.py        # GET/DELETE /reports
│   ├── db/
│   │   ├── mongo.py              # Motor async MongoDB client
│   │   └── models.py             # Pydantic models for DB documents
│   └── services/
│       ├── ocr_service.py        # PDF text extraction + OCR fallback + DOCX
│       ├── vector_service.py     # Gemini embeddings + Pinecone similarity search
│       └── llm_service.py        # Gemini 2.5 Flash clause risk assessment
├── frontend/
│   └── index.html                # Single-file browser UI (dark/light mode)
├── seed_vectors.py               # One-time script to load golden standards into Pinecone
├── requirements.txt
├── Dockerfile
├── docker-compose.yaml
├── .env.example
└── .gitignore
```

---

## Setup

### Prerequisites

- Python 3.11+
- A [Google AI Studio](https://aistudio.google.com) account → Gemini API key
- A [Pinecone](https://pinecone.io) account → API key + serverless index
- MongoDB (local or [MongoDB Atlas](https://www.mongodb.com/atlas))
- `tesseract-ocr` and `poppler-utils` (only needed for scanned PDFs)

**System dependencies (Ubuntu/Debian):**
```bash
sudo apt install tesseract-ocr poppler-utils
```

**macOS:**
```bash
brew install tesseract poppler
```

---

### Step 1 — Clone and configure

```bash
git clone https://github.com/cadylac20-coder/LexWarden.git
cd LexWarden
cp .env.example .env
```

Edit `.env`:

```env
GEMINI_API_KEY=your_google_ai_studio_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=lexwarden-safe-clauses
MONGO_URI=mongodb://localhost:27017/lexwarden
MONGO_DB_NAME=lexwarden
```

> ⚠️ **Never commit `.env` to git.** It's already in `.gitignore`.

---

### Step 2 — Install Python dependencies

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

### Step 3 — Seed the vector database

This is a **one-time step** that creates the Pinecone index and uploads 12 golden standard safe clauses covering:

| ID | Clause Type |
|----|-------------|
| std_liability_01 | Limitation of Liability |
| std_indemnity_01 | Mutual Indemnification |
| std_termination_01 | Termination for Cause |
| std_ip_01 | Intellectual Property |
| std_confidentiality_01 | Confidentiality / NDA |
| std_governing_law_01 | Governing Law + Dispute Resolution |
| std_data_privacy_01 | Data Protection / GDPR |
| std_noncompete_01 | Non-Solicitation |
| std_payment_01 | Payment Terms |
| std_warranty_01 | Warranty |
| std_force_majeure_01 | Force Majeure |
| std_auto_renewal_01 | Auto-Renewal Terms |

```bash
python seed_vectors.py
```

Expected output:
```
Creating Pinecone index: lexwarden-safe-clauses...
Seeding 12 golden standard clauses...
  ✓ std_liability_01 (liability)
  ✓ std_indemnity_01 (indemnification)
  ...
Seeding complete. 12 vectors loaded into 'lexwarden-safe-clauses'.
```

---

### Step 4 — Start the backend

```bash
uvicorn app.main:app --reload --port 8000
```

Verify it's alive:
```bash
curl http://localhost:8000/healthz
# {"status":"online","database_connected":true}
```

Interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Step 5 — Open the UI

Just open `frontend/index.html` in your browser:

```bash
# macOS
open frontend/index.html

# Linux
xdg-open frontend/index.html

# Or serve it properly (recommended, avoids CORS issues on some browsers):
cd frontend
python -m http.server 8080
# Then open http://localhost:8080
```

---

## Docker (optional)

Runs the FastAPI backend and MongoDB together:

```bash
docker-compose up --build
```

The UI is static — just open `frontend/index.html` directly. The backend will be at `http://localhost:8000`.

> **Note:** MongoDB data is persisted in a Docker volume (`mongo_data`). The `web` service waits for MongoDB to be healthy before starting.

---

## API Reference

### `POST /api/v1/analyze-contract`

Upload a contract file for analysis.

- **Body:** `multipart/form-data` with field `file` (PDF or DOCX)
- **Rate limit:** 10 requests/minute per IP

**Response:**
```json
{
  "_id": "6671abc123...",
  "filename": "vendor_agreement.pdf",
  "uploaded_at": "2025-06-15T10:30:00Z",
  "overall_status": "RISKY (RED FLAGS)",
  "clauses_analyzed": [
    {
      "scanned_clause": "Vendor shall not be liable...",
      "risk_level": "RED",
      "explanation": "This clause unilaterally removes all liability...",
      "suggested_revision": "Neither party shall be liable for...",
      "similarity_score": 0.8712
    }
  ]
}
```

### `GET /api/v1/reports`

Returns the 100 most recent reports.

### `GET /api/v1/reports/{report_id}`

Returns a single report by MongoDB ID.

### `DELETE /api/v1/reports/{report_id}`

Deletes a report.

### `GET /healthz`

Returns API + database status.

---

## UI Features

| Feature | Description |
|---------|-------------|
| **Dark / Light mode** | Toggles via the switch in the header. Preference saved to `localStorage`. |
| **Drag & drop** | Drop PDF or DOCX directly onto the upload zone. |
| **Scanner animation** | A document-sweep animation with real status messages while the pipeline runs. |
| **Results sorted by risk** | RED clauses always appear first. |
| **Expandable clause cards** | Click any card to expand and see raw clause, AI analysis, and suggested revision. |
| **Similarity score chips** | Shows cosine similarity % vs. the matched safe baseline (only shown when a match was found). |
| **History tab** | Last 20 analyses stored in `localStorage`. Click any item to reload that report. |
| **API status indicator** | Header shows whether the FastAPI backend is reachable. |

---

## Risk Level Guide

| Level | Meaning |
|-------|---------|
| 🔴 **RED** | Severe risk — uncapped liability, removed protections, unilateral rights, predatory terms |
| 🟡 **YELLOW** | Caution — asymmetric language, vague scope, non-standard terms, missing protections |
| 🟢 **GREEN** | Compliant — aligns with or improves upon the safe clause baseline |

---

## Known Limitations

- **Scanned PDFs** require `tesseract-ocr` and `poppler-utils` installed on the host (or Docker handles it).
- **Very large contracts** (100+ pages) may take 30–90 seconds depending on Gemini API latency.
- The UI stores history in `localStorage` — clearing browser data will remove it. For persistent history, use the `/reports` API.
- Rate limit is 10 analyses per minute per IP. For heavier use, adjust in `uploads.py`.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + Uvicorn |
| AI (embeddings) | Gemini `text-embedding-004` (768-dim) |
| AI (analysis) | Gemini `2.5 Flash` with structured JSON output |
| Vector DB | Pinecone serverless (cosine similarity) |
| Database | MongoDB (async via Motor) |
| OCR | pytesseract + pdf2image |
| DOCX parsing | python-docx |
| Rate limiting | slowapi |
| Frontend | Vanilla HTML/CSS/JS (no frameworks) |

