# AI Marketing Intelligence & Content Engine

A single workspace for campaign planning, multi-format content generation, repurposing, ad testing, audience sentiment, and a publish calendar — with **brand context** applied to every AI output.

## Project overview

Teams define **brand tone**, **guardrails**, and **campaign goals** once. The app validates setup against platform norms, generates coordinated assets (LinkedIn, Instagram, X, video scripts, email, blog outline, Google Ads, SEO meta), repurposes long-form sources with attribution, produces A/B ad variants with labels and export, analyzes review/comment CSVs for themes and sentiment, and organizes everything on a drag-and-drop calendar with gap detection and export.

## Tech stack

| Layer | Choice |
|-------|--------|
| Backend | Python 3.11+, **FastAPI**, SQLAlchemy 2, SQLite |
| Frontend | **Next.js 14** (App Router), **Tailwind CSS**, **shadcn/ui** patterns |
| AI | **OpenAI** (`OPENAI_API_KEY`), **Groq** free tier (`GROQ_API_KEY`), or local **Ollama** — see `backend/.env.example` and `LLM_PROVIDER` |
| Calendar | `@hello-pangea/dnd` drag-and-drop on a week grid |

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- A Groq, OpenAI, or other OpenAI-compatible API key, **or** a running Ollama instance (see `.env.example`)

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
copy .env.example .env    # edit OPENAI_API_KEY
uvicorn app.main:app --reload --port 8000
```

API docs: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
copy .env.local.example .env.local   # set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

App: `http://localhost:3000`

## Feature list (modules)

1. **Brand & campaign setup** — Brand name, industry, audience (age, interests, pain points), **exactly 3 tone picks** from the required list, keywords include/avoid, campaign name, goal, duration, platforms. AI validates tone vs platform and suggests adjustments.
2. **Content generation hub** — One brief → LinkedIn (3 variants), Instagram + hashtags (emoji / no-emoji), 5 X posts, 2 video scripts (30s/60s), email section, blog outline, 3 Google Ad combos, SEO title + description. Per-piece **regenerate** and **refinement** (“make more aggressive”, etc.).
3. **Repurposing** — Paste blog/podcast/webinar text or **upload a `.txt` transcript**; attribution line on outputs; **coverage map** (section usage); insights, quotes, argument summary; then same formats as module 2 from source only.
4. **Ad copy & A/B** — Product, audience, platform, goal → 5 variants with tone labels; side-by-side; status Testing/Winner/Rejected; AI pick + rationale; CSV export.
5. **Sentiment intelligence** — Upload CSV of text; sentiment %, themes, emotional highlights, VoC paragraph, **word cloud** data, campaign angles.
6. **Content calendar** — Drag items to dates; **filter by platform**; gap highlights; **per-piece status** (Draft / Ready / Scheduled / Published); AI schedule suggestion; PDF/CSV export.

## Known limitations

- **SQLite** is fine for demos; production would use Postgres and background jobs for long LLM calls.
- **PDF export** uses print-friendly HTML (browser print to PDF); dedicated PDF layout is a follow-up.
- **Competitor counter-analysis** and **tone consistency score** are implemented as **bonus** endpoints/UI when API keys are set; quality depends on model.
- Large uploads and very long transcripts may hit token limits; chunking is partially done in repurposing only.

## Screenshots / GIFs

Add your own after running the app:

1. Dashboard → Brand & Campaign wizard  
2. Content Hub with generated blocks and refinement  
3. Repurpose upload + coverage map  
4. Ad lab comparison + CSV export  
5. Sentiment dashboard + word cloud  
6. Calendar drag-and-drop + gap alert  

*(Replace this section with embedded images or links before submission.)*

## Environment variables

See `backend/.env.example` and `frontend/.env.local.example`.

## Assignment rubric (self-check)

| Requirement | Where it lives |
|-------------|----------------|
| Brand + audience + 3 tones + guardrails | `Brand` page, `brand_context.py` |
| Campaign goal, dates, platforms + AI validation | `Campaign` page, `campaign` router + `validate_campaign_platforms` |
| Multi-format hub + regenerate + refinement | `Content hub`, `/content/generate`, `/content/regenerate` |
| Repurpose + coverage + attribution | `Repurpose` page, `repurpose` service |
| 5 ad variants, labels, status, export, AI notes | `Ad lab`, `/ads/*` |
| Sentiment CSV, themes, VoC, word cloud, trend | `Sentiment` page, `sentiment` service |
| Calendar DnD, filter, gaps, status, export, AI schedule | `Calendar` page, `/calendar/*` |
| Bonus: competitor + tone score | `Bonus` page, `/bonus/*` |

## Git & submission checklist

1. Initialize the repo **inside** `ai-marketing-engine` (not your whole user profile).  
2. Make **multiple commits** (e.g. `chore: scaffold`, `feat: brand module`, `feat: content hub`, `fix: calendar DnD`) — avoid a single dump commit.  
3. Add **screenshots or GIFs** under `docs/` and link them in this README.  
4. Record a **≤5 min** demo (YouTube unlisted or Drive): problem, full UI, ≥3 AI scenarios, one prompt-design choice, one limitation + future fix.  
5. Submit the form with repo URL, video URL, and your **100-word reflection**.

### Prompt design (for your video)

Brand context is injected **once** in the system prefix (`app/services/brand_context.py`) so every module shares the same tone and guardrail rules. JSON response shapes are described explicitly in `content_generation.py` and `llm.py` so outputs stay structured for UI, regeneration, and exports.

## License

MIT — assignment / portfolio use.
