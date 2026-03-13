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
    
def convert_md_to_pdf(md_content, output_put):
    pdf = FPDF ()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Standard Body Font
    pdf.set_font("helvetica", size=10)
    
    for line in md_content.split('\n'):
        # Basic Heading check (lines starting with #)
        if line.startswith('#'):
            pdf.set_font("helvetica", 'B', 14)
            clean_line = line.lstrip('#').strip()
            pdf.multi_cell(0, 10, clean_line)
            pdf.ln(2)
            pdf.set_font("helvetica", size=10)
            
        # Bold Text Check (looking for **text**)
        elif "**" in line:
            # This regex splits the line parts: normal and bold
            parts = re.split(r'(\*\*.*?\*\*)', line)
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    pdf.set_font("helvetica", 'B', 10)
                    pdf.write(5, part.replace('**', ''))
                else:
                    pdf.set_font("helvetica", size=10)
                    pdf.write(5, part)
                pdf.ln(6)
        
        # Regular lines
        else:
            pdf.multi_cell(0, 5, line)
            pdf.ln(2)
    pdf.output(output_path)

def save_cv_md(content: str, filepath: str):
    """"Save the generated CV text to a markdown file."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)