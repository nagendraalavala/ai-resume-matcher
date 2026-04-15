"""Matching engine - compares resume against job description using AI and keyword analysis."""

import os
import json
import re
import math
from typing import Any
from collections import Counter
from openai import AsyncOpenAI


def _get_client() -> AsyncOpenAI:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    return AsyncOpenAI(api_key=api_key)


async def compute_match(resume_data: dict[str, Any], job_description: str) -> dict[str, Any]:
    """Compute match score between resume and job description."""
    resume_text = resume_data.get("raw_text", "")

    # Run keyword-based analysis
    keyword_result = _keyword_analysis(resume_text, job_description)

    # Run AI-powered semantic analysis
    ai_result = await _ai_analysis(resume_data, job_description)

    # Combine scores: 40% keyword, 60% AI
    keyword_score = keyword_result["keyword_score"]
    ai_score = ai_result.get("match_score", 50)

    combined_score = int(0.4 * keyword_score + 0.6 * ai_score)
    combined_score = max(0, min(100, combined_score))

    return {
        "match_score": combined_score,
        "keyword_score": keyword_score,
        "ai_score": ai_score,
        "missing_skills": ai_result.get("missing_skills", []),
        "matched_skills": ai_result.get("matched_skills", []),
        "weak_areas": ai_result.get("weak_areas", []),
        "suggestions": ai_result.get("suggestions", []),
        "keyword_overlap": keyword_result["overlap_keywords"],
        "missing_keywords": keyword_result["missing_keywords"],
    }


def _keyword_analysis(resume_text: str, job_description: str) -> dict[str, Any]:
    """Perform keyword overlap and lightweight cosine similarity matching."""
    job_words = set(_extract_keywords(job_description))
    resume_words = set(_extract_keywords(resume_text))

    if not job_words:
        return {
            "keyword_score": 50,
            "overlap_keywords": [],
            "missing_keywords": [],
        }

    overlap = job_words & resume_words
    missing = job_words - resume_words

    overlap_score = int((len(overlap) / len(job_words)) * 100) if job_words else 50

    # Lightweight cosine similarity using term frequency
    cosine_score = _cosine_similarity_simple(resume_text, job_description)

    # Blend overlap and cosine similarity
    score = int(0.5 * overlap_score + 0.5 * cosine_score)

    return {
        "keyword_score": max(0, min(100, score)),
        "overlap_keywords": sorted(list(overlap))[:30],
        "missing_keywords": sorted(list(missing))[:30],
    }


def _cosine_similarity_simple(text_a: str, text_b: str) -> float:
    """Compute cosine similarity using simple term frequency vectors."""
    words_a = _extract_keywords(text_a)
    words_b = _extract_keywords(text_b)

    counter_a = Counter(words_a)
    counter_b = Counter(words_b)

    all_words = set(counter_a.keys()) | set(counter_b.keys())
    if not all_words:
        return 50.0

    dot_product = sum(counter_a.get(w, 0) * counter_b.get(w, 0) for w in all_words)
    mag_a = math.sqrt(sum(v * v for v in counter_a.values()))
    mag_b = math.sqrt(sum(v * v for v in counter_b.values()))

    if mag_a == 0 or mag_b == 0:
        return 50.0

    return (dot_product / (mag_a * mag_b)) * 100


def _extract_keywords(text: str) -> list[str]:
    """Extract meaningful keywords from text."""
    text = text.lower()
    # Remove special characters but keep meaningful tech terms
    text = re.sub(r"[^a-z0-9+#./\s-]", " ", text)
    words = text.split()

    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "shall", "can", "need", "must",
        "this", "that", "these", "those", "i", "you", "he", "she", "it", "we",
        "they", "me", "him", "her", "us", "them", "my", "your", "his", "its",
        "our", "their", "what", "which", "who", "whom", "when", "where", "why",
        "how", "all", "each", "every", "both", "few", "more", "most", "other",
        "some", "such", "no", "not", "only", "own", "same", "so", "than",
        "too", "very", "just", "about", "above", "after", "again", "also",
        "as", "because", "before", "between", "during", "if", "into", "over",
        "through", "under", "until", "up", "while", "able", "work", "working",
        "experience", "team", "role", "including", "using", "required",
        "requirements", "responsibilities", "years", "year", "strong",
        "preferred", "knowledge", "ability", "understanding", "etc",
    }

    keywords = [w for w in words if w not in stop_words and len(w) > 1]
    return keywords


async def _ai_analysis(resume_data: dict[str, Any], job_description: str) -> dict[str, Any]:
    """Use OpenAI to perform semantic analysis."""
    client = _get_client()

    resume_summary = _build_resume_summary(resume_data)

    prompt = f"""You are an expert resume analyst and ATS (Applicant Tracking System) specialist.

Analyze the following resume against the job description and provide a detailed match assessment.

RESUME:
{resume_summary}

JOB DESCRIPTION:
{job_description[:4000]}

Provide your analysis as a JSON object with these fields:
- "match_score": integer 0-100 representing overall match percentage
- "matched_skills": list of skills from the resume that match the job requirements
- "missing_skills": list of important skills from the job description not found in the resume
- "weak_areas": list of areas where the resume is weak relative to the job (max 5)
- "suggestions": list of specific actionable suggestions to improve the resume (max 5)

Be thorough but realistic in your scoring. A perfect match is rare.
Return ONLY the JSON object, no other text."""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000,
        )

        content = response.choices[0].message.content or "{}"
        # Strip markdown code blocks if present
        content = content.strip()
        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?\s*", "", content)
            content = re.sub(r"\s*```$", "", content)

        return json.loads(content)
    except Exception as e:
        return {
            "match_score": 50,
            "matched_skills": [],
            "missing_skills": [],
            "weak_areas": [f"AI analysis error: {str(e)}"],
            "suggestions": ["Please try again or check your API key"],
        }


def _build_resume_summary(resume_data: dict[str, Any]) -> str:
    """Build a concise summary of resume data for the AI prompt."""
    parts = []

    if resume_data.get("name"):
        parts.append(f"Name: {resume_data['name']}")

    if resume_data.get("summary"):
        parts.append(f"Summary: {resume_data['summary']}")

    if resume_data.get("skills"):
        parts.append(f"Skills: {', '.join(resume_data['skills'][:50])}")

    if resume_data.get("experience"):
        parts.append("Experience:")
        for exp in resume_data["experience"][:5]:
            if isinstance(exp, dict):
                parts.append(f"  - {exp.get('title_line', '')}")
                if exp.get("bullets"):
                    parts.append(f"    {exp['bullets'][:300]}")
            else:
                parts.append(f"  - {str(exp)[:200]}")

    if resume_data.get("education"):
        parts.append("Education:")
        for edu in resume_data["education"][:3]:
            if isinstance(edu, dict):
                parts.append(f"  - {edu.get('degree_line', '')}")
            else:
                parts.append(f"  - {str(edu)[:200]}")

    summary = "\n".join(parts)

    # If structured extraction was minimal, use raw text
    if len(summary) < 100 and resume_data.get("raw_text"):
        return resume_data["raw_text"][:4000]

    return summary[:4000]
