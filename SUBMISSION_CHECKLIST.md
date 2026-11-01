# CineScope submission checklist

## Run locally
1. Install Python 3.10+ if needed.
2. Open Command Prompt in this folder.
3. Run `py -m pip install -r requirements-web.txt`.
4. Run `py webapp.py`.
5. Open `http://127.0.0.1:5000`. Keep the terminal open.

## Smoke tests
- Homepage: `http://127.0.0.1:5000/`
- Health check: `http://127.0.0.1:5000/health` should return `{"ok":true}`.
- Movie API: `http://127.0.0.1:5000/api/movies?industry=tollywood`
- Box office API: `http://127.0.0.1:5000/api/box-office`
- Test all three industry filters, title search, recommendations, box-office charts, and CSV export.

## Data integrity note
Offline catalogue titles are demonstration records. Ratings and posters are left blank where unavailable. Offline box-office figures are **synthetic illustrative examples only** so the charts and ROI calculations can be demonstrated; do not present them as actual box-office results. For factual financial analysis, replace them with sourced values and record the source/date for each figure.

## Before submission
- Add student name, roll number, class, guide/faculty, and institution details to your report.
- Capture screenshots of the homepage, each industry filter, recommendations, dataset explorer, and box-office analysis.
- Explain ROI: `(Revenue - Budget) / Budget × 100`. Note that this simple ratio excludes marketing, distribution shares, taxes, and other costs.
- Describe the current offline version honestly: it does not fetch new titles automatically.
<<<<<<< HEAD


## PWA verification

- [ ] Deploy on HTTPS (or run on localhost).
- [ ] Open CineScope online once and wait for the default catalogue to load.
- [ ] In browser DevTools → Application, verify the manifest and active service worker.
- [ ] Install CineScope from the browser's install control when offered.
- [ ] Visit a few movie details and recommendations while online so their responses/posters are cached.
- [ ] Switch DevTools Network to Offline and reload; confirm the shell and cached catalogue render.
- [ ] Confirm uncached requests show a clear unavailable state rather than invented content.
- [ ] Restore connectivity and confirm the online indicator returns and data can refresh.
- [ ] Deploy a new version and verify the update prompt activates the waiting worker.
=======
>>>>>>> origin/main
