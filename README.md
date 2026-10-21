# AI Resume Analyzer

A portfolio project that compares a PDF resume with a job description. It extracts text, detects skills, estimates keyword coverage and TF-IDF cosine similarity, highlights skills to review, and stores analysis summaries in SQLite.

## Features
- PDF resume text extraction with PyMuPDF
- Skill detection from a configurable skill dictionary
- Matched and missing skill lists
- Estimated match score, skill coverage, and text similarity
- Interactive Plotly chart
- CSV report download
- SQLite analysis history
- Streamlit interface

## Tech stack
Python, Streamlit, PyMuPDF, Pandas, scikit-learn, Plotly, SQLite, Git/GitHub.

## Setup

Python 3.10+ is recommended.

```bash
python -m venv .venv
```

Activate the environment:

**Windows**
```bash
.venv\Scripts\activate
```

**macOS/Linux**
```bash
source .venv/bin/activate
```

Install packages and run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Streamlit will show a local URL, usually `http://localhost:8501`.

## How to use
1. Open **Analyze Resume**.
2. Upload a text-based PDF resume.
3. Enter a job title.
4. Paste the target job description.
5. Select **Analyze Resume**.
6. Review the estimated score, matched skills, skills to review, and suggestions.
7. Download the CSV report or view **Analysis History**.

## Score methodology
- Skill coverage = number of detected job skills found in the resume / number of detected job skills × 100.
- Text similarity = TF-IDF cosine similarity between resume text and job description.
- Estimated match score = 70% skill coverage + 30% text similarity.

This score is a simple project metric, not an official ATS score, validated hiring predictor, or guarantee of selection. The result depends on the skill dictionary and the text extracted from the PDF.

## Database
The app creates `resume_analyzer.db` locally. The `analyses` table stores timestamp, uploaded filename, job title, estimated score, detected skills, missing skills, and similarity score. Resume file contents are not stored in the database.

## Known limitations
- Scanned or image-only PDFs may produce little or no extracted text.
- The skill dictionary is intentionally small and should be expanded.
- Keyword detection can miss synonyms and does not measure proficiency.
- Local SQLite history is not a multi-user production database.
- Do not upload private resumes unless you are comfortable with the processing and storage arrangement.

## Suggested next steps
- Add tests for PDF extraction, skill detection, and scoring.
- Add OCR for scanned documents.
- Add section detection for education, experience, projects, and certifications.
- Add SQL filters and aggregate analytics.
- Add an option to delete saved history.
- Deploy through Streamlit Community Cloud after reviewing privacy and configuration.

## Project structure
```text
ai-resume-analyzer/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── resume_analyzer.db   # generated locally; not committed
```

## Resume bullet (use only after you build and test it)
- Developed a Python and Streamlit resume analyzer that extracts PDF text, identifies job-related skills, estimates resume-to-job-description similarity using TF-IDF, and stores analysis summaries in SQLite.
- Created an interactive dashboard with matched/missing skill summaries, Plotly visualizations, and downloadable CSV reports.

## GitHub
Create a new public repository named `ai-resume-analyzer`, then push the project files. Do not commit private resumes, the SQLite database, virtual environments, or secrets.
