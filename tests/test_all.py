
import os

from services.engine import ats
import services.career as career
from services.career import (
    add_application,
    application_to_interview_rate,
    conversion_improvement_report,
    cover_letter,
    job_match_bulk,
    job_board_links,
    scale_down_postings,
    salary_negotiation_tips,
    scale_down_text,
    update_application,
)
from utils.validate import check

def test_flow():
    r="python sql 3 year experience project"
    j="need python sql excel"
    assert check(r,j)=="ok"
    a=ats(r,j)
    assert a['score']>=0


def test_scale_down_and_cover_letter():
    r="python sql testing communication 4 year experience projects and impact"
    j=(
        "We need python sql communication skills for data dashboards and API automation. "
        "Testing and cloud exposure are preferred. Build reports and optimize workflows."
    )
    s = scale_down_text(j, keep_ratio=0.2)
    assert len(s["text"]) > 0
    assert s["compression"] >= 0

    cl = cover_letter(r, j, "Acme", "Data Analyst")
    assert "Acme" in cl
    assert "Data Analyst" in cl


def test_job_links_and_salary_tips():
    j = "python sql tableau communication"
    links = job_board_links(j)
    assert "indeed.com" in links["indeed"]
    assert "linkedin.com" in links["linkedin"]
    assert len(salary_negotiation_tips("Software Engineer")) >= 3


def test_bulk_matching_and_scaledown():
    resume = "python sql testing cloud machine learning 5 year experience projects"
    postings = [
        "Need python sql and dashboard work for analytics.",
        "Java API testing and cloud deployment experience required.",
        "Machine learning, python, and communication skills.",
    ]
    bulk = job_match_bulk(resume, postings)
    scaled = scale_down_postings(postings, keep_ratio=0.2)
    assert bulk["count"] == 3
    assert len(bulk["top_matches"]) > 0
    assert scaled["count"] == 3
    assert scaled["avg_compression"] >= 0


def test_tracker_and_conversion_report():
    original = career.TRACKER_PATH
    test_path = os.path.join("data", "applications_test.json")
    try:
        career.TRACKER_PATH = test_path
        if os.path.exists(test_path):
            os.remove(test_path)
        add_application("Acme", "Data Analyst", "applied")
        assert update_application("Acme", "Data Analyst", "interview") is True
        rate = application_to_interview_rate()
        report = conversion_improvement_report(target_lift=40.0)
        assert rate == 100.0
        assert report["projected_rate"] == 100.0
    finally:
        career.TRACKER_PATH = original
        if os.path.exists(test_path):
            os.remove(test_path)
