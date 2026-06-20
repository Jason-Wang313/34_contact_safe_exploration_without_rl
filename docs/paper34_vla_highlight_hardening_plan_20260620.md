# Paper34 VLA Highlight Hardening Plan

Date: 2026-06-20

## Objective

Make `C:/Users/wangz/Downloads/34.pdf` match the visible VLA-v4 role model's PDF link-box behavior without changing the paper's scientific content:

- internal equation/table/figure links should render as red one-point boxes;
- citation and URL links should render as green one-point boxes when those link types exist;
- no cyan URL boxes should appear;
- the canonical build should leave only the Downloads PDF and no local `main.pdf`.

## Plan-Start Evidence

Baseline artifact:

- Canonical PDF: `C:/Users/wangz/Downloads/34.pdf`
- Pages: 25
- Size: 301,379 bytes
- SHA256: `9243DFAC7F540DE2EED48E9FAFA89318B23030224572AE6912EC952EDCA19548`
- Local `main.pdf`: absent
- Repository state: clean against `origin/master`

Baseline link inventory from the current Downloads PDF:

- Link pages: `[]`
- Annotation colors: none
- Borders: none

Source finding:

- `main.tex` is a single-root manuscript at repository root.
- The preamble loads `url` but does not load `hyperref`, so the existing cross-references are not clickable and cannot show VLA-style boxes.
- The manuscript contains five internal `\ref` commands: `tab:scale`, `tab:main`, `tab:regime`, `tab:family`, and `tab:stress`.
- No `\cite`, `\citep`, `\citet`, `\url`, or `\href` commands are present in `main.tex`; green cite/url boxes should be configured but not forced by adding cosmetic links.

## Role-Model Target

Install the same explicit hyperref policy as the visible VLA-v4 role model:

```tex
\usepackage{hyperref}
\hypersetup{
  colorlinks=false,
  pdfborder={0 0 1},
  citebordercolor={0 1 0},
  linkbordercolor={1 0 0},
  urlbordercolor={0 1 0}
}
```

## Execution Plan

1. Add `hyperref` and the role-model `\hypersetup` before `\usepackage{url}` in `main.tex`.
2. Rebuild with `scripts/build_pdf.ps1`, which copies the final PDF to Downloads and removes local `main.pdf`.
3. Recompute page count, SHA256, annotation colors, border widths, and link pages from the rebuilt PDF.
4. Render the new link pages into `tmp/pdfs/paper34_after`.
5. Visually inspect every affected page:
   - red boxes appear around table references and match the VLA role model's one-point outline style;
   - green cite/url boxes are configured but absent unless actual cite/url annotations exist;
   - no cyan boxes appear;
   - layout, figures, tables, headers, and page count remain stable.
6. Update README/status/audit/version/validation metadata with the new hash and visual-hardening result.
7. Scan LaTeX logs for fatal errors, undefined references, rerun warnings, and overfull boxes.
8. Remove Paper34 temp renders, leaving only the shared role-model render directory.
9. Stage only Paper34 source and metadata files, commit, push, and verify a clean repository.

## Non-Goals

- Do not add fake citations, URLs, or content merely to create green boxes.
- Do not alter experiment results, claims, figures, tables, or page count.
- Do not leave intermediate PDFs or render folders behind.

## Final QA Result

- Final PDF: `C:/Users/wangz/Downloads/34.pdf`
- Pages: 25
- Size: 346,308 bytes
- SHA256: `1209B26370B1118689B8D53DFC6BCDC9B1A278E00C8B9877289D58A3C289E232`
- Link pages: `[(4, 2), (5, 1), (6, 1), (7, 1)]`
- Annotation colors: red = 5, green = 0, cyan = 0
- Border widths: `(0, 0, 1)` for all 5 link annotations
- Visual QA: link pages rendered from the rebuilt Downloads PDF and inspected. Red boxes are crisp and aligned; no layout drift or cyan boxes appear. Green cite/url boxes are configured by policy but absent because the manuscript has no cite/url link annotations.
- Local `main.pdf`: absent after canonical build
