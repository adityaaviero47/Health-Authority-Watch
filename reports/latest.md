# Health Authority Watch: run 2026-11-25T23:15Z

Classifier: `rules` · items tracked: 250

## Source health

| Source | Authority | Items | Time (s) | Status |
|---|---|---|---|---|
| fda_recalls | US FDA | 100 | 0.4 | OK |
| fda_medwatch | US FDA | 20 | 0.2 | OK |
| mhra_govuk | UK MHRA | 50 | 0.3 | OK |
| aemps_es | Spain AEMPS | 30 | 1.5 | OK |
| cdsco_notices | India CDSCO | 0 | 60.9 | FAIL (collect failed: TimeoutError: Page.goto: Timeout 60000ms exceeded.
Call log:
  - navigating to "https://cdsco.gov.in/opencms/opencms/en/Notifications/Public-Notices/", waiting until "networkidle"
; only 0 items (min 5)) x15 |

## New and revised (4)

| Severity | Relevance | Status | Authority | Title (English) | Why |
|---|---|---|---|---|---|
| 1 | high | new | US FDA | [Breathing Systems Recall: Intersurgical Inc. Removes 22mm Smoothbore Breathing Tubes and Systems](http://www.fda.gov/medical-devices/medical-device-recalls-and-early-alerts/breathing-systems-recall-intersurgical-inc-removes-22mm-smoothbore-breathing-tubes-and-systems) | keyword rule |
| 2 | medium | new | US FDA | [Insulin Pump Recall: Tandem Diabetes Removes Tandem Mobi Insulin Pumps](http://www.fda.gov/medical-devices/medical-device-recalls-and-early-alerts/insulin-pump-recall-tandem-diabetes-removes-tandem-mobi-insulin-pumps) | keyword rule |
| 2 | medium | new | US FDA | [Early Alert: ICU Medical Removes Portex Endotracheal Tubes](http://www.fda.gov/medical-devices/medical-device-recalls-and-early-alerts/early-alert-icu-medical-removes-portex-endotracheal-tubes) | keyword rule |
| 3 | low | new | UK MHRA | [Class 4 Medicines Defect Notification: Takeda UK Limited, PROSTAP PD DCS 1.88 mg powder and solvent for prolonged-release suspension for injection in pre-filled syringe, EL(26)A/52](https://www.gov.uk/drug-device-alerts/class-4-medicines-defect-notification-takeda-uk-limited-prostap-pd-dcs-1-dot-88-mg-powder-and-solvent-for-prolonged-release-suspension-for-injection-in-pre-filled-syringe-el-26-a-slash-52) | keyword rule |
