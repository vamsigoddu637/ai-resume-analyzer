
import sqlite3
from datetime import datetime
import re

import pandas as pd
import plotly.express as px
import pymupdf
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# -------------------- CONFIGURATION --------------------

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = "resume_analyzer.db"

SKILL_BANK = {
    "Python": ["python"],
    "SQL": ["sql", "mysql", "postgresql", "sqlite"],
    "Excel": ["excel", "pivot table", "vlookup", "xlookup"],
    "Power BI": ["power bi", "dax"],
    "Tableau": ["tableau"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Statistics": [
        "statistics", "statistical analysis", "hypothesis testing"
    ],
    "Machine Learning": ["machine learning", "scikit-learn", "sklearn"],
    "NLP": ["nlp", "natural language processing"],
    "Data Visualization": [
        "data visualization", "matplotlib", "seaborn", "plotly"
    ],
    "ETL": ["etl", "data pipeline", "data pipelines"],
    "Data Cleaning": [
        "data cleaning", "data preprocessing", "data cleansing"
    ],
    "Power Query": ["power query"],
    "Git": ["git", "github"],
    "Communication": ["communication", "presentation", "stakeholder"],
    "Project Management": ["project management", "agile", "scrum"],
    "Java": ["java"],
    "C++": ["c++"],
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure", "microsoft azure"],
    "Data Warehousing": ["data warehouse", "data warehousing"],
}


# -------------------- DATABASE --------------------

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                file_name TEXT NOT NULL,
                job_title TEXT NOT NULL,
                match_score REAL NOT NULL,
                resume_skills TEXT NOT NULL,
                missing_skills TEXT NOT NULL,
                similarity_score REAL NOT NULL
            )
        """)


def save_analysis(file_name, job_title, result):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO analyses (
                created_at,
                file_name,
                job_title,
                match_score,
                resume_skills,
                missing_skills,
                similarity_score
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(timespec="seconds"),
            file_name,
            job_title,
            result["overall_score"],
            ", ".join(result["resume_skills"]),
            ", ".join(result["missing_skills"]),
            result["similarity_score"],
        ))


def load_history():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("""
            SELECT
                id,
                created_at,
                file_name,
                job_title,
                match_score,
                resume_skills,
                missing_skills,
                similarity_score
            FROM analyses
            ORDER BY id DESC
        """, conn)


# -------------------- RESUME PROCESSING --------------------

def extract_pdf_text(file_bytes):
    with pymupdf.open(stream=file_bytes, filetype="pdf") as doc:
        return "\n".join(
            page.get_text() for page in doc
        ).strip()


def normalize_text(text):
    return re.sub(r"\s+", " ", text.lower()).strip()


def detect_skills(text):
    normalized = normalize_text(text)
    found = []

    for skill, aliases in SKILL_BANK.items():
        for alias in aliases:
            pattern = (
                r"(?<!\w)"
                + re.escape(alias.lower())
                + r"(?!\w)"
            )

            if re.search(pattern, normalized):
                found.append(skill)
                break

    return sorted(found)


def calculate_similarity(resume_text, job_text):
    if not resume_text.strip() or not job_text.strip():
        return 0.0

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
    )

    try:
        matrix = vectorizer.fit_transform([
            resume_text,
            job_text,
        ])

        score = cosine_similarity(
            matrix[0:1],
            matrix[1:2],
        )[0][0]

        return float(score * 100)

    except ValueError:
        # For example, when the text contains no useful vocabulary.
        return 0.0


def analyze_resume(resume_text, job_text):
    resume_skills = detect_skills(resume_text)
    job_skills = detect_skills(job_text)

    matched = sorted(set(resume_skills) & set(job_skills))
    missing = sorted(set(job_skills) - set(resume_skills))

    skill_score = (
        len(matched) / len(job_skills) * 100
        if job_skills else 0.0
    )

    similarity_score = calculate_similarity(
        resume_text,
        job_text,
    )

    # Skill coverage contributes 70%; text similarity contributes 30%.
    overall = (
        0.7 * skill_score
        + 0.3 * similarity_score
    )

    return {
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_score": round(skill_score, 1),
        "similarity_score": round(similarity_score, 1),
        "overall_score": round(overall, 1),
        "has_projects_section": bool(
            re.search(
                r"\bprojects?\b",
                resume_text,
                re.IGNORECASE,
            )
        ),
    }


# -------------------- CUSTOM UI --------------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f7f9ff 0%, #eef2ff 100%);
    color: #172033;
}

[data-testid="stMainBlockContainer"] {
    max-width: 1380px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1 {
    color: #172554 !important;
    font-weight: 800 !important;
    letter-spacing: -1px;
}

h2, h3 {
    color: #1e293b !important;
    font-weight: 700 !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827 0%, #1e1b4b 100%);
}

[data-testid="stSidebar"] * {
    color: #f8fafc;
}

[data-testid="stSidebar"] [data-testid="stAlert"] * {
    color: #172033;
}

.stTextInput input,
.stTextArea textarea {
    background: #ffffff !important;
    color: #172033 !important;
    border: 1px solid #dbe3f0 !important;
    border-radius: 12px !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px #c7d2fe !important;
}

[data-testid="stFileUploader"] {
    background: #ffffff;
    border: 1px dashed #a5b4fc;
    border-radius: 14px;
    padding: 12px;
}

.stButton > button,
.stDownloadButton > button {
    border: none;
    border-radius: 12px;
    min-height: 46px;
    font-weight: 700;
    transition: all 0.2s ease;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #4f46e5, #7c3aed);
    color: white;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(90deg, #4338ca, #6d28d9);
    box-shadow: 0 6px 18px #4f46e533;
    transform: translateY(-1px);
}

.stDownloadButton > button {
    background: #e0e7ff;
    color: #3730a3;
    border: 1px solid #c7d2fe;
}

[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e0e7ff;
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 8px 25px rgba(49, 46, 129, 0.07);
}

[data-testid="stMetricLabel"] {
    color: #64748b;
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    color: #312e81;
    font-weight: 800;
}

[data-testid="stPlotlyChart"] {
    background: #ffffff;
    border: 1px solid #e0e7ff;
    border-radius: 16px;
    padding: 10px;
}

[data-testid="stAlert"] {
    border-radius: 12px;
}

hr {
    border-color: #dbe3f0;
}

footer {
    visibility: hidden;
}

@media (max-width: 768px) {
    [data-testid="stMainBlockContainer"] {
        padding: 1rem;
    }

    h1 {
        font-size: 1.8rem !important;
    }
}
</style>
""", unsafe_allow_html=True)


