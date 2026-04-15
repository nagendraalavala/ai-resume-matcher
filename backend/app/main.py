import os
import shutil
import tempfile
import json
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from typing import Optional

load_dotenv()

from app.services.resume_parser import parse_resume
from app.services.job_scraper import scrape_job_url
from app.services.matching_engine import compute_match
from app.services.optimizer import optimize_resume
from app.services.pdf_generator import generate_pdf

app = FastAPI(title="AI Resume Matcher & Optimizer")

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

UPLOAD_DIR = tempfile.mkdtemp()


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze(
    resume: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    job_url: Optional[str] = Form(None),
    target_percentage: int = Form(85),
):
    """
    Analyze a resume against a job description.
    Returns match score, missing skills, suggestions, and optimized resume.
    """
    if not job_description and not job_url:
        raise HTTPException(
            status_code=400,
            detail="Either job_description or job_url must be provided",
        )

    content = await resume.read()
    filename = resume.filename or "resume.pdf"

    file_ext = os.path.splitext(filename)[1].lower()
    if file_ext not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=400, detail="Only PDF and DOCX files are supported"
        )

    temp_path = os.path.join(UPLOAD_DIR, f"upload_{os.urandom(8).hex()}{file_ext}")
    with open(temp_path, "wb") as f:
        f.write(content)

    try:
        resume_data = parse_resume(temp_path, file_ext)

        if job_url and not job_description:
            job_description = scrape_job_url(job_url)
            if not job_description:
                raise HTTPException(
                    status_code=400,
                    detail="Could not extract job description from the provided URL. Please paste the job description text instead.",
                )

        match_result = await compute_match(resume_data, job_description)

        optimized = await optimize_resume(
            resume_data, job_description, match_result, target_percentage
        )

        return {
            "original_resume": resume_data,
            "match_result": match_result,
            "optimized_resume": optimized["optimized_resume"],
            "optimized_match_score": optimized["estimated_new_score"],
            "changes_summary": optimized["changes_summary"],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def _cleanup_temp_pdf(path: str) -> None:
    """Remove temp PDF file and its directory after response is sent."""
    dir_path = os.path.dirname(path)
    if os.path.exists(path):
        os.remove(path)
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path, ignore_errors=True)


@app.post("/api/download-pdf")
async def download_pdf(
    resume_data: str = Form(...),
):
    """Generate and download optimized resume as PDF."""
    try:
        data = json.loads(resume_data)
        pdf_path = generate_pdf(data)
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename="optimized_resume.pdf",
            background=BackgroundTask(_cleanup_temp_pdf, pdf_path),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
