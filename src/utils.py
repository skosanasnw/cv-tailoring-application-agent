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

    # Remove  chars that aren't standard Latin-1 ('💻','📍', etc.)
    clean_content = "".join(c for c in line if ord(c) < 256)

    for line in md_content.split('\n'):
        # safe_line = "".join(c for c in line if ord(c) < 256).strip()
        if not safe_line:
            line = line.strip()
            if not line:
                pdf.ln(2)
            continue

        # Basic Heading check (lines starting with #)
        if safe_line.startswith('#'):
            pdf.ln(4) #Add extra space BEFORE  a new section
            pdf.set_font("helvetica", 'B', 12)
            pdf.multi_cell(0, 8, safe_line.lstrip('#').strip().upper(), align='L') # UPPERCASE headers
            pdf.set_font("helvetica", size=10)

        # Bold Text Check (looking for **text**)
        # elif "**" in safe_line:
        #     # This regex splits the line parts: normal and bold
        #     parts = re.split(r'(\*\*.*?\*\*)', safe_line)
        #     for part in parts:
        #         if pdf.get_x() > 170:
        #             pdf.ln(6)
        #
        #         if part.startswith('**') and part.endswith('**'):
        #             pdf.set_font("helvetica", 'B', 10)
        #             pdf.write(5, part.replace('**', ''))

        # Regular lines with better line-height
        else:
            pdf.multi_cell(0,6, safe_line, markdown=True)
    pdf.output(output_path)

def save_cv_md(content: str, filepath: str):
    """"Save the generated CV text to a markdown file."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)