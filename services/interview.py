def star(q):
    return f"""Q: {q}
Use STAR:
Situation - context
Task - objective
Action - what you did
Result - impact"""


BASE = {
    "python": ["Explain decorators", "List vs tuple"],
    "sql": ["Join types", "Indexing"],
    "machine learning": ["Overfitting", "Bias variance"],
    "java": ["OOP pillars"],
}


def questions(jd):
    q = []
    for k, v in BASE.items():
        if k in jd.lower():
            q += v
    return [star(x) for x in q[:5]]
