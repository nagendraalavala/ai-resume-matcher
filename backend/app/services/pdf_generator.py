"""PDF generator - creates professionally formatted resume PDFs."""

import os
import tempfile
from typing import Any
from weasyprint import HTML


def generate_pdf(resume_data: dict[str, Any]) -> str:
    """Generate a clean professional PDF from resume data."""
    html_content = _build_html(resume_data)

    temp_dir = tempfile.mkdtemp()
    pdf_path = os.path.join(temp_dir, "optimized_resume.pdf")

    HTML(string=html_content).write_pdf(pdf_path)
    return pdf_path


def _build_html(data: dict[str, Any]) -> str:
    """Build HTML for the resume."""
    name = data.get("name", "")
    email = data.get("email", "")
    phone = data.get("phone", "")
    summary = data.get("summary", "")
    skills = data.get("skills", [])
    experience = data.get("experience", [])
    education = data.get("education", [])
    certifications = data.get("certifications", [])

    # Contact line
    contact_parts = []
    if email:
        contact_parts.append(email)
    if phone:
        contact_parts.append(phone)
    contact_line = " | ".join(contact_parts)

    # Skills HTML
    skills_html = ""
    if skills:
        skill_items = ", ".join(skills) if isinstance(skills[0], str) else ", ".join(str(s) for s in skills)
        skills_html = f"""
        <div class="section">
            <h2>Skills</h2>
            <p>{skill_items}</p>
        </div>"""

    # Experience HTML
    exp_html = ""
    if experience:
        exp_items = []
        for exp in experience:
            if isinstance(exp, dict):
                title = exp.get("title", exp.get("title_line", ""))
                company = exp.get("company", exp.get("company_line", ""))
                dates = exp.get("dates", "")
                bullets = exp.get("bullets", [])

                header = f"<h3>{title}</h3>"
                if company:
                    header += f"<p class='company'>{company}"
                    if dates:
                        header += f" | {dates}"
                    header += "</p>"

                bullet_html = ""
                if isinstance(bullets, list):
                    bullet_html = "<ul>" + "".join(f"<li>{b}</li>" for b in bullets if b) + "</ul>"
                elif isinstance(bullets, str) and bullets:
                    bullet_lines = bullets.split("\n")
                    bullet_html = "<ul>" + "".join(f"<li>{b}</li>" for b in bullet_lines if b.strip()) + "</ul>"

                exp_items.append(f"<div class='entry'>{header}{bullet_html}</div>")
            else:
                exp_items.append(f"<div class='entry'><p>{exp}</p></div>")

        exp_html = f"""
        <div class="section">
            <h2>Experience</h2>
            {''.join(exp_items)}
        </div>"""

    # Education HTML
    edu_html = ""
    if education:
        edu_items = []
        for edu in education:
            if isinstance(edu, dict):
                degree = edu.get("degree", edu.get("degree_line", ""))
                institution = edu.get("institution", "")
                dates = edu.get("dates", "")
                line = f"<h3>{degree}</h3>"
                if institution:
                    line += f"<p class='company'>{institution}"
                    if dates:
                        line += f" | {dates}"
                    line += "</p>"
                edu_items.append(f"<div class='entry'>{line}</div>")
            else:
                edu_items.append(f"<div class='entry'><p>{edu}</p></div>")

        edu_html = f"""
        <div class="section">
            <h2>Education</h2>
            {''.join(edu_items)}
        </div>"""

    # Certifications HTML
    cert_html = ""
    if certifications:
        cert_items = "".join(f"<li>{c}</li>" for c in certifications if c)
        if cert_items:
            cert_html = f"""
            <div class="section">
                <h2>Certifications</h2>
                <ul>{cert_items}</ul>
            </div>"""

    # Summary HTML
    summary_html = ""
    if summary:
        summary_html = f"""
        <div class="section">
            <h2>Professional Summary</h2>
            <p>{summary}</p>
        </div>"""

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    @page {{
        margin: 0.6in 0.7in;
        size: letter;
    }}
    body {{
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-size: 10.5pt;
        line-height: 1.4;
        color: #1a1a1a;
        margin: 0;
        padding: 0;
    }}
    .header {{
        text-align: center;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 2px solid #2563eb;
    }}
    .header h1 {{
        font-size: 20pt;
        margin: 0 0 4px 0;
        color: #1e3a5f;
        letter-spacing: 0.5px;
    }}
    .header .contact {{
        font-size: 9.5pt;
        color: #555;
    }}
    .section {{
        margin-bottom: 10px;
    }}
    .section h2 {{
        font-size: 12pt;
        color: #1e3a5f;
        border-bottom: 1px solid #cbd5e1;
        padding-bottom: 3px;
        margin: 10px 0 6px 0;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }}
    .entry {{
        margin-bottom: 8px;
    }}
    .entry h3 {{
        font-size: 10.5pt;
        margin: 0;
        color: #1a1a1a;
    }}
    .company {{
        font-size: 9.5pt;
        color: #555;
        margin: 1px 0 4px 0;
        font-style: italic;
    }}
    ul {{
        margin: 3px 0;
        padding-left: 18px;
    }}
    li {{
        margin-bottom: 2px;
        font-size: 10pt;
    }}
    p {{
        margin: 3px 0;
    }}
</style>
</head>
<body>
    <div class="header">
        <h1>{name}</h1>
        <div class="contact">{contact_line}</div>
    </div>
    {summary_html}
    {skills_html}
    {exp_html}
    {edu_html}
    {cert_html}
</body>
</html>"""
