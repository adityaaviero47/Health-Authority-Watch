import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from hawatch.collectors import parse_openfda, parse_govuk, parse_rss, parse_html_links, iso, CollectError
import pytest

F = ROOT / "tests" / "fixtures"
S = lambda **k: {"id": "t", "authority": "Test", "language": "en", "url": "https://cdsco.gov.in/opencms/opencms/en/Notifications/Public-Notices/", **k}


def test_openfda_fields_and_identity():
    items = parse_openfda((F / "openfda.json").read_text(), S())
    assert len(items) == 3
    assert items[0].item_id == "t:D-0101-2026" and items[0].published == "2026-11-04"
    assert items[0].extra["fda_class"] == "Class I" and "Sterility" in items[0].summary


def test_govuk_links_are_absolute_and_dated():
    items = parse_govuk((F / "govuk.json").read_text(), S())
    assert items[1].url.startswith("https://www.gov.uk/drug-device-alerts/")
    assert items[0].published == "2026-11-12"


def test_spanish_rss_keeps_accents_and_strips_html():
    items = parse_rss((F / "aemps_rss.xml").read_text(encoding="utf-8"), S(language="es"))
    assert items[0].title.startswith("Retirada del mercado") and "Sódico" in items[0].title
    assert "falta de esterilidad" in items[0].summary and "<b>" not in items[0].summary
    assert items[1].published == "2026-11-13"


def test_atom_feed():
    items = parse_rss((F / "atom.xml").read_text(), S())
    assert items[0].url == "https://example.org/guidance/epi" and items[0].updated.startswith("2026-11-15")


def test_bad_feed_raises():
    with pytest.raises(CollectError):
        parse_rss("<html>not a feed", S())


def test_html_list_rows_dates_and_dedup():
    items = parse_html_links((F / "cdsco_list.html").read_text(), S(link_pattern=r"Pdf-documents/.+\.pdf$"))
    assert len(items) == 2                                   # duplicate row dropped, footer link ignored
    assert "Paracetamol" in items[0].title and items[0].published == "2026-11-14"
    assert items[0].url.startswith("https://cdsco.gov.in/opencms/export/")


def test_iso_dates():
    assert iso("20261104") == "2026-11-04" and iso("Mon, 16 Nov 2026 10:00:00 +0000") == "2026-11-16"
    assert iso("2026-11-12T09:30:00.000+00:00") == "2026-11-12" and iso("garbage") == ""
