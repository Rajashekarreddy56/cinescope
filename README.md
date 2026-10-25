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
