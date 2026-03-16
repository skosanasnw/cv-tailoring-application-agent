import pandas as pd
from docx2python import docx2python
from git import Repo
import os
from fpdf import FPDF
import re

def extract_text_from_docx(file_path: str) -> str:
    """Extracts all text from a docx (word) file including headers/footers."""
    with docx2python(file_path) as docx_content:
        return docx_content.text

def log_to_csv(log_path: str, company: str, role: str, score: str):
    """Updates the persistent application log."""
    new_entry = {
        "Date": pd.Timestamp.now().strftime("%Y-%m-%d"),
        "Company": company,
        "Role": role,
        "ATS_Score": score,
        "Status": "Drafted"
    }
    if os.path.exists(log_path):
        df =pd.read_csv(log_path)
    else:
        df = pd.DataFrame(columns=["Date", "Company", "Role", "ATS_Score", "Status"])

    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)

def git_push_updates(repo_path: str, message: str):
    """Syncs code changes and the log file to GitHub"""
    repo = Repo(repo_path)
    repo.git.add(all=True)
    repo.index.commit(message)
    # origin = repo.remote(name='origin')
    # origin.push()
    
def convert_md_to_pdf(md_content, output_path):
    pdf = FPDF ()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("helvetica", size=10)

    # Dynamic Detail extraxion: Take first 3 lines for the header
    lines = md_content.split('\n')
    header_lines = []
    for line in lines:
        clean_line = "".join(c for c in line if ord(c) < 256).strip()
        if clean_line:
            # Remove MD markers like # or *
            header_lines.append(clean_line.replace('#', '').replace('*', ''))
        if len(header_lines) >= 3:
            break

    # Fill in blanks if the CV is too short
    while len(header_lines) < 3:
        header_lines.append("")

    # Work on the Dynamic header
    # Top line (name)- Big and centered
    pdf.set_font("helvetica", "B", 20)
    pdf.cell(0, 12, header_lines[0], ln=True, align='C')

    # Second line (contact details/location)- Centered
    pdf.set_font("helvetica", size=10)
    pdf.cell(0, 6, header_lines[1], ln=True, align='C')

    # Third line (email/links)- Centered
    pdf.cell(0, 6, header_lines[2], ln=True, align='C')

    pdf.ln(8) # Space before the rest of the CV
    # ------------------------------------
    body_started = False # Track when to start printing
    for line in lines:
        safe_line = "".join(c for c in line if ord(c) < 256).strip()

        # Skip if haven't reached heading
        if not body_started:
            if safe_line.startswith('#'):
                body_started = True
            else:
                continue #Skip the contact info lines we used in the header

        # Reset horizontal position to the left  margin
        pdf.set_x(10)

        if not safe_line:
                pdf.ln(2)
                continue

        # Basic Heading check (lines starting with #)
        if safe_line.startswith('#'):
            pdf.ln(4) #Add extra space BEFORE  a new section
            pdf.set_font("helvetica", 'B', 12)
            pdf.multi_cell(190, 8, safe_line.lstrip('#').strip().upper(), align='L') # UPPERCASE headers
            pdf.set_font("helvetica", size=10)

        # Bullet Points (CHecking for - or *)
        elif safe_line.startswith('_') or safe_line.startswith('*'):
            pdf.set_x(15)
            # Replace the MD  bullet with a clean dot and use markdown=True for bolding
            clean_bullet = chr(149) + " " + safe_line[1:].lstrip("-*").strip()
            pdf.multi_cell(175, 6, clean_bullet, markdown=True)

        # Regular lines with better line-height
        else:
            pdf.multi_cell(190,6, safe_line, markdown=True)

    pdf.output(output_path)

def save_cv_md(content: str, filepath: str):
    """"Save the generated CV text to a markdown file."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)