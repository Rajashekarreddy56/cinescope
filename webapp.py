"""Flask web application for the Movie Recommendation & Box Office Analyzer.

Live movie metadata comes from TMDB when TMDB_BEARER_TOKEN or TMDB_API_KEY is set.
Without credentials, the app runs in clearly labelled offline demo mode.
"""
from __future__ import annotations

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from datetime import date, timedelta
from typing import Any

import requests
from flask import Flask, jsonify, render_template, request, make_response
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"), static_folder=os.path.join(BASE_DIR, "static"))
app.config["JSON_SORT_KEYS"] = False
TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMAGE = "https://image.tmdb.org/t/p/w500"

# Keep the demo useful when someone opens it before setting an API credential.
# These records intentionally contain no box-office figures or numeric ratings.
# Live titles, ratings, posters and available financial metadata are supplied by TMDB.
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
    return bool(os.getenv("TMDB_BEARER_TOKEN", "").strip() or os.getenv("TMDB_API_KEY", "").strip())


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


def tmdb_get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    token = os.getenv("TMDB_BEARER_TOKEN", "").strip()
    api_key = os.getenv("TMDB_API_KEY", "").strip()
    if not token and not api_key:
        raise RuntimeError("TMDB credentials are not configured")
    query = dict(params or {})
    if api_key and not token:
        query["api_key"] = api_key
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.get(f"{TMDB_BASE}{path}", params=query, headers=headers, timeout=12)
    if response.status_code == 401:
        raise RuntimeError("TMDB rejected the credential. Check TMDB_BEARER_TOKEN or TMDB_API_KEY.")
    response.raise_for_status()
    return response.json()


def industry_params(industry: str) -> dict[str, Any]:
    industry = industry.lower()
    if industry == "tollywood":
        return {"with_original_language": "te", "region": "IN"}
    if industry == "bollywood":
        return {"with_original_language": "hi", "region": "IN"}
    if industry == "hollywood":
        return {"with_original_language": "en", "with_origin_country": "US", "region": "US"}
    if industry == "all":
        return {"region": "IN"}
    raise ValueError("Unknown industry")


def discover_params(industry: str, category: str, page: int = 1) -> dict[str, Any]:
    params: dict[str, Any] = {
        "language": "en-US",
        "include_adult": "false",
        "include_video": "false",
        "page": max(1, min(int(page), 500)),
        **industry_params(industry),
    }
    today = date.today()
    if category == "top-rated":
        params.update({"sort_by": "vote_average.desc", "vote_count.gte": 100})
    elif category == "now-playing":
        params.update({"sort_by": "popularity.desc", "primary_release_date.gte": (today - timedelta(days=120)).isoformat(), "primary_release_date.lte": today.isoformat()})
    elif category == "upcoming":
        params.update({"sort_by": "popularity.desc", "primary_release_date.gte": today.isoformat(), "primary_release_date.lte": (today + timedelta(days=180)).isoformat()})
    else:
        params.update({"sort_by": "popularity.desc"})
    return params


