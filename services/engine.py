
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import re, logging
try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config import WEIGHTS, SKILLS, DOMAIN_CORE

logging.basicConfig(level=logging.INFO)
model = None

def _get_model():
    global model
    if model is not None:
        return model
    if SentenceTransformer is None:
        return None
    try:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        return model
    except Exception as e:
        logging.warning("SentenceTransformer unavailable, using keyword fallback: %s", e)
        return None

def extract(t):
    t=t.lower()
    return [s for s in SKILLS if s in t]

def years(text):
    m=re.findall(r"(\d+)\s*year",text.lower())
    return int(m[0]) if m else 0

def sections(text):
    sec=["experience","education","skills","project"]
    c=sum([1 for s in sec if s in text.lower()])
    return c/len(sec)

def stuffing_penalty(text):
    words=text.lower().split()
    rep=max([words.count(w) for w in set(words)])
    return 0.9 if rep>15 else 1.0

def domain_bonus(jd, matched):
    for d,keys in DOMAIN_CORE.items():
        if any(k in jd.lower() for k in keys):
            c=len(set(keys)&set(matched))
            return 1 + (c*0.05)
    return 1

def semantic(a,b):
    m = _get_model()
    if m is None:
        return keyword(a, b)
    ea=m.encode([a]); eb=m.encode([b])
    return float(cosine_similarity(ea,eb)[0][0])

def keyword(a,b):
    v=TfidfVectorizer().fit([a,b])
    return float(cosine_similarity(v.transform([a]),v.transform([b]))[0][0])

def ats(resume,jd):
    try:
        r=set(extract(resume)); j=set(extract(jd))
        skill=len(r&j)/max(len(j),1)

        exp=min(years(resume)/5,1)
        sec=sections(resume)

        base=(WEIGHTS['semantic']*semantic(resume,jd)+
              WEIGHTS['keyword']*keyword(resume,jd)+
              WEIGHTS['skill']*skill+
              WEIGHTS['experience']*exp+
              WEIGHTS['section']*sec)

        final = base * stuffing_penalty(resume) * domain_bonus(jd,r&j)

        return {
          "score": round(min(final*100,99),2),
          "missing": list(j-r),
          "matched": list(r&j)
        }
    except Exception as e:
        logging.error(e)
        return {"score":0,"missing":[],"matched":[]}

def match_corpus(resume,folder):
    out=[]
    for f in os.listdir(folder):
        jd=open(os.path.join(folder,f)).read()
        a=ats(resume,jd)
        out.append({"file":f,"score":a["score"],"missing":a["missing"]})
    return sorted(out,key=lambda x:x["score"],reverse=True)
