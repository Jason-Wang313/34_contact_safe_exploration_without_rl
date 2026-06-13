# Reproducibility Checklist

- [x] Main simulator and recovery script is `scripts/recover_paper34.py`.
- [x] Build script is `scripts/build_pdf.ps1`.
- [x] Main output is `docs/contact_safe_results.csv`.
- [x] V2 outputs are `docs/contact_discontinuity_stress.csv` and `docs/contact_discontinuity_stress_table.tex`.
- [x] Paper source is `main.tex`.
- [x] Canonical PDF path is `C:/Users/wangz/Downloads/34.pdf`.
- [x] Local `main.pdf` is removed after canonical copy.
- [x] Visible Desktop PDF copies are absent.

Recommended verification commands:

```powershell
python scripts\recover_paper34.py --stress-only
powershell -ExecutionPolicy Bypass -File scripts\build_pdf.ps1
```
