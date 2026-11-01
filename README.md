<<<<<<< HEAD
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
=======
# CineScope

CineScope is a Flask-based movie discovery and box-office analysis website. It
provides movie browsing across Tollywood, Bollywood, and Hollywood, with search,
recommendations, movie details, and visualizations for box-office and ROI data.

## Features

- Browse movies by industry and category, and search by title.
- View movie details and recommendations.
- Explore box-office figures and ROI visualizations, and export data as CSV.
- Run in offline demo mode without an API key.
- Optionally request current movie metadata from TMDB when TMDB credentials are
  configured.

## Technologies

- Python and Flask
- HTML, CSS, and JavaScript
- TMDB API for optional live movie metadata
- Gunicorn for the included hosting configuration

## Project structure

```text
.
├── webapp.py                  # Flask application and API routes
├── requirements-web.txt       # Python dependencies
├── templates/
│   └── index.html              # Website page
├── static/
│   ├── app.js                  # Front-end behavior
│   └── styles.css              # Website styles
├── OFFLINE_DATASET_INFO.txt    # Offline catalogue notes
├── WEB_DEPLOY_GUIDE.md         # Optional live-data and hosting notes
├── Procfile                    # Gunicorn start command
└── render.yaml                 # Render service configuration
```

## Run locally on Windows

Install Python 3.10 or newer. In Command Prompt, change to the project folder
and create and activate a virtual environment:

```bat
py -m venv .venv
.venv\Scripts\activate
```

Install the dependencies and start the website:

```bat
py -m pip install -r requirements-web.txt
py webapp.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser. Keep the
terminal open while using the website; press `Ctrl+C` there to stop the server.

The app works without TMDB credentials using the bundled offline demo data.
To enable optional live metadata, configure `TMDB_BEARER_TOKEN` or
`TMDB_API_KEY` in a local `.env` file. Never commit `.env` or share its
credentials. The committed `.env.example` contains placeholders only.

## Offline data and limitations

The offline catalogue contains 45 curated demonstration movie records across
the three industry categories. It is a small, static sample rather than a
comprehensive or automatically updated database. Some ratings, posters, budget,
and revenue fields are unavailable in the bundled records.

Any illustrative or synthetic financial figures used in offline charts and
ROI examples are demo data, **not verified real-world box-office figures**.
They should not be used as factual financial results. When TMDB is configured,
its metadata may also be incomplete and is not an audited box-office source.

## Additional documentation

- [Offline dataset notes](OFFLINE_DATASET_INFO.txt)
- [Website and hosting guide](WEB_DEPLOY_GUIDE.md)
- [Submission checklist](SUBMISSION_CHECKLIST.md)
>>>>>>> origin/main
