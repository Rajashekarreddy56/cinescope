"""Download and verify the CineScope SQLite catalogue during a Render build."""
from __future__ import annotations

import hashlib
import os
import sqlite3
import tempfile
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = Path(
    os.environ.get("CINESCOPE_DATASET_PATH", str(ROOT / "data" / "movies.sqlite3"))
).resolve()
DATASET_URL = (
    "https://github.com/Rajashekarreddy56/cinescope/releases/download/"
    "v1.0/movies.sqlite3"
)
EXPECTED_SHA256 = "e733584b7ee7734ad9cc6aa4cad643e370eb1fc8aefc9a42c8ef637a2d16b1ea"
MAX_DATASET_BYTES = 256 * 1024 * 1024


def expected_sha256() -> str:
    if len(EXPECTED_SHA256) != 64 or any(
        character not in "0123456789abcdefABCDEF" for character in EXPECTED_SHA256
    ):
        raise RuntimeError(
            "The configured expected SHA-256 must contain exactly 64 hexadecimal "
            f"characters; got {len(EXPECTED_SHA256)}."
        )
    return EXPECTED_SHA256.lower()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as dataset:
        for chunk in iter(lambda: dataset.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_dataset(path: Path) -> int:
    if not path.is_file():
        raise RuntimeError("The SQLite dataset file is missing.")
    if path.stat().st_size == 0:
        raise RuntimeError("The SQLite dataset file is empty.")

    actual_sha256 = file_sha256(path)
    expected = expected_sha256()
    if actual_sha256 != expected:
        raise RuntimeError(
            "SQLite dataset SHA-256 mismatch: "
            f"expected {expected}, got {actual_sha256}."
        )

    connection = sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True)
    try:
        if connection.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise RuntimeError("The SQLite dataset failed its integrity check.")
        columns = {
            row[1] for row in connection.execute("PRAGMA table_info(movies)")
        }
        required_columns = {
            "id", "title", "original_title", "original_language", "release_date",
            "year", "genres", "overview", "vote_average", "vote_count", "popularity",
            "runtime", "budget", "revenue", "poster_path", "backdrop_path",
            "tagline", "imdb_id",
        }
        if not required_columns.issubset(columns):
            raise RuntimeError(
                "The SQLite movies table is missing required CineScope columns."
            )
        count = connection.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
        if count <= 0:
            raise RuntimeError("The SQLite movies table is empty.")
        return count
    finally:
        connection.close()


def download_dataset(destination: Path) -> int:
    expected = expected_sha256()
    parsed_url = urlparse(DATASET_URL)
    if parsed_url.scheme != "https" or not parsed_url.netloc:
        raise RuntimeError("The configured SQLite dataset URL must use HTTPS.")

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix="cinescope-dataset-",
            suffix=".download",
            dir=destination.parent,
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            request = Request(
                DATASET_URL,
                headers={"User-Agent": "CineScope-Render-Deploy"},
            )
            with urlopen(request, timeout=180) as response:
                if urlparse(response.geturl()).scheme != "https":
                    raise RuntimeError("The dataset download redirected away from HTTPS.")
                downloaded = 0
                digest = hashlib.sha256()
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    downloaded += len(chunk)
                    if downloaded > MAX_DATASET_BYTES:
                        raise RuntimeError(
                            "The dataset exceeds the 256 MiB safety limit."
                        )
                    digest.update(chunk)
                    temporary_file.write(chunk)

        actual_sha256 = digest.hexdigest()
        if actual_sha256 != expected:
            raise RuntimeError(
                "Downloaded SQLite dataset SHA-256 mismatch: "
                f"expected {expected}, got {actual_sha256}."
            )
        count = validate_dataset(temporary_path)
        os.replace(temporary_path, destination)
        return count
    except RuntimeError:
        raise
    except Exception:
        raise RuntimeError(
            "SQLite dataset download failed; check the GitHub Release asset and network access."
        ) from None
    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()


def main() -> None:
    expected_sha256()
    if DATASET_PATH.exists():
        try:
            count = validate_dataset(DATASET_PATH)
        except RuntimeError:
            print("Existing SQLite dataset is invalid; downloading a verified copy.")
        else:
            print(
                f"Verified existing SQLite dataset ({count:,} movies); download skipped."
            )
            return

    count = download_dataset(DATASET_PATH)
    print(
        f"Downloaded and verified the SQLite dataset ({count:,} movies) "
        f"at {DATASET_PATH}."
    )


if __name__ == "__main__":
    main()
