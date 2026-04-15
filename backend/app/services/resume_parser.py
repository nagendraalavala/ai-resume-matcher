"""Resume parsing service - extracts structured data from PDF and DOCX files."""

import re
from typing import Any

import pdfplumber
from docx import Document


def parse_resume(file_path: str, file_ext: str) -> dict[str, Any]:
    """Parse a resume file and extract structured data."""
    if file_ext == ".pdf":
        raw_text = _extract_text_from_pdf(file_path)
    elif file_ext == ".docx":
        raw_text = _extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")

    if not raw_text.strip():
        raise ValueError("Could not extract any text from the resume file.")

    structured = _extract_sections(raw_text)
    structured["raw_text"] = raw_text
    return structured


def _extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file using pdfplumber."""
    text_parts: list[str] = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def _extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX file."""
    doc = Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs if para.text.strip())


def _extract_sections(text: str) -> dict[str, Any]:
    """Extract structured sections from resume text using heuristics."""
    sections: dict[str, Any] = {
        "name": "",
        "email": "",
        "phone": "",
        "summary": "",
        "skills": [],
        "experience": [],
        "education": [],
        "certifications": [],
    }

    # Extract email
    email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
    if email_match:
        sections["email"] = email_match.group()

    # Extract phone
    phone_match = re.search(
        r"[\+]?[(]?[0-9]{1,4}[)]?[-\s./0-9]{7,15}", text
    )
    if phone_match:
        sections["phone"] = phone_match.group().strip()

    # Extract name (typically first non-empty line)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if lines:
        first_line = lines[0]
        if len(first_line) < 60 and not re.search(r"@|http|www\.", first_line):
            sections["name"] = first_line

    # Section detection patterns
    section_patterns = {
        "summary": r"(?:summary|objective|profile|about\s*me)",
        "skills": r"(?:skills|technical\s*skills|core\s*competencies|technologies|proficiencies)",
        "experience": r"(?:experience|work\s*experience|employment|professional\s*experience|work\s*history)",
        "education": r"(?:education|academic|qualifications|degrees)",
        "certifications": r"(?:certifications?|licenses?|credentials)",
    }

    current_section = None
    section_content: dict[str, list[str]] = {k: [] for k in section_patterns}

    for line in lines:
        line_lower = line.lower().strip()
        matched = False
        for section_name, pattern in section_patterns.items():
            if re.match(rf"^{pattern}\s*:?\s*$", line_lower) or re.match(
                rf"^[-=]*\s*{pattern}\s*[-=]*\s*:?\s*$", line_lower
            ):
                current_section = section_name
                matched = True
                break

        if not matched and current_section:
            section_content[current_section].append(line)

    # Process extracted sections
    if section_content["summary"]:
        sections["summary"] = " ".join(section_content["summary"][:5])

    if section_content["skills"]:
        skills_text = " ".join(section_content["skills"])
        skills = re.split(r"[,;|•·\n]", skills_text)
        sections["skills"] = [
            s.strip().strip("-").strip("•").strip()
            for s in skills
            if s.strip() and len(s.strip()) > 1
        ]

    if section_content["experience"]:
        sections["experience"] = _parse_experience_entries(
            section_content["experience"]
        )

    if section_content["education"]:
        sections["education"] = _parse_education_entries(
            section_content["education"]
        )

    if section_content["certifications"]:
        sections["certifications"] = [
            c.strip()
            for c in section_content["certifications"]
            if c.strip()
        ]

    return sections


def _parse_experience_entries(lines: list[str]) -> list[dict[str, str]]:
    """Parse experience section into structured entries."""
    entries: list[dict[str, str]] = []
    current_entry: dict[str, str] = {}
    bullets: list[str] = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect date patterns that indicate a new entry
        date_match = re.search(
            r"((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s,]*\d{4}|"
            r"\d{1,2}/\d{4}|\d{4}\s*[-–]\s*(?:present|\d{4}|current))",
            line,
            re.IGNORECASE,
        )

        is_bullet = line.startswith(("-", "•", "●", "○", "▪", "*"))

        if date_match and not is_bullet:
            if current_entry:
                current_entry["bullets"] = "\n".join(bullets)
                entries.append(current_entry)
                bullets = []
            current_entry = {"title_line": line, "bullets": ""}
        elif is_bullet:
            bullets.append(line.lstrip("-•●○▪* "))
        elif current_entry:
            if not current_entry.get("company_line"):
                current_entry["company_line"] = line
            else:
                bullets.append(line)

    if current_entry:
        current_entry["bullets"] = "\n".join(bullets)
        entries.append(current_entry)

    return entries


def _parse_education_entries(lines: list[str]) -> list[dict[str, str]]:
    """Parse education section into structured entries."""
    entries: list[dict[str, str]] = []
    current: dict[str, str] = {}

    for line in lines:
        line = line.strip()
        if not line:
            continue

        degree_match = re.search(
            r"(bachelor|master|ph\.?d|associate|b\.?s\.?|m\.?s\.?|b\.?a\.?|m\.?a\.?|mba|doctorate)",
            line,
            re.IGNORECASE,
        )

        if degree_match:
            if current:
                entries.append(current)
            current = {"degree_line": line}
        elif current:
            if "institution" not in current:
                current["institution"] = line
            else:
                current["details"] = current.get("details", "") + " " + line
        else:
            current = {"degree_line": line}

    if current:
        entries.append(current)

    return entries
