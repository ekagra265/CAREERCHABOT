
ACTION=["Developed","Implemented","Designed","Automated","Analyzed"]

def improve(resume, missing):
    lines="\n# AI Suggested Bullets\n"
    for s in missing:
        lines+=f"- {ACTION[0]} projects using {s} to solve business problems.\n"
    return resume+lines
