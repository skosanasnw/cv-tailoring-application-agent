import pandas as pd
from docx2python import docx2python
from git import Repo
import os

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
    origin = repo.remote(name='origin')
    origin.push()