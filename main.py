import os
from dotenv import load_dotenv
from src.agent_logic import JobTailorAgent
from src.utils import extract_text_from_docx, log_to_csv, git_push_updates

load_dotenv()

def main():
    # Setup
    API_KEY = os.getenv("GEMINI_API_KEY")
    agent = JobTailorAgent(API_KEY)

    # 1. Load Master Data
    master_text = extract_text_from_docx("MASTER CV.docx")

    # 2. Process all screenshots in folder
    screenshots = [f for f in os.listdir("job_screenshots") if f.endswith((".png", ".jpg", "jpeg"))]

    for shot in screenshots:
        print(f"Processing {shot}...")
        result = agent.analyze_and_tailor(master_text, f"job_screenshots/{shot}")

        # Save generated files
        # (Using a simple split for metadata, e.g., 'Google|AI_Engineer')
        meta_parts = result['metadata'].split("|")
        company = meta_parts[0] if len(meta_parts) > 0 else "Unkown"
        role = meta_parts[1] if len(meta_parts) > 1 else "Role"

        # Write tailored CV and Prep files
        with open(f"Generated_Docs/CV_{company}.md", "w") as f:
            f.write(result['cv_md'])

        # Log it
        log_to_csv("Application_Tracker.cs", company, role, "Check Prep File")

    # 3. Final GIT Sync (Only code and CSV log)
    git_push_updates(".", "Agentic Update: New application processed")
    print("All jobs processed and synced to Git!")

if __name__=="__main__":
    main()