# -------------------- APP INITIALIZATION --------------------

init_db()

st.title("📄 AI Resume Analyzer")
st.caption(
    "An intelligent resume review dashboard powered by Python, "
    "NLP, skill matching, and SQLite."
)

with st.sidebar:
    st.markdown("## 📄 Resume AI")
    st.caption("Your career preparation workspace")
    st.divider()

    st.markdown("### About")
    st.write(
        "Compare a PDF resume with a target job description "
        "to identify relevant and missing skills."
    )

    st.info(
        "Resume text is processed in memory. The app saves "
        "the filename and analysis summary to local SQLite history."
    )

    page = st.radio(
        "NAVIGATION",
        ["Analyze Resume", "Analysis History", "Project Guide"],
    )


# -------------------- ANALYZE RESUME PAGE --------------------

if page == "Analyze Resume":

    st.markdown("## Analyze your resume")
    st.caption(
        "Upload your resume, enter your target role, "
        "and compare your skills with job requirements."
    )

    left, right = st.columns([0.9, 1.1], gap="large")

    with left:
        with st.container(border=True):
            st.markdown("### 📄 Your resume")

            uploaded_file = st.file_uploader(
                "Upload resume (PDF)",
                type=["pdf"],
                help="Use a text-based PDF for best results.",
            )

            job_title = st.text_input(
                "Target job title",
                placeholder="e.g., Data Analyst Intern",
            )

    with right:
        with st.container(border=True):
            st.markdown("### 🎯 Job requirements")

            job_description = st.text_area(
                "Paste job description",
                height=240,
                placeholder=(
                    "Paste the job responsibilities, "
                    "required skills, and qualifications here..."
                ),
            )

    if st.button(
        "🚀 Analyze Resume",
        type="primary",
        use_container_width=True,
    ):
        if not uploaded_file:
            st.error("Please upload a PDF resume.")

        elif not job_title.strip():
            st.error("Please enter the target job title.")

        elif len(job_description.strip()) < 30:
            st.error(
                "Please enter a more complete job description "
                "(at least 30 characters)."
            )

        else:
            try:
                with st.spinner("Analyzing your resume..."):
                    resume_text = extract_pdf_text(
                        uploaded_file.getvalue()
                    )

                    if len(resume_text) < 40:
                        st.error(
                            "Very little text was extracted. "
                            "This PDF may be scanned or image-only. "
                            "Try a text-based PDF."
                        )
                    else:
                        result = analyze_resume(
                            resume_text,
                            job_description,
                        )

                        save_analysis(
                            uploaded_file.name,
                            job_title.strip(),
                            result,
                        )

                        st.session_state["latest_result"] = result
                        st.session_state["latest_job_title"] = (
                            job_title.strip()
                        )
                        st.session_state["latest_file_name"] = (
                            uploaded_file.name
                        )

                        st.success("Resume analysis completed!")

            except Exception as exc:
                st.error(
                    f"Could not analyze this PDF. "
                    f"Please try another file. Details: {exc}"
                )

    result = st.session_state.get("latest_result")

    if result:
        st.divider()

        st.markdown("## 📊 Analysis results")

        st.caption(
            f"Role: {st.session_state.get('latest_job_title', '')} "
            f"· Resume: {st.session_state.get('latest_file_name', '')}"
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Estimated Match Score",
            f"{result['overall_score']}%",
        )
        c2.metric(
            "Skill Coverage",
            f"{result['skill_score']}%",
        )
        c3.metric(
            "Text Similarity",
            f"{result['similarity_score']}%",
        )

        st.progress(
            min(max(result["overall_score"] / 100, 0.0), 1.0),
            text="Estimated resume-to-job match",
        )

        st.caption(
            "These scores measure text and skill overlap. "
            "They are not an official ATS score or a hiring prediction."
        )

        chart_data = pd.DataFrame({
            "Category": ["Matched skills", "Missing skills"],
            "Count": [
                len(result["matched_skills"]),
                len(result["missing_skills"]),
            ],
        })

        fig = px.bar(
            chart_data,
            x="Category",
            y="Count",
            color="Category",
            color_discrete_map={
                "Matched skills": "#6366f1",
                "Missing skills": "#f59e0b",
            },
            title="Job Skill Coverage",
            text="Count",
        )

        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font_color="#172033",
            showlegend=False,
            margin=dict(l=20, r=20, t=60, b=20),
            xaxis_title=None,
            yaxis_title="Number of skills",
        )

        fig.update_traces(
            textposition="outside",
            marker_line_width=0,
        )

        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2, gap="large")

        with col1:
            with st.container(border=True):
                st.markdown("### 🧠 Skills found in resume")

                if result["resume_skills"]:
                    st.write(", ".join(result["resume_skills"]))
                else:
                    st.info("No known skills detected.")

            with st.container(border=True):
                st.markdown("### ✅ Matched skills")

                if result["matched_skills"]:
                    st.write(", ".join(result["matched_skills"]))
                else:
                    st.info("No matching skills detected yet.")

        with col2:
            with st.container(border=True):
                st.markdown("### 🎯 Skills to review")

                if result["missing_skills"]:
                    st.write(", ".join(result["missing_skills"]))
                else:
                    st.success(
                        "No missing skills were detected from "
                        "the current skill dictionary."
                    )

            with st.container(border=True):
                st.markdown("### 💡 Improvement suggestions")

                suggestions = []

                if result["missing_skills"]:
                    suggestions.append(
                        "If you genuinely have experience with "
                        "these skills, make that experience clearer: "
                        + ", ".join(result["missing_skills"])
                        + "."
                    )

                if not result["has_projects_section"]:
                    suggestions.append(
                        "Consider adding a clearly titled Projects "
                        "section with tools, your contribution, "
                        "and measurable outcomes."
                    )

                suggestions.append(
                    "Use specific, truthful bullet points describing "
                    "what you built, analyzed, or improved."
                )

                suggestions.append(
                    "Tailor your resume to the role without adding "
                    "skills or experience you do not have."
                )

                for suggestion in suggestions:
                    st.markdown(f"- {suggestion}")

        report = pd.DataFrame({
            "Metric": [
                "Estimated match score",
                "Skill coverage",
                "Text similarity",
                "Resume skills",
                "Matched skills",
                "Skills to review",
            ],
            "Result": [
                f"{result['overall_score']}%",
                f"{result['skill_score']}%",
                f"{result['similarity_score']}%",
                ", ".join(result["resume_skills"]),
                ", ".join(result["matched_skills"]),
                ", ".join(result["missing_skills"]),
            ],
        })

        st.download_button(
            "⬇️ Download analysis report (CSV)",
            data=report.to_csv(index=False).encode("utf-8"),
            file_name="resume_analysis_report.csv",
            mime="text/csv",
            use_container_width=True,
        )


