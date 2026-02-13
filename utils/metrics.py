
def precision_recall(matched, actual):
    tp=len(set(matched)&set(actual))
    p=tp/max(len(matched),1)
    r=tp/max(len(actual),1)
    f=2*p*r/max(p+r,0.01)
    return round(p,2), round(r,2), round(f,2)
