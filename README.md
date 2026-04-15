# AI Resume Matcher & Optimizer

A production-ready web application that helps users match their resumes against job descriptions and automatically optimize them for better ATS compatibility.

## Features

- **Resume Upload**: Upload PDF or DOCX resumes
- **Job Description Input**: Paste text or provide a job URL (LinkedIn, Dice, Indeed, etc.)
- **AI-Powered Matching**: Get a % match score using semantic similarity and keyword analysis
- **Resume Optimization**: Automatically optimize your resume to reach a target match percentage
- **PDF Download**: Download the optimized resume as a professionally formatted PDF
- **Score Visualization**: Interactive charts showing match breakdown

## Tech Stack

### Frontend
- React 18 + TypeScript
- Vite build tool
- TailwindCSS for styling
- Recharts for data visualization
- Axios for API communication

### Backend
- FastAPI (Python)
- OpenAI GPT-4o-mini for AI analysis and rewriting
- OpenAI Embeddings for semantic similarity
- scikit-learn for TF-IDF keyword matching
- pdfplumber / python-docx for document parsing
- WeasyPrint for PDF generation
- BeautifulSoup for web scraping

## Setup

### Prerequisites
- Node.js 18+
- Python 3.12+
- Poetry (Python package manager)
- OpenAI API key

### Backend Setup

```bash
cd backend
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
poetry install
poetry run fastapi dev app/main.py
```

The backend will run at http://localhost:8000

### Frontend Setup

```bash
cd frontend
cp .env.example .env
# Edit .env if backend URL differs
npm install
npm run dev
```

The frontend will run at http://localhost:5173

## Environment Variables

### Backend (.env)
```
OPENAI_API_KEY=your_openai_api_key_here
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

## API Endpoints

### POST /api/analyze
Analyze a resume against a job description.

**Input** (multipart/form-data):
- `resume` - PDF or DOCX file
- `job_description` - Job description text (optional if job_url provided)
- `job_url` - Job posting URL (optional if job_description provided)
- `target_percentage` - Target match score (70-95, default 85)

**Output**:
- `original_resume` - Parsed resume data
- `match_result` - Match score, missing skills, suggestions
- `optimized_resume` - AI-optimized resume data
- `optimized_match_score` - Estimated new score
- `changes_summary` - List of changes made

### POST /api/download-pdf
Generate a PDF from optimized resume data.

**Input** (form-data):
- `resume_data` - JSON string of resume data

**Output**: PDF file download

## Architecture

```
ai-resume-matcher/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app with routes
│   │   └── services/
│   │       ├── resume_parser.py    # PDF/DOCX text extraction
│   │       ├── job_scraper.py      # URL scraping for job descriptions
│   │       ├── matching_engine.py  # AI + keyword matching
│   │       ├── optimizer.py        # GPT-powered resume rewriting
│   │       └── pdf_generator.py    # WeasyPrint PDF generation
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── App.tsx                 # Main app with routing
│   │   ├── types.ts                # TypeScript interfaces
│   │   └── components/
│   │       ├── UploadPage.tsx      # Resume upload & job input
│   │       └── ResultsDashboard.tsx # Results, charts, download
│   └── package.json
└── README.md
```

## Quality Notes

- Resume optimization maintains truthfulness - no fabricated experience
- Natural, human-like tone in rewritten resumes
- ATS-friendly formatting in generated PDFs
- Graceful error handling for scraping failures
- Loading states for AI processing steps