def genre_map() -> dict[int, str]:
    # Stable TMDB genre IDs, used only if the discover response has no genre_names.
    return {28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy", 80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family", 14: "Fantasy", 36: "History", 27: "Horror", 10402: "Music", 9648: "Mystery", 10749: "Romance", 878: "Science Fiction", 10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"}


def normalize_movie(item: dict[str, Any], industry: str | None = None) -> dict[str, Any]:
    language = item.get("original_language") or ""
    if industry and industry != "all":
        label = industry.title()
    elif language == "te":
        label = "Tollywood"
    elif language == "hi":
        label = "Bollywood"
    elif language == "en" and "US" in (item.get("origin_country") or ["US"]):
        label = "Hollywood"
    else:
        label = "International"
    genres = item.get("genres")
    if isinstance(genres, list) and genres and isinstance(genres[0], dict):
        genre_names = [g.get("name", "") for g in genres if g.get("name")]
    else:
        mapping = genre_map()
        genre_names = [mapping.get(g, "") for g in (item.get("genre_ids") or [])]
        genre_names = [g for g in genre_names if g]
    release_date = item.get("release_date") or ""
    return {
        "id": item.get("id"),
        "title": item.get("title") or item.get("name") or "Untitled",
        "original_title": item.get("original_title") or item.get("title") or "",
        "original_language": language,
        "industry": label,
        "release_date": release_date,
        "year": release_date[:4] if len(release_date) >= 4 else "—",
        "genre_names": genre_names,
        "overview": item.get("overview") or "Synopsis is not available from the data source.",
        "vote_average": item.get("vote_average"),
        "vote_count": item.get("vote_count"),
        "poster_path": item.get("poster_path"),
        "poster_url": f"{TMDB_IMAGE}{item.get('poster_path')}" if item.get("poster_path") else None,
        "backdrop_url": f"https://image.tmdb.org/t/p/w1280{item.get('backdrop_path')}" if item.get("backdrop_path") else None,
        "budget": item.get("budget"),
        "revenue": item.get("revenue"),
        "runtime": item.get("runtime"),
        "status": item.get("status"),
        "tagline": item.get("tagline") or "",
        "source": "TMDB live API" if live_configured() else "Offline sample dataset",
    }


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


@app.route("/")
def home():
    return render_template("index.html")


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
    configured = live_configured()
    return jsonify({"live": configured, "provider": "The Movie Database (TMDB)", "cache_ttl_seconds": CACHE_TTL,
                    "message": "Live metadata is enabled." if configured else "Offline sample mode. Add TMDB_BEARER_TOKEN or TMDB_API_KEY to load live movies, posters and available box-office metadata.",
                    "attribution": "This product uses the TMDB API but is not endorsed or certified by TMDB."})


@app.get("/api/movies")
def api_movies():
    industry = request.args.get("industry", "all").lower()
    category = request.args.get("category", "popular").lower()
    query = request.args.get("q", "")[:100]
    page = request.args.get("page", "1")
    refresh = request.args.get("refresh", "0") == "1"
    if industry not in {"all", "tollywood", "bollywood", "hollywood"}:
        return jsonify({"error": "Industry must be all, tollywood, bollywood or hollywood."}), 400
    if category not in {"popular", "now-playing", "top-rated", "upcoming"}:
        return jsonify({"error": "Unknown category."}), 400
    if not live_configured():
        movies = offline_movies(industry, category, query)
        return jsonify({"results": movies, "total_results": len(movies), "page": 1, "total_pages": 1, "live": False, "notice": "Offline sample dataset: titles are examples; live ratings, posters and financial figures require a TMDB credential."})
    try:
        def load():
            if query.strip():
                params = {"query": query.strip(), "language": "en-US", "include_adult": "false", "page": page}
                # Filter search results locally after the query; language classification is made from original language.
                payload = tmdb_get("/search/movie", params)
                items = payload.get("results", [])
                if industry != "all":
                    wanted = {"tollywood": "te", "bollywood": "hi", "hollywood": "en"}[industry]
                    items = [m for m in items if m.get("original_language") == wanted]
                    if industry == "hollywood":
                        items = [m for m in items if "US" in (m.get("origin_country") or ["US"])]
                return {"results": items, "total_results": len(items), "total_pages": 1}
            return tmdb_get("/discover/movie", discover_params(industry, category, int(page)))
        key = f"movies:{industry}:{category}:{query}:{page}"
        payload = cached(key, load, refresh)
        movies = [normalize_movie(m, industry if industry != "all" else None) for m in payload.get("results", [])]
        return jsonify({"results": movies, "total_results": payload.get("total_results", len(movies)), "page": payload.get("page", 1), "total_pages": payload.get("total_pages", 1), "live": True, "notice": "Live TMDB metadata. Financial fields are available only for titles with reported values in TMDB."})
    except Exception as exc:
        # Make the failure transparent while preserving sample-data functionality.
        movies = offline_movies(industry, category, query)
        return jsonify({"results": movies, "total_results": len(movies), "page": 1, "total_pages": 1, "live": False, "warning": str(exc), "notice": "Live request failed; showing offline sample records instead."})


@app.get("/api/movie/<movie_id>")
def api_movie_detail(movie_id: str):
    if movie_id.startswith("demo-") or not live_configured():
        found = next((m for m in OFFLINE_MOVIES if str(m["id"]) == movie_id), None)
        if not found:
            return jsonify({"error": "This movie is available only through the live TMDB API. Configure the API credentials and try again."}), 404
        return jsonify({**found, "year": found.get("release_date", "")[:4], "poster_url": None, "live": False, "notice": "Offline sample record; budget and revenue have not been filled with invented values."})
    try:
        payload = cached(f"detail:{movie_id}", lambda: tmdb_get(f"/movie/{int(movie_id)}", {"language": "en-US"}), request.args.get("refresh") == "1")
        movie = normalize_movie(payload)
        movie["live"] = True
        return jsonify(movie)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 502


@app.get("/api/movie/<movie_id>/recommendations")
def api_recommendations(movie_id: str):
    if movie_id.startswith("demo-") or not live_configured():
        source = next((m for m in OFFLINE_MOVIES if str(m["id"]) == movie_id), None)
        if not source:
            return jsonify({"results": [], "live": False})
        src_genres = set(source["genre_names"])
        recs = [m for m in OFFLINE_MOVIES if m["id"] != movie_id and (src_genres.intersection(m["genre_names"]) or m["industry"] == source["industry"])]
        recs.sort(key=lambda m: (len(src_genres.intersection(m["genre_names"])), m["industry"] == source["industry"]), reverse=True)
        return jsonify({"results": recs[:6], "live": False})
    try:
        payload = cached(f"recs:{movie_id}", lambda: tmdb_get(f"/movie/{int(movie_id)}/recommendations", {"language": "en-US", "page": 1}), request.args.get("refresh") == "1")
        return jsonify({"results": [normalize_movie(m) for m in payload.get("results", [])[:12]], "live": True})
    except Exception as exc:
        return jsonify({"results": [], "live": False, "warning": str(exc)}), 502


@app.get("/api/box-office")
def api_box_office():
    industry = request.args.get("industry", "all").lower()
    refresh = request.args.get("refresh", "0") == "1"
    if industry not in {"all", "tollywood", "bollywood", "hollywood"}:
        return jsonify({"error": "Unknown industry."}), 400
    if not live_configured():
        # Clearly labelled illustrative figures so the analytics UI can be demonstrated offline.
        # These are NOT sourced real-world box-office values and must not be cited as factual.
        demo_financials = {
            "demo-1": (80000000, 160000000), "demo-2": (40000000, 180000000),
            "demo-3": (25000000, 90000000), "demo-5": (75000000, 110000000),
            "demo-6": (10000000, 30000000), "demo-7": (6000000, 25000000),
            "demo-8": (40000000, 130000000), "demo-11": (185000000, 1000000000),
            "demo-12": (165000000, 700000000), "demo-13": (160000000, 830000000),
            "demo-14": (100000000, 950000000), "demo-15": (190000000, 700000000),
            "demo-38": (200000000, 2200000000), "demo-39": (237000000, 2900000000),
            "demo-42": (220000000, 1500000000)
        }
        result = []
        for movie in OFFLINE_MOVIES:
            if industry != "all" and movie["industry"].lower() != industry:
                continue
            if movie["id"] not in demo_financials:
                continue
            budget, revenue = demo_financials[movie["id"]]
            record = {**movie, "budget": budget, "revenue": revenue,
                      "profit": revenue - budget,
                      "roi": (revenue - budget) / budget * 100,
                      "illustrative_demo": True}
            result.append(record)
        result.sort(key=lambda m: m["revenue"], reverse=True)
        return jsonify({"results": result, "live": False,
                        "illustrative_demo": True,
                        "notice": "ILLUSTRATIVE DEMO ONLY: financial figures below are synthetic examples created to demonstrate charts and ROI calculations. They are NOT verified real box-office data. Configure a data provider for reported figures."})
    try:
        def load():
            payload = tmdb_get("/discover/movie", discover_params(industry, "popular", 1))
            ids = [m.get("id") for m in payload.get("results", [])[:16] if m.get("id")]
            details: list[dict[str, Any]] = []
            with ThreadPoolExecutor(max_workers=6) as pool:
                futures = {pool.submit(tmdb_get, f"/movie/{mid}", {"language": "en-US"}): mid for mid in ids}
                for future in as_completed(futures):
                    try:
                        record = future.result()
                        if record.get("budget") or record.get("revenue"):
                            details.append(record)
                    except Exception:
                        continue
            details.sort(key=lambda m: (m.get("revenue") or 0), reverse=True)
            return details
        raw = cached(f"box:{industry}", load, refresh)
        result = []
        for item in raw:
            m = normalize_movie(item, industry if industry != "all" else None)
            budget, revenue = m.get("budget") or 0, m.get("revenue") or 0
            m["profit"] = revenue - budget if revenue and budget else None
            m["roi"] = ((revenue - budget) / budget * 100) if revenue and budget else None
            result.append(m)
        return jsonify({"results": result, "live": True, "notice": "Financial values are from TMDB records when present; they may be missing or incomplete and are not audited box-office returns."})
    except Exception as exc:
        return jsonify({"results": [], "live": False, "warning": str(exc), "notice": "Could not load box-office data. Verify the TMDB credentials and internet connection."})


@app.get("/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=True)
