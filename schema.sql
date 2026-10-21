CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    file_name TEXT NOT NULL,
    job_title TEXT NOT NULL,
    match_score REAL NOT NULL,
    resume_skills TEXT NOT NULL,
    missing_skills TEXT NOT NULL,
    similarity_score REAL NOT NULL
);

-- Example portfolio query: average score by job title
SELECT job_title, ROUND(AVG(match_score), 1) AS average_match_score,
       COUNT(*) AS analyses_count
FROM analyses
GROUP BY job_title
ORDER BY average_match_score DESC;
