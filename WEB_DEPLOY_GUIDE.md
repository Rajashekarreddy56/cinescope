# Deploy CineScope to Render

## Render Web Service settings

The existing `render.yaml` defines a **Free** Python Web Service. Connect the GitHub repository containing this project (the repository root is this folder), then use the Blueprint configuration or enter:

| Setting | Value |
| --- | --- |
| Root Directory | Leave blank |
| Build Command | `pip install -r requirements-web.txt && python scripts/prepare_render_dataset.py` |
| Start Command | `gunicorn --bind 0.0.0.0:$PORT webapp:app` |
| Instance Type | Free |
| Health Check Path | `/health` |

`webapp.py` exports the Flask object as `app`; the explicit `:app` selects it for Gunicorn. The requested shorthand `gunicorn webapp` does not select that object and does not bind to Render's `$PORT`, so use the working command above. Render sets `PORT` for the service. Debug mode is disabled.

The service needs no API credentials for the local catalogue. `TRAKT_CLIENT_ID` in `.env.example` is an optional template value and must never be committed with a real credential. Do not configure unused TMDB credentials.

## Full SQLite catalogue on the Free plan

The local database is `data/movies.sqlite3`. It is 125,554,688 bytes (about 119.74 MiB), exceeds GitHub's 100 MB per-file limit, and is intentionally ignored by Git. The 128,596,378-byte source CSV is also excluded. Do not add either file to Git or assume a Render Free service has persistent disk storage.

The build command downloads the existing database from the public GitHub Release asset at `https://github.com/Rajashekarreddy56/cinescope/releases/download/v1.0/movies.sqlite3`. The helper saves it as `data/movies.sqlite3`, verifies the configured SHA-256, checks SQLite integrity and the expected movie columns, and fails the build on download or validation errors. It skips downloading when a valid database already exists. A mismatched/corrupt existing file is replaced only after a complete download passes verification. No environment variable or credential is needed for this public release.

**Checksum action required:** the SHA-256 supplied for this deployment currently contains 63 hexadecimal characters, not the required 64. The existing database and downloaded Release asset both hash to `e733584b7ee7734ad9cc6aa4cad643e370eb1fc8aefc9a42c8ef637a2d16b1ea`, which does not match the supplied value. The helper deliberately retains the supplied value and stops with a clear error before downloading until the checksum is corrected and verified.

Render Free instances have ephemeral filesystems, not persistent disks. The dataset is therefore downloaded and verified on each fresh build/redeploy; the app does not create an empty database or fall back silently during build. `/health` performs a read-only query and returns HTTP 503 with `database_ready: false` if the database is missing, empty, or unreadable.

After deployment, verify `/health` returns `{"ok":true,"database_ready":true}` and `/api/status` reports `215288` records.

`CINESCOPE_DATASET_PATH` can optionally point both the app and build helper to a different absolute database path. SQLite application connections use read-only mode. The default path is `data/movies.sqlite3`.

## Local checks and operation

From the project root:

```powershell
py -m pip install -r requirements-web.txt
py webapp.py
```

The local source-dataset installer is `py scripts/download_dataset.py`; it downloads the source CSV and builds the SQLite catalogue. Render uses `scripts/prepare_render_dataset.py` to fetch the prebuilt, checksum-pinned Release asset.

The application includes `/robots.txt` and `/sitemap.xml`. After deployment, submit the public sitemap URL in Google Search Console if search indexing is desired; indexing is not immediate or guaranteed. Serve the site over HTTPS for PWA installation.

Never commit `.env`, credentials, signed artifact URLs, or dataset files. Confirm the upstream dataset's current licence and attribution requirements before redistribution.
