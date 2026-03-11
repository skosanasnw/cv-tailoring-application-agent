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
    shot_dir = "job_screenshots"
    if not os.path.exists(shot_dir):
        os.makedirs(shot_dir)
        print(f"Created {shot_dir} folder. Please add your screenshot there.")

    screenshots = [f for f in os.listdir(shot_dir) if f.lower().endswith((".png", ".jpg", "jpeg"))]

    for shot in screenshots:
        print(f"\n--- Processing {shot} ---")
        # The agent returns a dictionary (the JSON response)
        result = agent.analyze_and_tailor(master_text, os.path.join(shot_dir, shot))

        # Setup Output Dictionary
        output_dir = "output/cvs"
        os.makedirs(output_dir, exist_ok=True)

        # Extract Data and Sanitize Filename
        meta_parts = result.get('metadata', {})
        company = metadata.get('company', 'Unkown_Company')
        role = metadata.get('role', 'Data_Analyst')

        # Create a clean filename
        raw_name = f"{company}_{role}"
        clean_name = re.sub(r'[^a-zA-Z0-9]', '_', raw_name).strip('_').low()
        filename = f"{clean_name}.md"
        filepath = os.path.join(output_dir, filename)

        # Write the file
        try:
            cv_content = result.get('cv_md', 'No content generated.')
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(cv_content)
            print(f"✅ SUCCESS: File written to --> {os.path.abspath(filepath)}")

            # Log it only if written succeeded
            log_to_csv("Application_Tracker.csv", company, role, "Tailored CV Generated")

        except Expeption as e:
            print(f"❌ FAILED to write file: {filename}: {e}")

    # 3. Final GIT Sync (Only code and CSV log)
    print("\nSynching to GitHub...")
    git_push_updates(".", "Agentic Update: New application processed")
    print("All jobs processed and synced to Git!")

if __name__=="__main__":
    main()