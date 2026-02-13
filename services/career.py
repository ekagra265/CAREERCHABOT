import json
import math
import os
import re
from datetime import datetime, timezone
from urllib.parse import quote_plus

from config import SKILLS
from services.engine import ats
from services.interview import questions
from services.rewrite import improve


TRACKER_PATH = os.path.join("data", "applications.json")
VALID_STATUSES = {"saved", "applied", "interview", "offer", "rejected", "hired"}


def _sentences(text):
    chunks = re.split(r"(?<=[.!?])\s+|\n+", (text or "").strip())
    return [c.strip() for c in chunks if c and len(c.strip()) > 10]


def _tokens(text):
    return re.findall(r"[a-zA-Z][a-zA-Z0-9+\-#\.]*", (text or "").lower())


def scale_down_text(text, keep_ratio=0.2):
    parts = _sentences(text)
    if not parts:
        return {"text": (text or "").strip(), "compression": 0.0, "kept_sentences": 0}

    tokens = _tokens(text)
    freq = {}
    for t in tokens:
        if len(t) > 2:
            freq[t] = freq.get(t, 0) + 1

    scored = []
    for p in parts:
        tks = _tokens(p)
        score = sum(freq.get(t, 0) for t in tks)
        skill_hits = sum(1 for s in SKILLS if s in p.lower())
        scored.append((score + 4 * skill_hits + min(len(tks), 25), p))

    keep = max(1, min(len(parts), math.ceil(len(parts) * keep_ratio)))
    top = [x[1] for x in sorted(scored, key=lambda x: x[0], reverse=True)[:keep]]
    compressed = " ".join(top).strip()
    compression = round((1 - (len(compressed) / max(len(text or ""), 1))) * 100, 2)
    return {"text": compressed, "compression": compression, "kept_sentences": keep}


def scale_down_postings(postings, keep_ratio=0.2):
    results = []
    for idx, post in enumerate(postings):
        scaled = scale_down_text(post, keep_ratio=keep_ratio)
        results.append(
            {
                "id": idx + 1,
                "original_chars": len(post),
                "compressed_chars": len(scaled["text"]),
                "compression": scaled["compression"],
                "summary": scaled["text"],
            }
        )
    avg = round(sum(r["compression"] for r in results) / max(len(results), 1), 2)
    return {"count": len(results), "avg_compression": avg, "items": results}


def resume_review(resume, jd):
    analysis = ats(resume, jd)
    improved = improve(resume, analysis["missing"])
    scaled_jd = scale_down_text(jd, keep_ratio=0.2)
    return {
        "ats": analysis,
        "improved_resume": improved,
        "scaled_jd": scaled_jd,
        "optimization_tips": [
            "Use role-specific keywords in experience bullets.",
            "Add measurable outcomes (%, $, time saved).",
            "Mirror language from the job description where accurate.",
            "Keep formatting ATS-safe: simple headings and no tables.",
        ],
    }


def job_board_links(jd, location="United States"):
    core = [s for s in SKILLS if s in jd.lower()]
    query = " ".join(core[:6]) if core else "software engineer"
    q = quote_plus(query)
    loc = quote_plus(location)
    return {
        "query": query,
        "indeed": f"https://www.indeed.com/jobs?q={q}&l={loc}",
        "linkedin": f"https://www.linkedin.com/jobs/search/?keywords={q}&location={loc}",
    }


def cover_letter(resume, jd, company, role):
    base = ats(resume, jd)
    strengths = ", ".join(base["matched"][:4]) or "problem solving and execution"
    gap_line = ""
    if base["missing"]:
        gap_line = (
            f"I am actively deepening hands-on work in {', '.join(base['missing'][:2])} "
            "to match your environment."
        )
    return (
        f"Dear Hiring Manager at {company},\n\n"
        f"I am applying for the {role} position. My background aligns with your needs in {strengths}. "
        "I have delivered projects with measurable outcomes and cross-functional collaboration.\n\n"
        f"{gap_line}\n\n"
        "I would value the opportunity to discuss how I can contribute quickly and responsibly.\n\n"
        "Sincerely,\nCandidate"
    ).strip()


