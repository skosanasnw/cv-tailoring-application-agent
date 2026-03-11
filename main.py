import os
import re
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
        meta_parts = result['cv_md'].split("|")
        company = meta_parts[0] if len(meta_parts) > 0 else "Unkown"
        role = meta_parts[1] if len(meta_parts) > 1 else "Role"

        # Write tailored CV and Prep files
        output_dir = "output/cvs"
        os.makedirs(output_dir, exist_ok=True)

        # Use .get() to prevent KeyErrors if the AI misses a field
        raw_name = res.get('metadata',{}.get('file_name', 'tailored_cv')
        clean_name = re.sub(r'[^a-zA-Z0-9]', '_', raw_name).strip('_').low()
        filename = f"{clean_name}.md"
        filepath = os.path.join(output_dir, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(res.get('cv_md', ''))
            print(f"✅ SUCCESS: File written to --> {os.path.abspath(filepath)}")
        except Expeption as e:
            print(f"❌ FAILED to write file: {e}")
        # ---TO HERE ---

        # Log it
        log_to_csv("Application_Tracker.cs", company, role, "Check Prep File")

    # 3. Final GIT Sync (Only code and CSV log)
    git_push_updates(".", "Agentic Update: New application processed")
    print("All jobs processed and synced to Git!")

if __name__=="__main__":
    main()