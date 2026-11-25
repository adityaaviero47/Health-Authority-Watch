# Health Authority Watch: run 2026-11-25T11:39Z

Classifier: `rules` · items tracked: 246

## Source health

| Source | Authority | Items | Time (s) | Status |
|---|---|---|---|---|
| fda_recalls | US FDA | 100 | 0.5 | OK |
| fda_medwatch | US FDA | 0 | 0.0 | FAIL (collect failed: https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/medwatch/rss.xml: HTTP 404; only 0 items (min 5)) x1 |
| mhra_govuk | UK MHRA | 50 | 0.7 | OK |
| aemps_es | Spain AEMPS | 30 | 0.8 | OK |
| cdsco_notices | India CDSCO | 0 | 62.6 | FAIL (collect failed: TimeoutError: Page.goto: Timeout 60000ms exceeded.
Call log:
  - navigating to "https://cdsco.gov.in/opencms/opencms/en/Notifications/Public-Notices/", waiting until "networkidle"
; only 0 items (min 5)) x14 |

## New and revised (14)

| Severity | Relevance | Status | Authority | Title (English) | Why |
|---|---|---|---|---|---|
| 1 | high | new | US FDA | [Class II recall: ORL Organic Oral Care Cinnamint toothpaste, 4 oz., ORL, ORL Labs, LLC, Scottsdale, Arizona, USA UPC# 850006245512](https://api.fda.gov/drug/enforcement.json?search=recall_number:"D-0176-2027") | keyword rule |
| 1 | high | new | US FDA | [Class II recall: ORL Organic Oral Care Fresh Mint natural toothpaste, 4 oz., ORL, Manufactured in USA, ORL Labs, LLC, Scottsdale, Arizona, USA, UPC 850006245499](https://api.fda.gov/drug/enforcement.json?search=recall_number:"D-0177-2027") | keyword rule |
| 1 | high | new | US FDA | [Class II recall: ORL Organic Oral Care Fresh mint mouthwash, 16.9 oz., ORL, Manufactured in USA, ORL Labs, LLC, Scottsdale, Arizona, USA, UPC# #850006245451](https://api.fda.gov/drug/enforcement.json?search=recall_number:"D-0180-2027") | keyword rule |
| 1 | high | new | US FDA | [Class II recall: ORL Organic Oral Care Bubblegum Kids Mouthwash, 16.9 oz., ORL, ORL Labs, LLC, Scottsdale, Arizona, USA, UPC# #850006245475](https://api.fda.gov/drug/enforcement.json?search=recall_number:"D-0178-2027") | keyword rule |
| 1 | high | new | US FDA | [Class I recall: UMARY Acido Hialuronico, also known as: "New Hyaluronic Acid 850mg Sealed 30 Caps", Suplemento Alimenticio, Contenido Neto: 30 capletas de 850 mg.](https://api.fda.gov/drug/enforcement.json?search=recall_number:"D-0189-2027") | keyword rule |
| 1 | high | new | US FDA | [Class II recall: Organic Oral Care Cinnamint Kids Mouthwash, 16.9 oz., ORL, ORL Labs, LLC, Scottsdale, Arizona, USA, 16.9 oz. UPC# #850006245468](https://api.fda.gov/drug/enforcement.json?search=recall_number:"D-0179-2027") | keyword rule |
| 1 | high | new | US FDA | [Class II recall: ORL Organic Oral Care Bubblegum Kids natural toothpaste, 4 oz., ORL, Manufactured in USA, ORL LAbs, LLC, Scottsdale, Arizona, USA, UPC# 850006245505](https://api.fda.gov/drug/enforcement.json?search=recall_number:"D-0175-2027") | keyword rule |
| 1 | high | new | US FDA | [Class II recall: Famotidine Injection, 200 mg per 50 mL (4 mg per mL), 1 x 50 mL Multi-Dose Vial, For Intravenous Use, Rx only, Sterile, Mfd. for SAGENT Pharmaceuticals, Schaumb](https://api.fda.gov/drug/enforcement.json?search=recall_number:"D-0185-2027") | keyword rule |
| 1 | high | new | US FDA | [Class II recall: Cyanocobalamin Injection, USP, 1000 mcg/mL, 25 x 1 mL multi-dose vials, Rx only, American Regent INC, Shirley, NY, 11967, NDC 0517-0031-25, (Vial NDC: 0517-0031](https://api.fda.gov/drug/enforcement.json?search=recall_number:"D-0172-2027") | keyword rule |
| 2 | medium | new | UK MHRA | [Complaints procedure - Medicines and Healthcare products Regulatory Agency](https://www.gov.uk/government/organisations/medicines-and-healthcare-products-regulatory-agency/about/complaints-procedure) | keyword rule |
| 2 | medium | new | UK MHRA | [Class 3 Medicines Recall: Mercury Pharmaceuticals Limited, Bexarotene 75 mg soft capsules, EL(26)A/51](https://www.gov.uk/drug-device-alerts/class-3-medicines-recall-mercury-pharmaceuticals-limited-bexarotene-75-mg-soft-capsules-el-26-a-slash-51) | keyword rule |
| 2 | medium | new | UK MHRA | [Guidance on pharmacovigilance procedures](https://www.gov.uk/government/publications/guidance-on-pharmacovigilance-procedures) | keyword rule |
| 2 | medium | new | Spain AEMPS | [La AEMPS actualiza las condiciones de autorización de formatos para dispensación fraccionada de medicamentos veterinarios](https://www.aemps.gob.es/informa/la-aemps-actualiza-las-condiciones-de-autorizacion-de-formatos-para-dispensacion-fraccionada-de-medicamentos-veterinarios/) | keyword rule |
| 3 | low | new | US FDA | [Class II recall: Lisdexamfetamine Dimesylate Capsules 40 mg, 100-count bottle, Rx Only, Manufactured by: Ohm Laboratories, New Brunswick, NJ 08901, Distributed by: Sun Pharmaceu](https://api.fda.gov/drug/enforcement.json?search=recall_number:"D-0174-2027") | keyword rule |
