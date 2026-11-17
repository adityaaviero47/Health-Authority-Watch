# Health Authority Watch

![ci](https://github.com/adityaaviero47/Health-Authority-Watch/actions/workflows/ci.yml/badge.svg)
![monitor](https://github.com/adityaaviero47/Health-Authority-Watch/actions/workflows/monitor.yml/badge.svg)

A small regulatory-intelligence monitor. Twice a day it:
- collects new publications from 5 health-authority sources, in English and Spanish;
- detects which items are **new** and which were **revised**;
- uses an LLM to rate each change for relevance and severity, with a reason;
- publishes a report with a health check for every source.

| Source | Authority | How it's collected |
|---|---|---|
| `fda_recalls` | US FDA | openFDA drug enforcement **JSON API** |
| `fda_medwatch` | US FDA | MedWatch safety alerts **RSS** |
| `mhra_govuk` | UK MHRA | GOV.UK search **JSON API** |
| `aemps_es` | Spain AEMPS | **Spanish-language** RSS |
| `cdsco_notices` | India CDSCO | **headless-browser (Playwright)** render of the notices page, plus a generic link extractor |

## How it works
```
sources.yaml ──> collect (retries + backoff) ──> validate ──> diff vs state ──> classify changes ──> report + health
                     │ failing page saved to debug/                 new / revised / unchanged       LLM (with reasons), keyword fallback
```
- **Collection** (`hawatch/collectors.py`): one parser per source type (JSON API, RSS/Atom, HTML list page). All network calls go through `fetch()`, which retries with exponential backoff. Pages that need JavaScript are loaded in headless Chromium. When an HTML source returns too few items, the raw page is saved as a run artifact so the extractor can be fixed.
- **Change detection** (`hawatch/state.py`): every item gets a stable id (the source's own id, such as the recall number, or a cleaned-up URL) and a hash of its content. Text is Unicode-normalised and whitespace-collapsed before hashing, so cosmetic edits don't count as revisions. A source's **first run is a baseline**, so adding a source doesn't flood the report with its whole back catalogue. Later runs flag **new** and **revised** items. For FDA recalls, a revision means the recall status, class or termination date changed.
- **Validation** (`hawatch/validate.py`): the same checks gate onboarding a new source and every scheduled run:
  - a minimum item count;
  - usable titles and URLs;
  - at least 50% of items dated;
  - no duplicate ids.

  A failing source turns the scheduled job red, so GitHub emails the owner. A `fail_streak` counter tracks repeat failures.
- **Classification** (`hawatch/classify.py`): Gemini gets 20 items per call and must return strict JSON with relevance, severity 1–3, category, an English title and a one-line reason. Any malformed or out-of-range answer falls back to the keyword baseline for that item, so a bad model reply can't corrupt the report.
- **Evaluation** (`eval/evaluate.py`): severity is scored against FDA's own recall classes (Class I/II/III) on recalls from the last 365 days, with an equal sample per class and the class hidden from the model. It reports accuracy, macro-F1, recall per class and a confusion matrix, for both the LLM and the keyword baseline.

## Run it
```bash
pip install -r requirements.txt && python -m playwright install chromium
python -m hawatch --validate-only     # onboarding check for every source
python -m hawatch                     # full run: writes reports/latest.md, state/state.json, state/health.json
GEMINI_API_KEY=... python eval/evaluate.py --per-class 50
python -m pytest -q                   # 14 tests on saved sample responses
```
On GitHub, the `monitor` workflow runs at 08:00 and 20:00 IST, and `evaluate` runs on demand. Both read the key from the `GEMINI_API_KEY` repository secret.

## Results
See `reports/latest.md` (latest run), `state/health.json` (source health) and `eval/results.json` (accuracy).

## Limits
- There are 5 sources so far. The HTML extractor is generic: it picks notice links by pattern, not by a page-specific selector.
- Severity is tested only on FDA recalls, because that's where official labels exist. Other sources are checked by reading the report.
- The keyword baseline is deliberately simple. It's the bar the LLM has to beat, not a production rule set.
