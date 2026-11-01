# CineScope dataset sources and update policy

## Primary movie catalogue

- Dataset: `TMDB_movie_dataset_v11.csv`
- Download page: https://huggingface.co/datasets/ada-datadruids/full_tmdb_movies_dataset
- Direct file: https://huggingface.co/datasets/ada-datadruids/full_tmdb_movies_dataset/resolve/main/TMDB_movie_dataset_v11.csv
- Reported file size: approximately 524 MB; large-scale TMDB metadata collection.
- Related large collection listing: Kaggle's *Full TMDB Movies Dataset 2024 (1M Movies)* describes a one-million-record catalogue and daily updates: https://www.kaggle.com/dsv/10525426
- Data is sourced from TMDB. TMDB branding/data terms and the dataset host's current licence must be reviewed before public/commercial redistribution. The Kaggle listing reports ODC-By attribution; do not assume every mirror inherits that licence without checking its own dataset card.

## Install/update

Run `py scripts/download_dataset.py` from the CineScope project folder. The downloaded CSV is stored under `data/raw/` and imported into indexed `data/movies.sqlite3`. CineScope reads this local file; movie browsing does not call a movie API at runtime. Re-run the script when you want to refresh the source snapshot. A new snapshot is only as recent as the upstream file currently published.

## Data quality and analytics notes

- Language-to-industry labels are heuristics (for example, Telugu → Tollywood and Hindi → Bollywood), not official industry classifications.
- Budget and revenue are only used when present and positive in the source. Missing financial values are not imputed or fabricated.
- Currency is retained as supplied by the source; do not compare currencies without normalization.
- Ratings are source dataset ratings, not IMDb ratings unless the source explicitly identifies them as such.
- Poster paths are linked to TMDB image hosting; offline browsing/search/analytics work without posters, but poster images need internet access unless separately cached.
