"""Flask web application for the dataset-powered CineScope Movie Analytics PWA."""
from __future__ import annotations

import os
import csv
import json
import math
import re
import sqlite3
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from threading import Lock
from datetime import date, timedelta
from typing import Any

import requests
from flask import Flask, jsonify, render_template, request, make_response, send_from_directory
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"), static_folder=os.path.join(BASE_DIR, "static"))
app.config["JSON_SORT_KEYS"] = False
TRAKT_BASE = "https://api.trakt.tv"
TRAKT_API_VERSION = "2"

# Keep the demo useful when someone opens it before setting an API credential.
# These records intentionally contain no box-office figures or numeric ratings.
# Live metadata and audience ratings are supplied by Trakt; unavailable fields remain blank.
OFFLINE_MOVIES: list[dict[str, Any]] = [
    {"id": "demo-1", "title": "RRR", "original_title": "RRR", "original_language": "te", "industry": "Tollywood", "release_date": "2022-03-24", "genre_names": ["Action", "Drama"], "overview": "Two legendary revolutionaries and their journey away from home before they began fighting for their country.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-2", "title": "Baahubali 2: The Conclusion", "original_title": "Baahubali 2: The Conclusion", "original_language": "te", "industry": "Tollywood", "release_date": "2017-04-28", "genre_names": ["Action", "Fantasy"], "overview": "Shiva learns about his heritage and the events that led to the fall of the Mahishmati kingdom.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-3", "title": "Pushpa: The Rise", "original_title": "Pushpa: The Rise", "original_language": "te", "industry": "Tollywood", "release_date": "2021-12-17", "genre_names": ["Action", "Crime"], "overview": "A labourer rises through the ranks of a red sandalwood smuggling syndicate.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-4", "title": "Sita Ramam", "original_title": "Sita Ramam", "original_language": "te", "industry": "Tollywood", "release_date": "2022-08-05", "genre_names": ["Romance", "Drama"], "overview": "A letter from a woman brings an orphaned army officer into a moving search across time.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-5", "title": "Kalki 2898 AD", "original_title": "Kalki 2898 AD", "original_language": "te", "industry": "Tollywood", "release_date": "2024-06-27", "genre_names": ["Science Fiction", "Action"], "overview": "In a distant future, a group of people become connected to a prophesied child.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-6", "title": "Dangal", "original_title": "Dangal", "original_language": "hi", "industry": "Bollywood", "release_date": "2016-12-21", "genre_names": ["Drama", "Family"], "overview": "A former wrestler trains his daughters to become competitive wrestlers.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-7", "title": "3 Idiots", "original_title": "3 Idiots", "original_language": "hi", "industry": "Bollywood", "release_date": "2009-12-25", "genre_names": ["Comedy", "Drama"], "overview": "Three engineering students challenge college traditions and rethink success.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-8", "title": "Jawan", "original_title": "Jawan", "original_language": "hi", "industry": "Bollywood", "release_date": "2023-09-07", "genre_names": ["Action", "Thriller"], "overview": "A man driven by a personal vendetta sets out to correct social wrongs.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-9", "title": "Laapataa Ladies", "original_title": "Laapataa Ladies", "original_language": "hi", "industry": "Bollywood", "release_date": "2024-03-01", "genre_names": ["Comedy", "Drama"], "overview": "Two young brides are accidentally swapped during a train journey in rural India.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-10", "title": "12th Fail", "original_title": "12th Fail", "original_language": "hi", "industry": "Bollywood", "release_date": "2023-10-27", "genre_names": ["Drama"], "overview": "A small-town student attempts to overcome setbacks while preparing for a civil service exam.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-11", "title": "The Dark Knight", "original_title": "The Dark Knight", "original_language": "en", "industry": "Hollywood", "release_date": "2008-07-18", "genre_names": ["Action", "Crime", "Drama"], "overview": "Batman faces a criminal mastermind who throws Gotham into chaos.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-12", "title": "Interstellar", "original_title": "Interstellar", "original_language": "en", "industry": "Hollywood", "release_date": "2014-11-07", "genre_names": ["Science Fiction", "Drama"], "overview": "A group of explorers travels beyond this galaxy to secure humanity's future.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-13", "title": "Inception", "original_title": "Inception", "original_language": "en", "industry": "Hollywood", "release_date": "2010-07-16", "genre_names": ["Science Fiction", "Action"], "overview": "A specialist enters dreams to plant an idea inside a target's mind.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-14", "title": "Oppenheimer", "original_title": "Oppenheimer", "original_language": "en", "industry": "Hollywood", "release_date": "2023-07-21", "genre_names": ["Drama", "History"], "overview": "The story of the scientist who led the development of the atomic bomb.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-15", "title": "Dune: Part Two", "original_title": "Dune: Part Two", "original_language": "en", "industry": "Hollywood", "release_date": "2024-03-01", "genre_names": ["Science Fiction", "Adventure"], "overview": "Paul Atreides unites with Chani and the Fremen while seeking revenge.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-16", "title": "Ala Vaikunthapurramuloo", "original_title": "Ala Vaikunthapurramuloo", "original_language": "te", "industry": "Tollywood", "release_date": "2020-01-12", "genre_names": ["Action", "Comedy"], "overview": "A man discovers the truth about his birth and family.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-17", "title": "Arjun Reddy", "original_title": "Arjun Reddy", "original_language": "te", "industry": "Tollywood", "release_date": "2017-08-25", "genre_names": ["Drama", "Romance"], "overview": "A talented surgeon struggles with anger and heartbreak.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-18", "title": "Jersey", "original_title": "Jersey", "original_language": "te", "industry": "Tollywood", "release_date": "2019-04-19", "genre_names": ["Drama", "Sport"], "overview": "A former cricketer attempts a comeback for his son.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-19", "title": "Eega", "original_title": "Eega", "original_language": "te", "industry": "Tollywood", "release_date": "2012-07-06", "genre_names": ["Fantasy", "Action"], "overview": "A murdered man is reincarnated as a housefly to seek revenge.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-20", "title": "Magadheera", "original_title": "Magadheera", "original_language": "te", "industry": "Tollywood", "release_date": "2009-07-31", "genre_names": ["Action", "Fantasy"], "overview": "A modern romance connects to a warrior story from a past life.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-21", "title": "Rangasthalam", "original_title": "Rangasthalam", "original_language": "te", "industry": "Tollywood", "release_date": "2018-03-30", "genre_names": ["Drama", "Action"], "overview": "A partially deaf man challenges a powerful village leader.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-22", "title": "Hanu-Man", "original_title": "Hanu-Man", "original_language": "te", "industry": "Tollywood", "release_date": "2024-01-12", "genre_names": ["Fantasy", "Action"], "overview": "A young man gains extraordinary powers and protects his village.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-23", "title": "Devara: Part 1", "original_title": "Devara: Part 1", "original_language": "te", "industry": "Tollywood", "release_date": "2024-09-27", "genre_names": ["Action", "Drama"], "overview": "A coastal community faces a dangerous conflict.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-24", "title": "Pokiri", "original_title": "Pokiri", "original_language": "te", "industry": "Tollywood", "release_date": "2006-04-28", "genre_names": ["Action", "Thriller"], "overview": "A ruthless criminal becomes entangled with law enforcement.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-25", "title": "Mahanati", "original_title": "Mahanati", "original_language": "te", "industry": "Tollywood", "release_date": "2018-05-09", "genre_names": ["Biography", "Drama"], "overview": "A biographical story of celebrated actor Savitri.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-26", "title": "Sholay", "original_title": "Sholay", "original_language": "hi", "industry": "Bollywood", "release_date": "1975-08-15", "genre_names": ["Action", "Adventure"], "overview": "Two criminals are hired to help a village resist a bandit.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-27", "title": "Lagaan", "original_title": "Lagaan", "original_language": "hi", "industry": "Bollywood", "release_date": "2001-06-15", "genre_names": ["Drama", "Sport"], "overview": "Villagers challenge colonial officers to a cricket match.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-28", "title": "Queen", "original_title": "Queen", "original_language": "hi", "industry": "Bollywood", "release_date": "2014-03-07", "genre_names": ["Comedy", "Drama"], "overview": "A young woman takes a solo trip after her wedding is called off.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-29", "title": "Zindagi Na Milegi Dobara", "original_title": "Zindagi Na Milegi Dobara", "original_language": "hi", "industry": "Bollywood", "release_date": "2011-07-15", "genre_names": ["Comedy", "Drama"], "overview": "Three friends take a road trip through Spain.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-30", "title": "PK", "original_title": "PK", "original_language": "hi", "industry": "Bollywood", "release_date": "2014-12-19", "genre_names": ["Comedy", "Drama"], "overview": "An alien questions social customs while searching for a lost device.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-31", "title": "Andhadhun", "original_title": "Andhadhun", "original_language": "hi", "industry": "Bollywood", "release_date": "2018-10-05", "genre_names": ["Thriller", "Crime"], "overview": "A pianist becomes entangled in a murder mystery.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-32", "title": "Gully Boy", "original_title": "Gully Boy", "original_language": "hi", "industry": "Bollywood", "release_date": "2019-02-14", "genre_names": ["Drama", "Music"], "overview": "A Mumbai street rapper pursues his musical ambitions.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-33", "title": "Swades", "original_title": "Swades", "original_language": "hi", "industry": "Bollywood", "release_date": "2004-12-17", "genre_names": ["Drama"], "overview": "An Indian scientist returns to his village and reconsiders his priorities.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-34", "title": "Taare Zameen Par", "original_title": "Taare Zameen Par", "original_language": "hi", "industry": "Bollywood", "release_date": "2007-12-21", "genre_names": ["Drama", "Family"], "overview": "An art teacher helps a child who struggles in school.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-35", "title": "Chak De! India", "original_title": "Chak De! India", "original_language": "hi", "industry": "Bollywood", "release_date": "2007-08-10", "genre_names": ["Drama", "Sport"], "overview": "A former hockey player coaches the Indian womens national team.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-36", "title": "The Shawshank Redemption", "original_title": "The Shawshank Redemption", "original_language": "en", "industry": "Hollywood", "release_date": "1994-09-23", "genre_names": ["Drama"], "overview": "Two imprisoned men form a lasting friendship.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-37", "title": "The Matrix", "original_title": "The Matrix", "original_language": "en", "industry": "Hollywood", "release_date": "1999-03-31", "genre_names": ["Science Fiction", "Action"], "overview": "A hacker discovers that reality is not what it seems.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-38", "title": "Titanic", "original_title": "Titanic", "original_language": "en", "industry": "Hollywood", "release_date": "1997-12-19", "genre_names": ["Romance", "Drama"], "overview": "A romance unfolds aboard a doomed ocean liner.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-39", "title": "Avatar", "original_title": "Avatar", "original_language": "en", "industry": "Hollywood", "release_date": "2009-12-18", "genre_names": ["Science Fiction", "Adventure"], "overview": "A former marine becomes involved in a conflict on an alien moon.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-40", "title": "Jurassic Park", "original_title": "Jurassic Park", "original_language": "en", "industry": "Hollywood", "release_date": "1993-06-11", "genre_names": ["Adventure", "Science Fiction"], "overview": "Scientists visit a theme park populated by cloned dinosaurs.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-41", "title": "Forrest Gump", "original_title": "Forrest Gump", "original_language": "en", "industry": "Hollywood", "release_date": "1994-07-06", "genre_names": ["Drama", "Romance"], "overview": "A kind-hearted man witnesses key moments in American history.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-42", "title": "The Avengers", "original_title": "The Avengers", "original_language": "en", "industry": "Hollywood", "release_date": "2012-05-04", "genre_names": ["Action", "Science Fiction"], "overview": "Earths mightiest heroes unite against a global threat.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-43", "title": "Spider-Man: Across the Spider-Verse", "original_title": "Spider-Man: Across the Spider-Verse", "original_language": "en", "industry": "Hollywood", "release_date": "2023-06-02", "genre_names": ["Animation", "Action"], "overview": "Miles Morales encounters a team of spider-powered heroes.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-44", "title": "The Lord of the Rings: The Fellowship of the Ring", "original_title": "The Lord of the Rings: The Fellowship of the Ring", "original_language": "en", "industry": "Hollywood", "release_date": "2001-12-19", "genre_names": ["Fantasy", "Adventure"], "overview": "A hobbit begins a dangerous journey to destroy a powerful ring.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
    {"id": "demo-45", "title": "Barbie", "original_title": "Barbie", "original_language": "en", "industry": "Hollywood", "release_date": "2023-07-21", "genre_names": ["Comedy", "Fantasy"], "overview": "Barbie journeys from her idealized world into the real world.", "vote_average": None, "poster_path": None, "backdrop_path": None, "budget": None, "revenue": None},
]

_cache: dict[str, tuple[float, Any]] = {}
_cache_lock = Lock()
CACHE_TTL = 600  # ten minutes; users can force refresh with ?refresh=1


def live_configured() -> bool:
    return bool(os.getenv("TRAKT_CLIENT_ID", "").strip())


def cached(key: str, loader, refresh: bool = False):
    now = time.time()
    with _cache_lock:
        found = _cache.get(key)
        if not refresh and found and found[0] > now:
            return found[1]
    value = loader()
    with _cache_lock:
        _cache[key] = (now + CACHE_TTL, value)
    return value


def trakt_get(path: str, params: dict[str, Any] | None = None) -> Any:
    client_id = os.getenv("TRAKT_CLIENT_ID", "").strip()
    if not client_id:
        raise RuntimeError("Trakt Client ID is not configured. Add TRAKT_CLIENT_ID to your .env file.")
    headers = {"Content-Type": "application/json", "trakt-api-version": TRAKT_API_VERSION, "trakt-api-key": client_id}
    response = requests.get(f"{TRAKT_BASE}{path}", params=params or {}, headers=headers, timeout=15)
    if response.status_code == 401:
        raise RuntimeError("Trakt rejected the Client ID. Check TRAKT_CLIENT_ID in your .env file.")
    if response.status_code == 429:
        raise RuntimeError("Trakt API rate limit reached. Please wait and try again.")
    response.raise_for_status()
    return response.json()


def classify_industry(language: str, country: str | None = None) -> str:
    if language == "te": return "Tollywood"
    if language == "hi": return "Bollywood"
    if language == "en" and (not country or country == "us"): return "Hollywood"
    return "International"


def normalize_trakt(item: dict[str, Any], industry: str | None = None) -> dict[str, Any]:
    # Trakt list endpoints wrap movie data in {movie, watchers/...}.
    movie = item.get("movie") if isinstance(item.get("movie"), dict) else item
    ids = movie.get("ids") or {}
    language = movie.get("language") or ""
    label = industry.title() if industry and industry != "all" else classify_industry(language)
    rating = movie.get("rating")
    votes = movie.get("votes")
    released = movie.get("released") or ""
    genres = movie.get("genres") or []
    return {
        "id": ids.get("trakt") or movie.get("title"), "trakt_id": ids.get("trakt"),
        "imdb_id": ids.get("imdb"), "imdb_url": f"https://www.imdb.com/title/{ids.get('imdb')}/" if ids.get("imdb") else None,
        "title": movie.get("title") or "Untitled", "original_title": movie.get("title") or "",
        "original_language": language, "industry": label, "release_date": released,
        "year": movie.get("year") or (released[:4] if released else "—"),
        "genre_names": [str(g).replace("-", " ").title() for g in genres],
        "overview": movie.get("overview") or "Synopsis is not available from Trakt.",
        "vote_average": rating, "vote_count": votes, "rating_source": "Trakt",
        "runtime": movie.get("runtime"), "certification": movie.get("certification"),
        "poster_url": None, "poster_path": None, "backdrop_url": None,
        "budget": None, "revenue": None, "tagline": "", "source": "Trakt API"
    }


def trakt_list_endpoint(category: str) -> str:
    return {"popular": "/movies/popular", "now-playing": "/movies/trending", "top-rated": "/movies/popular", "upcoming": "/movies/anticipated"}.get(category, "/movies/popular")


def industry_filter(movies: list[dict[str, Any]], industry: str) -> list[dict[str, Any]]:
    if industry == "all": return movies
    wanted = {"tollywood": "te", "bollywood": "hi", "hollywood": "en"}.get(industry)
    return [m for m in movies if m.get("original_language") == wanted]


def offline_movies(industry: str, category: str, query: str = "") -> list[dict[str, Any]]:
    movies = OFFLINE_MOVIES[:]
    if industry != "all":
        movies = [m for m in movies if m["industry"].lower() == industry]
    q = query.strip().lower()
    if q:
        movies = [m for m in movies if q in m["title"].lower() or q in m["overview"].lower() or any(q in g.lower() for g in m["genre_names"])]
    # Keep the local fallback meaningful when categories are selected, without inventing fresh API data.
    if category == "top-rated":
        movies = sorted(movies, key=lambda m: m["title"])
    return movies


DATASET_FILE = os.environ.get("CINESCOPE_DATASET_PATH", "").strip() or os.path.join(
    BASE_DIR, "data", "movies.sqlite3"
)
PAGE_SIZE = 40
RECOMMENDATION_LIMIT = 12
RECOMMENDATION_CANDIDATE_LIMIT = 6000
TOKEN_PATTERN = re.compile(r"[a-z0-9]{2,}")
TEXT_STOP_WORDS = {
    "about", "after", "again", "against", "also", "and", "are", "because",
    "been", "before", "being", "between", "but", "came", "can", "come",
    "could", "did", "does", "during", "each", "for", "from", "get", "got",
    "had", "has", "have", "her", "here", "him", "his", "how", "into", "its",
    "just", "like", "made", "make", "many", "more", "most", "much", "must",
    "not", "now", "off", "once", "only", "other", "our", "out", "over",
    "same", "see", "should", "since", "some", "such", "than", "that", "the",
    "their", "them", "then", "there", "these", "they", "this", "those",
    "through", "time", "too", "under", "use", "very", "was", "way", "well",
    "were", "what", "when", "where", "which", "while", "who", "will", "with",
    "would", "you", "your",
}
KNOWN_INDUSTRY_LANGUAGES = (
    "te", "hi", "en", "ta", "ml", "kn", "bn", "mr", "ja", "ko", "fr", "es", "zh",
)


def dataset_industry(language: str) -> str:
    code = (language or "").strip().lower()
    return {"te": "Tollywood", "hi": "Bollywood", "en": "Hollywood", "ta": "Kollywood", "ml": "Mollywood", "kn": "Sandalwood", "bn": "Bengali Cinema", "mr": "Marathi Cinema", "ja": "Japanese Cinema", "ko": "Korean Cinema", "fr": "French Cinema", "es": "Spanish Cinema", "zh": "Chinese Cinema"}.get(code, "International")


def db_connection():
    if not os.path.isfile(DATASET_FILE): return None
    conn = sqlite3.connect(f"file:{DATASET_FILE}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def movie_from_row(row):
    if row is None: return None
    item = dict(row)
    item["industry"] = dataset_industry(item.get("original_language"))
    item["genre_names"] = [g.strip() for g in (item.pop("genres", "") or "").split(",") if g.strip()]
    poster = item.pop("poster_path", "") or ""
    item["poster_url"] = ("https://image.tmdb.org/t/p/w500" + poster) if poster.startswith("/") else (poster or None)
    item["backdrop_url"] = item.pop("backdrop_path", None)
    item["source"] = "Downloaded TMDB movie dataset"
    item["live"] = True
    item["imdb_url"] = f"https://www.imdb.com/title/{item['imdb_id']}/" if item.get("imdb_id") else None
    return item


def industry_sql(industry):
    return {"tollywood": "te", "bollywood": "hi", "hollywood": "en", "kollywood": "ta", "mollywood": "ml", "sandalwood": "kn"}.get(industry)


def _recommendation_genres(movie: dict[str, Any]) -> set[str]:
    genres = movie.get("genre_names")
    if genres is None:
        genres = (movie.get("genres") or "").split(",")
    if isinstance(genres, str):
        genres = genres.split(",")
    return {str(genre).strip().casefold() for genre in genres if str(genre).strip()}


def _recommendation_tokens(overview: str | None) -> Counter:
    return Counter(
        token for token in TOKEN_PATTERN.findall((overview or "").casefold())
        if token not in TEXT_STOP_WORDS
    )


def _overview_similarities(source: dict[str, Any], candidates: list[dict[str, Any]]) -> dict[str, float]:
    source_tokens = _recommendation_tokens(source.get("overview"))
    candidate_tokens = {
        str(candidate.get("id")): _recommendation_tokens(candidate.get("overview"))
        for candidate in candidates
    }
    document_frequency = Counter()
    for tokens in candidate_tokens.values():
        document_frequency.update(tokens.keys())
    document_frequency.update(source_tokens.keys())

    document_count = len(candidates) + 1
    inverse_document_frequency = {
        token: math.log((document_count + 1) / (frequency + 1)) + 1
        for token, frequency in document_frequency.items()
    }

    def weighted_vector(tokens: Counter) -> tuple[dict[str, float], float]:
        vector = {
            token: (1 + math.log(count)) * inverse_document_frequency[token]
            for token, count in tokens.items()
            if token in inverse_document_frequency
        }
        norm = math.sqrt(sum(weight * weight for weight in vector.values()))
        return vector, norm

    source_vector, source_norm = weighted_vector(source_tokens)
    if not source_norm:
        return {movie_id: 0.0 for movie_id in candidate_tokens}

    similarities = {}
    for movie_id, tokens in candidate_tokens.items():
        vector, norm = weighted_vector(tokens)
        if not norm:
            similarities[movie_id] = 0.0
            continue
        dot_product = sum(
            weight * vector.get(token, 0.0)
            for token, weight in source_vector.items()
        )
        similarities[movie_id] = max(0.0, min(1.0, dot_product / (source_norm * norm)))
    return similarities


def _recommendation_quality(movie: dict[str, Any]) -> float:
    signals = []
    try:
        rating = float(movie.get("vote_average") or 0)
        if rating > 0:
            signals.append(min(rating / 10.0, 1.0))
    except (TypeError, ValueError):
        pass
    try:
        popularity = float(movie.get("popularity") or 0)
        if popularity > 0:
            signals.append(min(math.log1p(popularity) / math.log(101), 1.0))
    except (TypeError, ValueError):
        pass
    return sum(signals) / len(signals) if signals else 0.0


def _rank_recommendations(
    source: dict[str, Any], candidates: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    source_genres = _recommendation_genres(source)
    source_language = str(source.get("original_language") or "").strip().casefold()
    source_industry = dataset_industry(source_language) if source_language else ""
    text_scores = _overview_similarities(source, candidates)
    source_title = re.sub(r"[^\w]+", " ", str(source.get("title") or "").casefold()).strip()
    ranked = []
    seen_titles = {source_title} if source_title else set()

    for movie in candidates:
        title = str(movie.get("title") or "").strip()
        title_key = re.sub(r"[^\w]+", " ", title.casefold()).strip()
        if not title_key or title_key in seen_titles:
            continue
        seen_titles.add(title_key)

        movie_genres = _recommendation_genres(movie)
        union = source_genres | movie_genres
        genre_score = len(source_genres & movie_genres) / len(union) if union else 0.0
        language = str(movie.get("original_language") or "").strip().casefold()
        language_score = float(bool(source_language and language and source_language == language))
        industry = dataset_industry(language) if language else ""
        industry_score = float(bool(source_industry and industry and source_industry == industry))
        overview_score = text_scores.get(str(movie.get("id")), 0.0)
        quality_score = _recommendation_quality(movie)
        score = (
            0.45 * genre_score
            + 0.25 * overview_score
            + 0.15 * language_score
            + 0.10 * industry_score
            + 0.05 * quality_score
        )
        ranked.append((
            score, genre_score, overview_score, quality_score, title.casefold(),
            str(movie.get("id") or ""), movie,
        ))

    ranked.sort(key=lambda result: (
        -result[0], -result[1], -result[2], -result[3], result[4], result[5],
    ))
    return [result[-1] for result in ranked[:RECOMMENDATION_LIMIT]]


@lru_cache(maxsize=128)
def _recommendations_for(movie_id: str, dataset_mtime_ns: int) -> dict[str, Any]:
    conn = db_connection()
    if conn:
        try:
            source_row = conn.execute("SELECT * FROM movies WHERE id = ?", (movie_id,)).fetchone()
            if source_row:
                source = dict(source_row)
                genres = sorted(_recommendation_genres(source))
                language = str(source.get("original_language") or "").strip().casefold()
                genre_expression = "instr(',' || replace(lower(coalesce(genres,'')), ', ', ',') || ',', ',' || ? || ',') > 0"
                genre_select = " + ".join(f"(CASE WHEN {genre_expression} THEN 1 ELSE 0 END)" for _ in genres) or "0"
                language_condition = ""
                language_args: list[str] = []
                if language and dataset_industry(language) == "International":
                    language_condition = (
                        "lower(coalesce(original_language,'')) NOT IN "
                        f"({','.join('?' for _ in KNOWN_INDUSTRY_LANGUAGES)}) "
                        "AND trim(coalesce(original_language,'')) <> ''"
                    )
                    language_args.extend(KNOWN_INDUSTRY_LANGUAGES)
                elif language:
                    language_condition = "lower(coalesce(original_language,'')) = ?"
                    language_args.append(language)

                where_parts = []
                where_args: list[Any] = []
                if genres:
                    where_parts.append("(" + " OR ".join(genre_expression for _ in genres) + ")")
                    where_args.extend(genres)
                if language_condition:
                    where_parts.append(f"({language_condition})")
                    where_args.extend(language_args)

                if where_parts:
                    sql = (
                        f"SELECT *, ({genre_select}) AS recommendation_genre_hits "
                        "FROM movies WHERE id <> ? AND (" + " OR ".join(where_parts) + ") "
                        "ORDER BY recommendation_genre_hits DESC, "
                        "CASE WHEN lower(coalesce(original_language,'')) = ? THEN 1 ELSE 0 END DESC, "
                        "coalesce(popularity, 0) DESC LIMIT ?"
                    )
                    args = genres + [movie_id] + where_args + [language, RECOMMENDATION_CANDIDATE_LIMIT]
                    candidates = [dict(row) for row in conn.execute(sql, args).fetchall()]
                    results = _rank_recommendations(source, candidates)
                    for movie in results:
                        movie.pop("recommendation_genre_hits", None)
                    return {
                        "results": [movie_from_row(movie) for movie in results],
                        "live": True,
                        "message": (
                            "No suitable matches were found for this movie in the local dataset."
                            if not results else ""
                        ),
                    }
        finally:
            conn.close()

    source = next((movie for movie in OFFLINE_MOVIES if str(movie["id"]) == movie_id), None)
    if source:
        candidates = [movie for movie in OFFLINE_MOVIES if str(movie["id"]) != movie_id]
        results = _rank_recommendations(source, candidates)
        return {
            "results": [
                {**movie, "year": (movie.get("release_date") or "")[:4], "live": False}
                for movie in results
            ],
            "live": False,
            "message": (
                "No suitable matches were found among the offline sample movies."
                if not results else ""
            ),
        }
    return {"results": [], "live": False, "message": "Movie not found in the local dataset."}


@app.route("/")
def home():
    return render_template("index.html")


@app.get("/service-worker.js")
def service_worker():
    response = make_response(send_from_directory(os.path.join(BASE_DIR, "static"), "service-worker.js", mimetype="application/javascript"))
    response.headers["Service-Worker-Allowed"] = "/"
    response.headers["Cache-Control"] = "no-cache"
    return response


@app.route("/robots.txt")
def robots():
    sitemap_url = f"{request.url_root.rstrip('/')}/sitemap.xml"
    response = make_response(f"User-agent: *\nAllow: /\nSitemap: {sitemap_url}\n")
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    return response


@app.route("/sitemap.xml")
def sitemap():
    public_root = request.url_root.rstrip("/")
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{public_root}/</loc><changefreq>daily</changefreq><priority>1.0</priority></url></urlset>'''
    response = make_response(xml)
    response.headers["Content-Type"] = "application/xml; charset=utf-8"
    return response


@app.get("/api/status")
def api_status():
    conn = db_connection()
    count = conn.execute("SELECT COUNT(*) FROM movies").fetchone()[0] if conn else 0
    if conn: conn.close()
    return jsonify({"live": bool(count), "provider": "Local SQLite dataset", "dataset_records": count,
        "message": f"Local movie dataset loaded: {count:,} records." if count else "Dataset not installed yet. Run py scripts/download_dataset.py.",
        "attribution": "See DATASET_SOURCES.md for source, licence and update notes."})


@app.get("/api/movies")
def api_movies():
    industry = request.args.get("industry", "all").lower()
    category = request.args.get("category", "popular").lower()
    query = request.args.get("q", "")[:100].strip()
    page = max(1, request.args.get("page", 1, type=int))
    if category not in {"popular", "now-playing", "top-rated", "upcoming"}:
        return jsonify({"error": "Unknown category."}), 400
    conn = db_connection()
    if not conn:
        fallback = offline_movies(industry, category, query)
        return jsonify({"results": fallback, "total_results": len(fallback), "page": 1, "total_pages": 1, "live": False, "notice": "Dataset is not installed. Run py scripts/download_dataset.py."})
    where=[]; args=[]
    lang=industry_sql(industry)
    if lang: where.append("original_language = ?"); args.append(lang)
    elif industry not in ("all", "international"):
        where.append("1 = 0")
    if industry == "international": where.append("original_language NOT IN ('te','hi','en','ta','ml','kn','bn','mr','ja','ko','fr','es','zh')")
    if query:
        where.append("(LOWER(title) LIKE ? OR LOWER(original_title) LIKE ? OR LOWER(overview) LIKE ? OR LOWER(genres) LIKE ?)")
        pattern=f"%{query.lower()}%"; args.extend([pattern]*4)
    today=date.today().isoformat()
    if category == "upcoming": where.append("release_date > ?"); args.append(today)
    elif category == "now-playing": where.append("release_date >= ?"); args.append(f"{date.today().year}-01-01")
    clause=" WHERE "+" AND ".join(where) if where else ""
    total=conn.execute("SELECT COUNT(*) FROM movies"+clause,args).fetchone()[0]
    order="vote_average DESC, vote_count DESC" if category=="top-rated" else "release_date DESC" if category in ("now-playing","upcoming") else "popularity DESC, vote_count DESC"
    rows=conn.execute(f"SELECT * FROM movies{clause} ORDER BY {order} LIMIT ? OFFSET ?",args+[PAGE_SIZE,(page-1)*PAGE_SIZE]).fetchall()
    conn.close()
    total_pages=max(1,(total+PAGE_SIZE-1)//PAGE_SIZE)
    return jsonify({"results":[movie_from_row(r) for r in rows],"total_results":total,"page":page,"total_pages":total_pages,"live":True,
        "notice":f"Showing {total:,} matching records from the local movie dataset. Browsing does not call a movie API."})


@app.get("/api/movie/<movie_id>")
def api_movie_detail(movie_id: str):
    conn=db_connection()
    if conn:
        row=conn.execute("SELECT * FROM movies WHERE id = ?",(movie_id,)).fetchone(); conn.close()
        movie=movie_from_row(row)
        if movie:
            movie["rating_label"]="Dataset audience rating"
            movie["box_office_note"]="Budget and revenue are shown only when supplied in the source dataset."
            return jsonify(movie)
    found=next((m for m in OFFLINE_MOVIES if str(m["id"])==movie_id),None)
    if found: return jsonify({**found,"year":found.get("release_date","")[:4],"live":False})
    return jsonify({"error":"Movie not found in the installed dataset."}),404


@app.get("/api/movie/<movie_id>/recommendations")
def api_recommendations(movie_id: str):
    dataset_mtime_ns = os.stat(DATASET_FILE).st_mtime_ns if os.path.isfile(DATASET_FILE) else 0
    response = _recommendations_for(movie_id, dataset_mtime_ns)
    if response["message"] == "Movie not found in the local dataset.":
        return jsonify({**response, "error": response["message"]}), 404
    return jsonify(response)


@app.get("/api/box-office")
def api_box_office():
    conn=db_connection()
    if not conn: return jsonify({"results":[],"live":False,"notice":"Install the local dataset to enable box-office analysis."})
    total=conn.execute("SELECT COUNT(*) FROM movies WHERE budget > 0 AND revenue > 0").fetchone()[0]
    rows=conn.execute("SELECT * FROM movies WHERE budget > 0 AND revenue > 0 ORDER BY revenue DESC LIMIT 100").fetchall()
    conn.close(); results=[]
    for row in rows:
        item=movie_from_row(row); item["profit"]=item["revenue"]-item["budget"]
        item["roi"]=round(item["profit"]/item["budget"]*100,2) if item["budget"] else None
        results.append(item)
    return jsonify({"results":results,"live":bool(total),"total_financial_records":total,
        "notice":f"{total:,} records contain both budget and revenue. Values are source-reported; currency may vary and should be normalized before comparisons."})


@app.get("/health")
def health():
    return jsonify({"ok": True})


@app.errorhandler(500)
def internal_server_error(_error):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Internal server error"}), 500
    return "Internal server error", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