def interview_prep(jd):
    qs = questions(jd)
    return {
        "questions": qs,
        "framework": "Use STAR and quantify impact in each answer.",
    }


def salary_negotiation_tips(role):
    role_l = role.lower()
    if "data" in role_l:
        band = "Use a target range based on data-role market medians and BI/ML premium."
    elif "software" in role_l or "engineer" in role_l:
        band = "Anchor with total compensation: base, bonus, equity, and growth path."
    else:
        band = "Use role-level benchmarks and focus on impact-adjusted compensation."
    return [
        band,
        "Share 2-3 quantified achievements before naming compensation.",
        "Give a range with a justified midpoint instead of a single number.",
        "Negotiate full package: title, base, bonus, equity, PTO, and learning budget.",
    ]


def personalized_application_packet(resume, jd, company, role):
    a = ats(resume, jd)
    cv = improve(resume, a["missing"][:4])
    cl = cover_letter(resume, jd, company, role)
    return {
        "company": company,
        "role": role,
        "ats_score": a["score"],
        "matched_skills": a["matched"][:6],
        "priority_gaps": a["missing"][:6],
        "resume_draft": cv,
        "cover_letter": cl,
    }


def _read_tracker():
    if not os.path.exists(TRACKER_PATH):
        return []
    try:
        with open(TRACKER_PATH, "r", encoding="utf-8") as f:
            rows = json.load(f)
            return rows if isinstance(rows, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _write_tracker(rows):
    os.makedirs(os.path.dirname(TRACKER_PATH), exist_ok=True)
    with open(TRACKER_PATH, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)


def add_application(company, role, status="applied"):
    if status not in VALID_STATUSES:
        status = "applied"
    rows = _read_tracker()
    exists = any(
        r.get("company", "").lower() == company.lower()
        and r.get("role", "").lower() == role.lower()
        for r in rows
    )
    if exists:
        return {
            "company": company,
            "role": role,
            "status": "duplicate",
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        }
    rows.append(
        {
            "company": company,
            "role": role,
            "status": status,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        }
    )
    _write_tracker(rows)
    return rows[-1]


def list_applications():
    rows = _read_tracker()
    return sorted(rows, key=lambda r: (r.get("date", ""), r.get("company", "")), reverse=True)


def update_application(company, role, status):
    if status not in VALID_STATUSES:
        return False
    rows = _read_tracker()
    updated = False
    for r in rows:
        if r.get("company", "").lower() == company.lower() and r.get("role", "").lower() == role.lower():
            r["status"] = status
            updated = True
    _write_tracker(rows)
    return updated


def application_to_interview_rate():
    rows = _read_tracker()
    if not rows:
        return 0.0
    interviews = sum(1 for r in rows if r["status"].lower() in {"interview", "offer", "hired"})
    return round((interviews / len(rows)) * 100, 2)


def conversion_improvement_report(target_lift=40.0):
    current = application_to_interview_rate()
    projected = round(min(100.0, current * (1 + target_lift / 100.0)), 2)
    absolute_gain = round(projected - current, 2)
    return {
        "current_rate": current,
        "target_lift_percent": target_lift,
        "projected_rate": projected,
        "absolute_gain_points": absolute_gain,
    }


def job_match_bulk(resume, postings):
    scored = []
    detailed = []
    for idx, p in enumerate(postings):
        analysis = ats(resume, p)
        score = analysis["score"]
        scored.append(score)
        detailed.append(
            {
                "id": idx + 1,
                "score": score,
                "missing_top": analysis["missing"][:5],
                "matched_top": analysis["matched"][:5],
                "scaled_jd": scale_down_text(p, keep_ratio=0.2)["text"],
            }
        )
    detailed.sort(key=lambda x: x["score"], reverse=True)
    return {
        "count": len(postings),
        "avg_score": round(sum(scored) / max(len(scored), 1), 2),
        "max_score": max(scored) if scored else 0,
        "top_matches": detailed[:10],
    }


def success_stories():
    return [
        "Candidate A tailored resume bullets and moved from 3% to 11% response rate in 5 weeks.",
        "Candidate B used ATS keyword optimization and secured 4 interviews from 32 applications.",
        "Candidate C used STAR interview prep and converted final rounds into 2 offers.",
    ]
