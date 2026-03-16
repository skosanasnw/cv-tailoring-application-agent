# CV optimizing AI agent
An autonomous agent that uses Gemini 3 Flash to optimize a master CV into  a role-specific masterpiece.

##Tech Stack
    -AI: Gemini 3 Flash (Vision + High-reasoning)
    -Engine: Python 3.12
    -Automation:Selenium
    -GitPython (Automating Git commands)This project includes a custom automation utility in `src/utils.py` that converts generated Markdown CVs into polished PDF documents.

### 🛠️ Key Technical Features
* **Dynamic Header Extraction**: Automatically identifies contact details from the Markdown to create a centered executive header.
* **Smart Skip Logic**: Prevents duplication of header information in the body of the CV.
* **Character Cleaning**: Strips non-Latin-1 characters to ensure font compatibility while preserving professional bullet points.
* **Professional Formatting**: Automatically handles section headers, indented bullets, and automatic word-wrapping.