# -------------------- ANALYSIS HISTORY PAGE --------------------

elif page == "Analysis History":

    st.markdown("## 🗂️ Analysis history")
    st.caption("Review and download previous resume analyses.")

    history = load_history()

    if history.empty:
        st.info(
            "No analyses saved yet. Analyze a resume to see "
            "your history here."
        )

    else:
        c1, c2 = st.columns(2)

        c1.metric("Total analyses", len(history))

        c2.metric(
            "Average match score",
            f"{history['match_score'].mean():.1f}%",
        )

        with st.container(border=True):
            st.markdown("### Previous analyses")

            st.dataframe(
                history,
                use_container_width=True,
                hide_index=True,
            )

        st.download_button(
            "⬇️ Download history (CSV)",
            data=history.to_csv(index=False).encode("utf-8"),
            file_name="resume_analysis_history.csv",
            mime="text/csv",
            use_container_width=True,
        )

        fig = px.line(
            history.sort_values("id", ascending=True),
            x="id",
            y="match_score",
            markers=True,
            title="Estimated match score by analysis",
            labels={
                "id": "Analysis number",
                "match_score": "Match score (%)",
            },
        )

        fig.update_traces(
            line_color="#6366f1",
            marker_size=9,
        )

        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font_color="#172033",
        )

        st.plotly_chart(fig, use_container_width=True)


