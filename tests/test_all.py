
from services.engine import ats
from utils.validate import check

def test_flow():
    r="python sql 3 year experience project"
    j="need python sql excel"
    assert check(r,j)=="ok"
    a=ats(r,j)
    assert a['score']>=0
