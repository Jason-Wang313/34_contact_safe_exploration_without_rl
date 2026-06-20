# Reproducibility Checklist

- [x] Legacy simulator is `scripts/recover_paper34.py`.
- [x] Full-scale runner is `scripts/run_full_scale_contact_safe_suite.py`.
- [x] Build script is `scripts/build_pdf.ps1`.
- [x] Legacy outputs are `docs/contact_safe_results.csv`, `docs/contact_discontinuity_stress.csv`, and `docs/contact_discontinuity_stress_table.tex`.
- [x] Full-scale outputs are stored in `results/full_scale/`.
- [x] Full-scale figures are stored in `figures/full_scale/`.
- [x] Paper source is `main.tex`.
- [x] Canonical PDF path is `C:/Users/wangz/Downloads/34.pdf`.
- [x] Final PDF pages: 25.
- [x] Final PDF SHA256: `1209B26370B1118689B8D53DFC6BCDC9B1A278E00C8B9877289D58A3C289E232`.
- [x] Local `main.pdf` is removed after canonical copy.
- [x] Visible Desktop PDF copies are absent.
- [x] Final build status is recorded in `data/build_status.json`.
- [x] Delivered PDF text markers were verified.
- [x] Delivered PDF was rendered with `pdftoppm` and inspected visually.
- [x] VLA-style link-box policy is configured in `main.tex`; final PDF has one-point red internal reference boxes and no cyan boxes.

Recommended verification commands:

```powershell
python scripts\run_full_scale_contact_safe_suite.py
powershell -ExecutionPolicy Bypass -File scripts\build_pdf.ps1
pdfinfo C:\Users\wangz\Downloads\34.pdf
Get-FileHash C:\Users\wangz\Downloads\34.pdf -Algorithm SHA256
```
