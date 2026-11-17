import sys, pathlib, json, shutil
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from hawatch import classify, run as runner
from hawatch.collectors import parse_openfda, CollectError

F = ROOT / "tests" / "fixtures"


def item(t, s=""):
    return {"item_id": "x:1", "title": t, "summary": s, "authority": "A", "language": "en"}


def test_rule_baseline():
    assert classify.rule_classify(item("Heparin", "Lack of Assurance of Sterility"))["severity"] == 1
    assert classify.rule_classify(item("Ibuprofen", "Labeling: incorrect expiration date on carton"))["severity"] == 3
    assert classify.rule_classify(item("Tablets", "Failed impurities specification"))["severity"] == 3


def test_llm_json_is_validated_and_falls_back():
    chunk = [{**item("A"), "item_id": "a"}, {**item("B"), "item_id": "b"}]
    resp = {"candidates": [{"content": {"parts": [{"text": json.dumps([
        {"id": "a", "relevance": "high", "severity": 1, "category": "recall", "english_title": "A", "reason": "sterility"},
        {"id": "b", "relevance": "urgent", "severity": 9}])}]}}]}
    out = classify.parse_llm(resp, chunk)
    assert out[0]["by"] == "llm" and out[0]["severity"] == 1
    assert out[1]["by"] == "rules"                             # invalid values -> baseline


def test_end_to_end_run(tmp_path, monkeypatch):
    for d in ("hawatch", "tests"):
        shutil.copytree(ROOT / d, tmp_path / d)
    (tmp_path / "sources.yaml").write_text(
        "sources:\n  - {id: fda, authority: US FDA, country: US, language: en, kind: openfda, url: x, min_items: 2}\n"
        "  - {id: down, authority: Down, country: XX, language: en, kind: rss, url: y, min_items: 1}\n")
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    data = (F / "openfda.json").read_text()

    def fake(src, debug):
        if src["id"] == "down":
            raise CollectError("HTTP 503")
        return parse_openfda(data, src)
    monkeypatch.setattr(runner, "collect", fake)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert runner.main([]) == 1                                # one source down -> job fails after saving
    health = json.loads((tmp_path / "state" / "health.json").read_text())
    assert health["down"]["fail_streak"] == 1 and health["fda"]["ok"]
    assert "Source health" in (tmp_path / "reports" / "latest.md").read_text()
    assert runner.main([]) == 1
    assert json.loads((tmp_path / "state" / "health.json").read_text())["down"]["fail_streak"] == 2
