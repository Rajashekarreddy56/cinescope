# CineScope Website: run locally and publish online

This Flask website is separate from the Streamlit analysis dashboard. It includes a movie-discovery frontend, Tollywood/Bollywood/Hollywood filters, search, recommendations, dataset export, and a box-office view. The live data layer uses TMDB's API; it does not invent missing ratings, budgets, or revenue.

## 1. Enable live data

1. Create/sign in to a TMDB account at https://www.themoviedb.org/.
2. Open account Settings → API and request developer API access. TMDB documents the process at https://developer.themoviedb.org/docs/authentication-application.
3. Copy the **API Read Access Token** (Bearer token).
4. In the project root, copy `.env.example` to `.env` and replace the placeholder:

   ```dotenv
   TMDB_BEARER_TOKEN=your_actual_api_read_access_token
   ```

   Keep `.env` private; never push the token to GitHub or paste it into a public issue. A TMDB v3 API key can alternatively be provided as `TMDB_API_KEY`.

5. Launch the site with `run_web_windows.bat` (Windows) or manually:

   ```bash
   python -m venv .venv-web
   # Windows: .venv-web\\Scripts\\activate
   # macOS/Linux: source .venv-web/bin/activate
   pip install -r requirements-web.txt
   python webapp.py
   ```

6. Open http://127.0.0.1:5000. The site requests current TMDB metadata and caches successful API responses for ten minutes; use **Refresh data** to bypass the cache.

If you haven't obtained credentials yet, the website still runs with a curated offline sample across Telugu, Hindi and English-language cinema. It clearly labels sample mode, and does not fabricate numerical financial values.

## 2. Publish on the internet (Render)

A local address such as `127.0.0.1:5000` is visible only on your own computer. To open the site from another device or have a search engine discover it, deploy it to a public host.

1. Create a GitHub repository and upload this project folder. Do not upload `.env`; `.gitignore` excludes it.
2. In Render, create a new **Web Service** and connect that repository (or use the included `render.yaml` Blueprint).
3. Use build command `pip install -r requirements-web.txt` and start command `gunicorn webapp:app`.
4. In the host's Environment settings, add `TMDB_BEARER_TOKEN` with your token as a secret; do not commit credentials in code.
5. Deploy. Render gives the service a public `onrender.com` URL. Open that URL and test search, industry filters, details, recommendations, and box-office tab.

Official reference: https://render.com/docs/deploy-flask

## 3. Make it show up when people search Google

Deployment creates a public URL; it does **not** instantly guarantee that the site appears in Google results. This project includes a title, description, Open Graph tags, `/robots.txt`, and `/sitemap.xml`. After deployment:

1. Replace absolute sitemap URLs with your final public domain if you later add a custom domain (the current sitemap returns a relative root URL for host independence; Google Search Console may require a full absolute sitemap URL).
2. Add the public URL to Google Search Console and verify ownership.
3. Submit the sitemap, inspect the home page URL, and request indexing. Indexing can take time and is not guaranteed.

Google guide: https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap

## Data and academic accuracy

- “Real-time” here means the website fetches current movie metadata from TMDB when requested, with a ten-minute application cache. It is not a real-time cinema ticket-sales feed.
- Industry labels are inferred mainly from original language: Telugu → Tollywood, Hindi → Bollywood, English + US origin → Hollywood. This is a useful project filter, not an authoritative industry-credit database; dubbed releases and co-productions can cross these categories.
- TMDB budget/revenue values may be missing, incomplete, expressed in USD, and are not audited box-office returns. ROI is calculated as `(revenue - budget) / budget * 100`; it excludes marketing, distribution, taxes and other costs.
- The site contains the required attribution: “This product uses the TMDB API but is not endorsed or certified by TMDB.” See TMDB's API documentation and terms before public/commercial use.
