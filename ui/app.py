
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from services.engine import ats, match_corpus
from services.interview import questions
from services.rewrite import improve
from utils.validate import check

st.set_page_config(layout="wide")
st.title("Advanced Career Assistant")

resume=st.text_area("Resume Text")
jd=st.text_area("Job Description")

msg=check(resume,jd)
if msg!="ok":
    st.warning(msg)

if st.button("Analyze"):
    a=ats(resume,jd)
    st.metric("ATS Score",a['score'])
    st.write("Missing Skills",a['missing'])
    st.write("Matched Skills",a['matched'])

    st.subheader("Auto Improvement")
    st.text_area("Improved",improve(resume,a['missing']),height=200)

if st.button("Corpus Match"):
    st.write(match_corpus(resume,"corpus"))

st.subheader("Interview Prep")
if st.button("Generate"):
    st.write(questions(jd))
