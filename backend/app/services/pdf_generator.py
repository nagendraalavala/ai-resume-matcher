"""PDF generator - creates professionally formatted resume PDFs using fpdf2."""

import os
import tempfile
from typing import Any
from fpdf import FPDF


class ResumePDF(FPDF):
    """Custom PDF class for resume generation."""

    def header(self):
        pass

    def footer(self):
        pass


def generate_pdf(resume_data: dict[str, Any]) -> str:
    """Generate a clean professional PDF from resume data."""
    pdf = ResumePDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(15, 15, 15)
    pdf.add_page()

    name = resume_data.get("name", "Candidate")
    email = resume_data.get("email", "")
    phone = resume_data.get("phone", "")
    summary = resume_data.get("summary", "")
    skills = resume_data.get("skills", [])
    experience = resume_data.get("experience", [])
    education = resume_data.get("education", [])
    certifications = resume_data.get("certifications", [])

    # Name header
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(30, 58, 95)
    pdf.cell(0, 10, _clean_text(name), new_x="LMARGIN", new_y="NEXT", align="C")

    # Contact info
    contact_parts = [p for p in [email, phone] if p]
    if contact_parts:
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, _clean_text(" | ".join(contact_parts)), new_x="LMARGIN", new_y="NEXT", align="C")

    # Blue divider line
    pdf.set_draw_color(37, 99, 235)
    pdf.set_line_width(0.5)
    pdf.line(15, pdf.get_y() + 3, 195, pdf.get_y() + 3)
    pdf.ln(8)

    # Professional Summary
    if summary:
        _add_section_header(pdf, "PROFESSIONAL SUMMARY")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(0, 5, _clean_text(summary))
        pdf.ln(3)

    # Skills
    if skills:
        _add_section_header(pdf, "SKILLS")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(40, 40, 40)
        skill_list = [str(s) for s in skills if s]
        pdf.multi_cell(0, 5, _clean_text(", ".join(skill_list)))
        pdf.ln(3)

    # Experience
    if experience:
        _add_section_header(pdf, "EXPERIENCE")
        for exp in experience:
            if isinstance(exp, dict):
                title = exp.get("title", exp.get("title_line", ""))
                company = exp.get("company", exp.get("company_line", ""))
                dates = exp.get("dates", "")
                bullets = exp.get("bullets", [])

                if title:
                    pdf.set_font("Helvetica", "B", 10)
                    pdf.set_text_color(30, 30, 30)
                    pdf.cell(0, 5, _clean_text(title), new_x="LMARGIN", new_y="NEXT")

                if company or dates:
                    pdf.set_font("Helvetica", "I", 9)
                    pdf.set_text_color(100, 100, 100)
                    company_line = company or ""
                    if dates:
                        company_line += f" | {dates}" if company_line else dates
                    pdf.cell(0, 5, _clean_text(company_line), new_x="LMARGIN", new_y="NEXT")

                if bullets:
                    pdf.set_font("Helvetica", "", 9)
                    pdf.set_text_color(40, 40, 40)
                    bullet_list = bullets if isinstance(bullets, list) else str(bullets).split("\n")
                    for bullet in bullet_list:
                        bullet = str(bullet).strip()
                        if bullet:
                            pdf.set_x(pdf.l_margin)
                            pdf.multi_cell(0, 4.5, _clean_text(f"  - {bullet}"))

                pdf.ln(2)

    # Education
    if education:
        _add_section_header(pdf, "EDUCATION")
        for edu in education:
            if isinstance(edu, dict):
                degree = edu.get("degree", edu.get("degree_line", ""))
                institution = edu.get("institution", "")
                dates = edu.get("dates", "")

                if degree:
                    pdf.set_font("Helvetica", "B", 10)
                    pdf.set_text_color(30, 30, 30)
                    pdf.cell(0, 5, _clean_text(degree), new_x="LMARGIN", new_y="NEXT")

                if institution or dates:
                    pdf.set_font("Helvetica", "I", 9)
                    pdf.set_text_color(100, 100, 100)
                    inst_line = institution or ""
                    if dates:
                        inst_line += f" | {dates}" if inst_line else dates
                    pdf.cell(0, 5, _clean_text(inst_line), new_x="LMARGIN", new_y="NEXT")

                pdf.ln(2)

    # Certifications
    if certifications:
        _add_section_header(pdf, "CERTIFICATIONS")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(40, 40, 40)
        for cert in certifications:
            if cert:
                pdf.cell(5)
                pdf.cell(0, 5, _clean_text(f"- {str(cert)}"), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    temp_dir = tempfile.mkdtemp()
    pdf_path = os.path.join(temp_dir, "optimized_resume.pdf")
    pdf.output(pdf_path)
    return pdf_path


def _add_section_header(pdf: FPDF, title: str) -> None:
    """Add a styled section header."""
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 58, 95)
    pdf.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(200, 213, 225)
    pdf.set_line_width(0.3)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)


def _clean_text(text: str) -> str:
    """Clean text for PDF output - replace unsupported characters."""
    if not text:
        return ""
    replacements = {
        "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-", "\u2022": "-", "\u2026": "...",
        "\u00a0": " ", "\u200b": "", "\u2028": " ", "\u2029": " ",
        "\u00b7": "-", "\u25cf": "-", "\u25cb": "-", "\u25aa": "-",
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    return text.encode("latin-1", errors="replace").decode("latin-1")
