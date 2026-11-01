# CineScope deployment notes

1. Install dependencies: `pip install -r requirements-web.txt`.
2. Download/import the dataset before deployment: `python scripts/download_dataset.py`.
3. The resulting `data/movies.sqlite3` is intentionally excluded from Git because it is a large generated data asset. Provide it to the host through a release asset, object storage, or a host build step with sufficient disk and build time.
4. Start command: `gunicorn webapp:app`.
5. Serve over HTTPS for PWA installation.

Do not commit `.env`, credentials, or the raw 500+ MB source CSV. Verify dataset licensing and host storage limits before public deployment.
