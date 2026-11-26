# Health Authority Watch: run 2026-11-26T23:14Z

Classifier: `rules` · items tracked: 256

## Source health

| Source | Authority | Items | Time (s) | Status |
|---|---|---|---|---|
| fda_recalls | US FDA | 100 | 0.2 | OK |
| fda_medwatch | US FDA | 0 | 0.2 | FAIL (collect failed: https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/medwatch/rss.xml: HTTP 401; only 0 items (min 5)) x1 |
| mhra_govuk | UK MHRA | 50 | 0.4 | OK |
| aemps_es | Spain AEMPS | 30 | 1.2 | OK |
| cdsco_notices | India CDSCO | 0 | 62.3 | FAIL (collect failed: TimeoutError: Page.goto: Timeout 60000ms exceeded.
Call log:
  - navigating to "https://cdsco.gov.in/opencms/opencms/en/Notifications/Public-Notices/", waiting until "networkidle"
; only 0 items (min 5)) x17 |

## New and revised (5)

| Severity | Relevance | Status | Authority | Title (English) | Why |
|---|---|---|---|---|---|
| 2 | medium | revised | UK MHRA | [Apply for the AI in Mental Health Airlock](https://www.gov.uk/government/publications/apply-for-the-ai-in-mental-health-airlock) | keyword rule |
| 2 | medium | new | UK MHRA | [MHRA Safety Roundup: November 2026](https://www.gov.uk/drug-device-alerts/mhra-safety-roundup-november-2026) | keyword rule |
| 2 | medium | new | UK MHRA | [MHRA authorises obicetrapib and ezetimibe for adults with high cholesterol when current treatments are insufficient](https://www.gov.uk/government/news/mhra-authorises-obicetrapib-and-ezetimibe-for-adults-with-high-cholesterol-when-current-treatments-are-insufficient) | keyword rule |
| 2 | medium | new | Spain AEMPS | [La AEMPS informa de la retirada de un lote del medicamento veterinario Camdolor 20mg/ml solución inyectable para bovino, porcino y caballos](https://www.aemps.gob.es/informa/la-aemps-informa-de-la-retirada-de-un-lote-del-medicamento-veterinario-camdolor-20mg-ml-solucion-inyectable-para-bovino-porcino-y-caballos/) | keyword rule |
| 2 | medium | new | Spain AEMPS | [CAMDOLOR 20 MG/ML SOLUCION INYECTABLE PARA BOVINO PORCINO Y CABALLOS (3841 ESP)](https://www.aemps.gob.es/informa/camdolor-20-mg-ml-solucion-inyectable-para-bovino-porcino-y-caballos-3841-esp/) | keyword rule |
