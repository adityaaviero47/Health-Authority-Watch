# Health Authority Watch: run 2026-11-24T12:51Z

Classifier: `rules` · items tracked: 225

## Source health

| Source | Authority | Items | Time (s) | Status |
|---|---|---|---|---|
| fda_recalls | US FDA | 100 | 0.1 | OK |
| fda_medwatch | US FDA | 20 | 0.1 | OK |
| mhra_govuk | UK MHRA | 50 | 0.3 | OK |
| aemps_es | Spain AEMPS | 30 | 1.1 | OK |
| cdsco_notices | India CDSCO | 0 | 63.6 | FAIL (collect failed: TimeoutError: Page.goto: Timeout 60000ms exceeded.
Call log:
  - navigating to "https://cdsco.gov.in/opencms/opencms/en/Notifications/Public-Notices/", waiting until "networkidle"
; only 0 items (min 5)) x12 |

## New and revised (3)

| Severity | Relevance | Status | Authority | Title (English) | Why |
|---|---|---|---|---|---|
| 2 | medium | new | UK MHRA | [MHRA Performance Data](https://www.gov.uk/government/publications/mhra-performance-data) | keyword rule |
| 2 | medium | new | Spain AEMPS | [La AEMPS informa sobre la actualización de las recomendaciones europeas para la gestión de impurezas de nitrosaminas en medicamentos de uso humano](https://www.aemps.gob.es/informa/la-aemps-informa-sobre-la-actualizacion-de-las-recomendaciones-europeas-para-la-gestion-de-impurezas-de-nitrosaminas-en-medicamentos-de-uso-humano/) | keyword rule |
| 3 | low | new | UK MHRA | [Class 2 Medicines Recall: Quadrant Pharmaceuticals Limited (Parallel Import), Brintellix 5 mg film-coated tablets, EL(26)A/49](https://www.gov.uk/drug-device-alerts/class-2-medicines-recall-quadrant-pharmaceuticals-limited-parallel-import-brintellix-5-mg-film-coated-tablets-el-26-a-slash-49) | keyword rule |
