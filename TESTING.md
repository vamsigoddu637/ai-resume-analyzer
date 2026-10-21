# Manual testing checklist

- [ ] App starts with `streamlit run app.py`.
- [ ] Clicking Analyze without a PDF displays a validation message.
- [ ] Missing job title is rejected.
- [ ] Very short job description is rejected.
- [ ] A normal text-based PDF is analyzed.
- [ ] A scanned/image-only PDF displays a helpful message.
- [ ] Skills present in both resume and job description are listed as matched.
- [ ] Job skills absent from the resume are listed as skills to review.
- [ ] CSV report downloads and opens correctly.
- [ ] Analysis appears in Analysis History after a rerun.
- [ ] History CSV downloads.
- [ ] SQLite database is excluded from Git commits.
