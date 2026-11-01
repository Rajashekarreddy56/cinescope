# CineScope — Dataset-powered Movie Analytics PWA

CineScope is a Flask-based movie discovery and analytics project for Tollywood, Bollywood, Hollywood and international cinema. It includes local-dataset search, language/industry filters, movie details, genre-based recommendations, box-office analysis when source values exist, CSV export and an installable/offline-capable PWA shell.

## 1. Install the large movie dataset

The primary catalogue is a large downloadable TMDB movie metadata CSV (approximately 524 MB). It is downloaded once and stored locally and imported into indexed SQLite; CineScope does not call a movie API for normal browsing.

```powershell
py -m pip install -r requirements-web.txt
py scripts/download_dataset.py
```

The script builds `data/movies.sqlite3` in batches, avoiding a huge in-memory load. First download may take several minutes and requires internet. The app can then search/filter the local file without an API key. Read `DATASET_SOURCES.md` for source, attribution/licence cautions, update procedure and data-quality notes.

## 2. Run locally

```powershell
py webapp.py
```

Open http://127.0.0.1:5000.

## 3. Dataset refresh

Run `py scripts/download_dataset.py` again when you want to refresh from the upstream downloadable file. Refresh freshness depends on when the upstream publisher updates its file. The dataset is not a real-time feed.

## 4. Features

- Local CSV-backed catalogue and search (no runtime movie API calls)
- Tollywood/Hindi/Hollywood and international language-based grouping
- Popular, top-rated, recently released and upcoming filters
- Offline content-based recommendations ranked by genre Jaccard similarity, overview TF-IDF, language, industry and a small rating/popularity factor
- Box-office analysis only for rows with positive budget and revenue values
- ROI calculation: `(revenue - budget) / budget × 100`
- CSV export and PWA shell/offline caching

## 5. Important limitations

- Language-based industry classification is approximate: language does not always equal film industry.
- Missing budget/revenue/rating values are not invented. Source financial figures may use different currencies; compare only after currency normalization.
- Poster images are hosted remotely and may need internet even when the catalogue itself is local.
- For public/commercial deployment, verify the dataset mirror's current licence and TMDB terms. Keep attribution and source links visible.

## 6. Deploy

For deployment, provide `data/movies.sqlite3` through a release asset or deployment storage (GitHub blocks files over 100 MB) or add a build step that downloads it. Check the host's disk, build-time download and repository size limits before deploying a 500+ MB file. A local install on your PC will work after the download script completes.
