# Career Chatbot (Applications Assistant)

AI-assisted career chatbot for job seekers.  
It helps with resume analysis, ATS optimization, job matching, cover letter drafting, interview prep, salary negotiation tips, and application tracking.

## What It Does

- Resume review with ATS score, matched skills, and missing skills.
- ATS optimization with auto-improved resume bullets.
- Job board integration links for Indeed and LinkedIn.
- ScaleDown compression for job descriptions (target up to 80%).
- Bulk posting analysis for 100+ roles (paste multiple JDs).
- Personalized application packet (resume draft + cover letter + skill gaps).
- Interview prep prompts with STAR framework.
- Salary negotiation guidance by role type.
- Application tracking with conversion metrics.

## Tech Stack

- Python 3.13+
- Streamlit UI
- scikit-learn TF-IDF + cosine similarity
- sentence-transformers (optional semantic scoring fallback)
- Local JSON persistence for application tracking

## Project Structure

```text
ui/app.py                 # Streamlit interface
services/engine.py        # ATS scoring engine
services/career.py        # Career assistant workflows
services/rewrite.py       # Resume bullet improvements
services/interview.py     # Interview question generation
utils/validate.py         # Input checks
corpus/                   # Sample job descriptions
tests/test_all.py         # Unit tests
```

## Quick Start

1. Install dependencies:

```powershell
pip install -r requirements.txt
```

2. Run app:

```powershell
streamlit run ui/app.py
```

3. Run tests:

```powershell
pytest -q
```

## How to Use

1. Paste your resume and target job description.
2. Open `Resume + ATS` tab:
- Run `Analyze Resume` for ATS score and optimized resume draft.
- Review ScaleDown compressed JD summary.
3. Open `Job Matching` tab:
- Use corpus matching.
- Open generated Indeed/LinkedIn links.
- Paste multiple JDs separated by `---`, then run bulk analysis.
4. Open `Cover Letter + Prep` tab:
- Generate a cover letter.
- Generate personalized application packet.
- Review interview and salary guidance.
5. Open `Tracking + Results` tab:
- Track applications and status changes.
- Monitor application-to-interview conversion and projected improvement.

## ScaleDown Notes

- Compression target is set with `keep_ratio=0.2` (about 80% reduction when possible).
- Bulk mode summarizes each posting and reports average compression.

## Quality and Testing

- Core flows are covered in `tests/test_all.py`.
- Tracker logic is tested with temporary files.
- Semantic model loading is optional; system falls back to keyword similarity.

## Current Limitations

- Job board integration is link-based (no API ingestion).
- Tracker is local JSON (single-user local state).
- Cover letter generation is rule/template-based.
- Success stories are sample narratives, not analytics-generated.

## Recommended Next Improvements

1. Add direct job board API ingestion and deduplication.
2. Add resume parsing from PDF/DOCX upload in UI.
3. Add role-aware prompt templates for cover letters.
4. Add dashboard charts for funnel analytics by week/month.
5. Export personalized packets to DOCX/PDF.
6. Add authentication and cloud database for multi-user tracking.

## Git Publish

```powershell
git add -A
git commit -m "Add README and improve career chatbot workflows"
git push -u origin main
```
