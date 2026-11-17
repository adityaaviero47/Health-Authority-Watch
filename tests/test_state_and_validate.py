import sys, pathlib, copy
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from hawatch.collectors import parse_openfda
from hawatch.items import Item
from hawatch import state as st
from hawatch.validate import check

F = ROOT / "tests" / "fixtures"
SRC = {"id": "fda", "authority": "US FDA", "language": "en", "min_items": 2}


def items():
    return parse_openfda((F / "openfda.json").read_text(), SRC)


def test_first_run_is_baseline_not_new():
    s = {}
    out = st.diff(items(), s, "t0", baseline=True)
    assert {x[0] for x in out} == {st.UNCHANGED} and len(s) == 3


def test_new_revised_unchanged():
    s = {}; st.diff(items(), s, "t0", baseline=True)
    nxt = items()
    nxt[2].watch["status"] = "Terminated"                    # recall status changed -> revised
    nxt.append(Item("fda", "US FDA", "en", "https://x", "Class II recall: new product", extra={"native_id": "D-0200-2026"}))
    out = {it.item_id: status for status, it in st.diff(nxt, s, "t1")}
    assert out["fda:D-0103-2026"] == st.REVISED and out["fda:D-0200-2026"] == st.NEW
    assert out["fda:D-0101-2026"] == st.UNCHANGED and s["fda:D-0103-2026"]["revisions"] == 1


def test_cosmetic_whitespace_is_not_a_revision():
    s = {}; st.diff(items(), s, "t0", baseline=True)
    nxt = items(); nxt[0].summary = "  Lack of   Assurance​ of Sterility "
    assert dict((i.item_id, x) for x, i in st.diff(nxt, s, "t1"))["fda:D-0101-2026"] == st.UNCHANGED


def test_validation_flags_problems():
    good = check(SRC, items())
    assert good["ok"]
    bad = check({**SRC, "min_items": 5}, items()[:1] + items()[:1])
    assert not bad["ok"] and any("only 2 items" in p for p in bad["problems"]) and any("duplicate" in p for p in bad["problems"])
    undated = [Item("fda", "US FDA", "en", "https://x/1", "A long enough title"), Item("fda", "US FDA", "en", "https://x/2", "Another long title")]
    assert any("carry a date" in p for p in check(SRC, undated)["problems"])
    assert not check(SRC, [], error="HTTP 503")["ok"]
