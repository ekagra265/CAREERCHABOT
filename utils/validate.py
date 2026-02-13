
def check(resume,jd):
    if len(resume)<30:
        return "Resume too short"
    if len(jd)<20:
        return "JD too short"
    return "ok"
