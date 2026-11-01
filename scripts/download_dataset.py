"""Download and install the large TMDB movie metadata CSV for offline CineScope use.

Run from the project root: py scripts/download_dataset.py
The source CSV is large (~524 MB); this script supports HTTP resume when possible.
"""
from pathlib import Path
import os
import shutil
import urllib.request
import csv
import sqlite3
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw"
RAW.mkdir(parents=True, exist_ok=True)
SOURCE_URL = "https://huggingface.co/datasets/ada-datadruids/full_tmdb_movies_dataset/resolve/main/TMDB_movie_dataset_v11.csv"
RAW_FILE = RAW / "TMDB_movie_dataset_v11.csv"
INSTALLED = DATA / "movies.sqlite3"


def download():
    if RAW_FILE.exists() and RAW_FILE.stat().st_size > 100_000_000:
        print(f"Found existing source file ({RAW_FILE.stat().st_size / 1e6:.1f} MB); reusing it.")
        return
    offset = RAW_FILE.stat().st_size if RAW_FILE.exists() else 0
    headers = {"User-Agent": "CineScope-Student-Analytics/2.0"}
    if offset:
        headers["Range"] = f"bytes={offset}-"
    req = urllib.request.Request(SOURCE_URL, headers=headers)
    print("Downloading the large movie catalogue (~524 MB). This may take several minutes...")
    with urllib.request.urlopen(req, timeout=180) as response:
        if offset and response.status != 206:
            offset = 0
        mode = "ab" if offset else "wb"
        with RAW_FILE.open(mode) as out:
            shutil.copyfileobj(response, out, length=1024 * 1024)
    if RAW_FILE.stat().st_size < 100_000_000:
        raise RuntimeError("Download appears incomplete. Check your connection and run this script again.")


def install():
    # Stream the 1M-row CSV into SQLite in batches to avoid loading it all into RAM.
    if INSTALLED.exists(): INSTALLED.unlink()
    conn = sqlite3.connect(INSTALLED)
    conn.execute("""CREATE TABLE movies (
        id TEXT PRIMARY KEY, title TEXT, original_title TEXT, original_language TEXT,
        release_date TEXT, year TEXT, genres TEXT, overview TEXT, vote_average REAL,
        vote_count REAL, popularity REAL, runtime REAL, budget REAL, revenue REAL,
        poster_path TEXT, backdrop_path TEXT, tagline TEXT, imdb_id TEXT
    )""")
    def get(row, *keys):
        for key in keys:
            value = row.get(key)
            if value not in (None, "", "nan", "NaN", "null", "None"):
                return str(value).strip()
        return ""
    def num(value):
        try: return float(value) if value else None
        except (ValueError, TypeError): return None
    batch=[]; count=0
    with RAW_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            title=get(row,"title","Title","original_title")
            if not title: continue
            release=get(row,"release_date","Release_Date")
            genres=get(row,"genres","genre_names","Genre")
            try:
                obj=json.loads(genres) if genres.startswith("[") else None
                if isinstance(obj,list): genres=", ".join(str(x.get("name",x)) if isinstance(x,dict) else str(x) for x in obj)
            except Exception: pass
            movie_id=get(row,"id","tmdb_id","movie_id") or f"row-{count+1}"
            batch.append((movie_id,title,get(row,"original_title") or title,get(row,"original_language").lower(),release,get(row,"year") or release[:4],genres,get(row,"overview"),num(get(row,"vote_average")),num(get(row,"vote_count")),num(get(row,"popularity")),num(get(row,"runtime")),num(get(row,"budget")),num(get(row,"revenue")),get(row,"poster_path"),get(row,"backdrop_path"),get(row,"tagline"),get(row,"imdb_id")))
            if len(batch)>=5000:
                conn.executemany("INSERT OR REPLACE INTO movies VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",batch); conn.commit(); count+=len(batch); batch=[]
                if count % 50000 == 0: print(f"Imported {count:,} movies...")
    if batch: conn.executemany("INSERT OR REPLACE INTO movies VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",batch); count+=len(batch)
    conn.execute("CREATE INDEX idx_movies_language ON movies(original_language)")
    conn.execute("CREATE INDEX idx_movies_release ON movies(release_date)")
    conn.execute("CREATE INDEX idx_movies_popularity ON movies(popularity DESC)")
    conn.execute("CREATE INDEX idx_movies_rating ON movies(vote_average DESC)")
    conn.commit(); conn.close()
    print(f"Installed {count:,} movie records in {INSTALLED} ({INSTALLED.stat().st_size / 1_000_000:.1f} MB)")


if __name__ == "__main__":
    download()
    install()
    print("Done. Restart CineScope; its catalogue, filters, recommendations and available box-office fields now read locally.")
