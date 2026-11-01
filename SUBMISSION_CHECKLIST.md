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
When `data/movies.sqlite3` is installed, CineScope uses the local 215,288-record catalogue. If it is unavailable, the app clearly falls back to 45 curated sample records. Missing ratings, posters, budgets, and revenue are not invented. Financial analysis uses only source rows with reported budget and revenue.

## Before submission
- Add student name, roll number, class, guide/faculty, and institution details to your report.
- Capture screenshots of the homepage, each industry filter, recommendations, dataset explorer, and box-office analysis.
- Explain ROI: `(Revenue - Budget) / Budget × 100`. Note that this simple ratio excludes marketing, distribution shares, taxes, and other costs.
- Describe the current offline version honestly: it does not fetch new titles automatically.

## Render deployment verification

- [ ] Confirm the Render service is Free and its Root Directory is blank.
- [ ] Confirm the build command is `pip install -r requirements-web.txt` and the start command binds Gunicorn to `$PORT`.
- [ ] Confirm `/health` returns HTTP 200 without querying SQLite.
- [ ] If deploying the full dataset, configure a private HTTPS artifact URL and use the build step in `WEB_DEPLOY_GUIDE.md`; do not commit the database.
- [ ] Confirm `/api/status` reports the expected dataset record count after deployment.


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
