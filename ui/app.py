
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from services.engine import match_corpus
from services.career import (
    add_application,
    application_to_interview_rate,
    conversion_improvement_report,
    cover_letter,
    interview_prep,
    job_match_bulk,
    job_board_links,
    list_applications,
    personalized_application_packet,
    resume_review,
    salary_negotiation_tips,
    scale_down_postings,
    success_stories,
    update_application,
)
from utils.validate import check

st.set_page_config(layout="wide")
st.title("Advanced Career Assistant")

resume=st.text_area("Resume Text")
jd=st.text_area("Job Description")
company=st.text_input("Target Company", value="Example Corp")
role=st.text_input("Target Role", value="Software Engineer")
location=st.text_input("Target Location", value="United States")
bulk_jds_raw = st.text_area(
    "Bulk Job Descriptions (separate each posting with `---`)",
    height=150,
)

bulk_jds = [x.strip() for x in bulk_jds_raw.split("---") if x.strip()]

tab1, tab2, tab3, tab4 = st.tabs(
    ["Resume + ATS", "Job Matching", "Cover Letter + Prep", "Tracking + Results"]
)

with tab1:
    if st.button("Analyze Resume", key="analyze_resume"):
        msg = check(resume, jd)
        if msg != "ok":
            st.warning(msg)
            st.stop()
        details = resume_review(resume, jd)
        a = details["ats"]
        st.metric("ATS Score", a["score"])
        st.write("Missing Skills", a["missing"])
        st.write("Matched Skills", a["matched"])
        st.subheader("ATS Optimization")
        st.text_area("Improved Resume", details["improved_resume"], height=220)
        st.write("Optimization Tips", details["optimization_tips"])
        st.subheader("ScaleDown Job Description")
        st.metric("Compression %", details["scaled_jd"]["compression"])
        st.text_area("Compressed JD", details["scaled_jd"]["text"], height=180)

with tab2:
    if st.button("Corpus Match", key="corpus_match"):
        st.write(match_corpus(resume, "corpus"))
    links = job_board_links(jd, location=location)
    st.write(f"Suggested search query: `{links['query']}`")
    st.markdown(f"[Indeed Jobs]({links['indeed']})")
    st.markdown(f"[LinkedIn Jobs]({links['linkedin']})")
    if st.button("Analyze Bulk Postings", key="bulk_match"):
        if not resume.strip() or not bulk_jds:
            st.warning("Add resume text and at least one posting in bulk input.")
        else:
            bulk = job_match_bulk(resume, bulk_jds)
            scaled = scale_down_postings(bulk_jds, keep_ratio=0.2)
            st.metric("Postings analyzed", bulk["count"])
            st.metric("Average ATS score", bulk["avg_score"])
            st.metric("Average ScaleDown compression %", scaled["avg_compression"])
            st.write("Top matches", bulk["top_matches"])

with tab3:
    if st.button("Generate Cover Letter", key="cover_letter"):
        st.text_area("Cover Letter Draft", cover_letter(resume, jd, company, role), height=240)
    if st.button("Generate Personalized Application Packet", key="packet"):
        st.write(personalized_application_packet(resume, jd, company, role))
    st.subheader("Interview Prep")
    prep = interview_prep(jd)
    st.write(prep["framework"])
    st.write(prep["questions"])
    st.subheader("Salary Negotiation Tips")
    st.write(salary_negotiation_tips(role))

with tab4:
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Add Application"):
            st.write(add_application(company, role, "applied"))
    with c2:
        if st.button("Mark Interview"):
            st.write("Updated" if update_application(company, role, "interview") else "No matching application found")
    with c3:
        st.metric("Application->Interview %", application_to_interview_rate())
    st.subheader("Conversion Improvement Projection")
    st.write(conversion_improvement_report(target_lift=40.0))
    st.subheader("Application Tracker")
    st.write(list_applications())
    st.subheader("Job Seeker Success Stories")
    st.write(success_stories())
    st.caption("ScaleDown target: up to 80% JD compression and fast matching across 100+ job postings.")