# -------------------- PROJECT GUIDE PAGE --------------------

else:

    st.markdown("## 📘 Project guide")
    st.caption(
        "Understand the scoring method, limitations, "
        "and possible future enhancements."
    )

    with st.container(border=True):
        st.markdown("### 🧮 How the score works")

        st.markdown("""
        - **Skill coverage:** matched job skills divided by detected
          job skills, multiplied by 100.
        - **Text similarity:** cosine similarity between TF-IDF
          representations of the resume and job description.
        - **Estimated match score:** 70% skill coverage plus
          30% text similarity.
        """)

    with st.container(border=True):
        st.markdown("### ⚠️ Current limitations")

        st.markdown("""
        - The built-in skill dictionary may miss synonyms and context.
        - Keyword matches do not prove skill proficiency.
        - Scanned PDFs require OCR, which is not included.
        - The project-section check is a simple keyword check.
        - The score should support resume review, not make hiring decisions.
        """)

    with st.container(border=True):
        st.markdown("### 🚀 Future improvements")

        st.markdown("""
        1. Expand the skill dictionary and add unit tests.
        2. Add OCR support for scanned resumes.
        3. Improve resume section detection and NLP.
        4. Add history filters and SQL summary queries.
        5. Add a control to delete saved analysis history.
        """)


# -------------------- FOOTER --------------------

st.divider()

st.caption(
    "Built with Python · Streamlit · PyMuPDF · "
    "scikit-learn · Pandas · Plotly · SQLite"
)
