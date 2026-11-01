# Deploy CineScope to Render

## Render Web Service settings

The existing `render.yaml` defines a **Free** Python Web Service. Connect the GitHub repository containing this project (the repository root is this folder), then use the Blueprint configuration or enter:

| Setting | Value |
| --- | --- |
| Root Directory | Leave blank |
| Build Command | `pip install -r requirements-web.txt` |
| Start Command | `gunicorn --bind 0.0.0.0:$PORT webapp:app` |
| Instance Type | Free |
| Health Check Path | `/health` |

`webapp.py` exports the Flask object as `app`; the explicit `:app` selects it for Gunicorn. The requested shorthand `gunicorn webapp` does not select that object and does not bind to Render's `$PORT`, so use the working command above. Render sets `PORT` for the service. Debug mode is disabled.

The service needs no API credentials for the local catalogue. `TRAKT_CLIENT_ID` in `.env.example` is an optional template value and must never be committed with a real credential. Do not configure unused TMDB credentials.

## Full SQLite catalogue on the Free plan

The local database is `data/movies.sqlite3`. It is 125,554,688 bytes (about 119.74 MiB), exceeds GitHub's 100 MB per-file limit, and is intentionally ignored by Git. The 128,596,378-byte source CSV is also excluded. Do not add either file to Git or assume a Render Free service has persistent disk storage.

Without a separately supplied database, Render can start the app and answer health checks, but the catalogue APIs use the built-in offline sample rather than the 215,288-record catalogue. To deploy the actual dataset:

1. Put the existing `movies.sqlite3` file in private object storage or another trusted HTTPS artifact store. Do not regenerate or replace it with sample records. Ensure the provider allows the Render build to download the file.
2. In Render's Environment settings, add `CINESCOPE_DATASET_URL` as a secret containing a valid HTTPS download URL (a short-lived signed URL is suitable). Never put the URL or its access token in Git.
3. Keep the Render **Build Command** as `pip install -r requirements-web.txt` for a sample-data deployment. To package the real dataset into each deployment, change it to:

   ```sh
   pip install -r requirements-web.txt && python scripts/prepare_render_dataset.py
   ```

   The helper downloads to `data/movies.sqlite3`, validates SQLite integrity and the `movies` table, and installs atomically. It refuses to overwrite an existing dataset and does not log the signed URL. It uses only Python's standard library.
4. Deploy and verify `/health`, `/api/status` (`dataset_records` should be `215288` for this snapshot), and movie search. The build downloads the artifact again on future deployments. Runtime-written files on a Free instance are ephemeral; do not rely on them surviving restarts or redeploys.

`CINESCOPE_DATASET_PATH` can optionally point the app to a different absolute database path. SQLite connections use read-only mode. The normal local database path remains `data/movies.sqlite3`.

## Local checks and operation

From the project root:

```powershell
py -m pip install -r requirements-web.txt
py webapp.py
```

The local dataset installer is `py scripts/download_dataset.py`; it downloads the source CSV and builds the SQLite catalogue. Do not run that installer on Render when deploying a prebuilt SQLite artifact.

The application includes `/robots.txt` and `/sitemap.xml`. After deployment, submit the public sitemap URL in Google Search Console if search indexing is desired; indexing is not immediate or guaranteed. Serve the site over HTTPS for PWA installation.

Never commit `.env`, credentials, signed artifact URLs, or dataset files. Confirm the upstream dataset's current licence and attribution requirements before redistribution.
