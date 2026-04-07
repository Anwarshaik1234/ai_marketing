# AI Marketing Engine - Setup Guide

## Prerequisites
- Python 3.10+
- Node.js 20.x or higher
- npm 10.x or higher

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Install dependencies
python -m pip install -r requirements.txt

# Create .env file with your OpenAI API key
# Edit .env and add: OPENAI_API_KEY=sk-proj-your-key-here
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install --legacy-peer-deps

# Create .env.local (already created with defaults)
```

### 3. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## Access the Application

- **Frontend**: http://localhost:3000
- **Backend Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs
- **API ReDoc**: http://localhost:8000/redoc

## Environment Variables

### Backend (.env)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | - | Your OpenAI API key (get from https://platform.openai.com/api-keys) |
| `DATABASE_URL` | ❌ No | `sqlite+aiosqlite:///./marketing.db` | Database connection string |
| `OLLAMA_BASE_URL` | ❌ No | `http://localhost:11434` | Ollama server URL (for local LLM) |
| `OLLAMA_MODEL` | ❌ No | `llama3.2` | Ollama model name |
| `OLLAMA_ONLY` | ❌ No | `false` | Use only Ollama (no OpenAI) |

### Frontend (.env.local)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | ❌ No | `http://localhost:8000` | Backend API URL |

## Getting OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign up or login with your OpenAI account
3. Click "Create new secret key"
4. Copy the key (you'll only see it once)
5. Add it to `backend/.env`: `OPENAI_API_KEY=sk-proj-your-key-here`

## Using Ollama (Local LLM Alternative)

If you don't have an OpenAI key, you can use Ollama for local inference:

1. Install Ollama: https://ollama.ai
2. Run Ollama: `ollama serve`
3. In `backend/.env`, set:
   ```
   OLLAMA_ONLY=true
   OPENAI_API_KEY=
   ```
4. Restart the backend

## Troubleshooting

### Backend won't start - "ModuleNotFoundError"
- Make sure you installed dependencies: `pip install -r requirements.txt`
- Check PYTHONPATH is set correctly

### Frontend won't start - "next command not found"
- Make sure you installed dependencies: `npm install --legacy-peer-deps`
- Make sure you're in the `frontend` directory

### API returns 401/auth error
- Check your `OPENAI_API_KEY` is set correctly in `backend/.env`
- Keys should start with `sk-proj-`

### Frontend can't reach backend
- Make sure backend is running on http://localhost:8000
- Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
- Check CORS settings if deploying to different domain

### Database errors
- Delete `marketing.db` to reset database
- Tables will auto-create on next run

## Project Structure

```
ai-marketing-engine/
├── backend/
│   ├── app/
│   │   ├── routers/          # API endpoints (brands, campaigns, content, etc.)
│   │   ├── services/         # Business logic (LLM calls, analysis, etc.)
│   │   ├── models.py         # Database models
│   │   ├── schemas.py        # Pydantic request/response schemas
│   │   ├── database.py       # Database setup
│   │   ├── config.py         # Configuration/environment
│   │   └── main.py           # FastAPI app entry point
│   ├── requirements.txt       # Python dependencies
│   └── .env                  # Environment variables (create this)
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx        # Root layout
│   │   ├── page.tsx          # Home page
│   │   ├── brand/page.tsx    # Brand setup
│   │   ├── campaign/page.tsx # Campaign creation
│   │   ├── hub/page.tsx      # Content generation hub
│   │   ├── repurpose/page.tsx# Asset repurposing
│   │   ├── ads/page.tsx      # Ad copy generator
│   │   ├── sentiment/page.tsx# Sentiment analysis
│   │   └── calendar/page.tsx # Publishing calendar
│   ├── components/           # React components
│   ├── lib/api.ts            # API client
│   ├── package.json          # Dependencies
│   └── .env.local            # Environment variables (create this)
│
└── README.md                 # Project documentation
```

## Features

### 1. Brand Context (Setup)
- Define brand name, industry, audience
- Set brand tone and voice (up to 3 tones)
- Configure keywords to include/avoid

### 2. Campaign Creation
- Create marketing campaigns linked to brands
- Set goals (Awareness, Lead Gen, Retention, Product Launch)
- Select platforms (LinkedIn, Instagram, Email, Twitter, Google Ads)
- Validate platform fit with AI

### 3. Content Generation (Hub)
- Generate multi-channel content from a single brief
- AI creates platform-optimized versions
- Outputs: LinkedIn posts, Instagram captions, emails, blog outlines, video scripts, Google Ads, SEO meta

### 4. Asset Repurposing
- Upload long-form content (blog, podcast, webinar transcript)
- AI extracts key insights and quotable moments
- Generate channel-specific content from the source

### 5. Ad Copy Lab
- Generate 5 ad variants with different tones
- AI recommends best variant
- Export as CSV for media buyer

### 6. Sentiment Analysis
- Upload customer feedback CSV
- AI analyzes themes, emotions, and trends
- Visual wordcloud of top terms

### 7. Publishing Calendar
- Drag-drop calendar scheduling
- AI suggests optimal posting times
- Detect content gaps by platform
- Export as CSV or print-friendly HTML

### 8. Bonus Tools
- **Competitor Counter**: Analyze competitor post and generate counter positioning
- **Tone Score**: Rate content against brand tone guidelines

## API Endpoints

### Brands
- `POST /brands` - Create brand
- `GET /brands` - List brands
- `GET /brands/{id}` - Get brand details

### Campaigns
- `POST /campaigns` - Create campaign
- `GET /campaigns` - List campaigns
- `GET /campaigns/{id}` - Get campaign details

### Content
- `POST /content/generate` - Generate content from brief
- `POST /content/regenerate` - Regenerate single piece
- `GET /content/campaign/{id}` - Get campaign content

### Repurpose
- `POST /repurpose/analyze` - Analyze source document
- `POST /repurpose/run` - Generate repurposed content
- `GET /repurpose/jobs` - List repurpose jobs

### Ads
- `POST /ads/generate` - Generate ad variants
- `PATCH /ads/experiment/{id}/variant` - Update variant status
- `GET /ads/experiment/{id}` - Get experiment
- `GET /ads/experiment/{id}/export.csv` - Export as CSV

### Sentiment
- `POST /sentiment/upload` - Upload and analyze CSV
- `GET /sentiment/reports` - List sentiment reports
- `GET /sentiment/reports/{id}` - Get report details

### Calendar
- `POST /calendar/move` - Schedule content piece
- `GET /calendar/gaps/{id}` - Find scheduling gaps
- `POST /calendar/suggest/{id}` - Get AI schedule suggestions
- `GET /calendar/export` - Export calendar

### Bonus
- `POST /bonus/competitor` - Analyze competitor post
- `POST /bonus/tone-score` - Score content tone

## Next Steps

1. ✅ Set up environment variables
2. ✅ Install dependencies
3. ✅ Start backend and frontend
4. Create a brand profile
5. Create a campaign
6. Generate content
7. Schedule content in calendar
8. Export and use

Enjoy! 🚀
