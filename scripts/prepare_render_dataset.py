"""Install an existing SQLite catalogue artifact during a Render build."""
from __future__ import annotations

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
MAX_DATASET_BYTES = 512 * 1024 * 1024


def validate_dataset(path: Path) -> int:
    if not path.is_file():
        raise RuntimeError("The SQLite dataset file is missing.")
    if path.stat().st_size == 0:
        raise RuntimeError("The SQLite dataset file is empty.")

    connection = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    try:
        if connection.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise RuntimeError("The SQLite dataset failed its integrity check.")
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        if "movies" not in tables:
            raise RuntimeError("The SQLite dataset does not contain a movies table.")
        count = connection.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
        if count <= 0:
            raise RuntimeError("The SQLite movies table is empty.")
        return count
    finally:
        connection.close()


def download_dataset(url: str, destination: Path) -> int:
    parsed_url = urlparse(url)
    if parsed_url.scheme != "https" or not parsed_url.netloc:
        raise RuntimeError("CINESCOPE_DATASET_URL must be an HTTPS artifact URL.")

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
            request = Request(url, headers={"User-Agent": "CineScope-Render-Deploy"})
            with urlopen(request, timeout=180) as response:
                if urlparse(response.geturl()).scheme != "https":
                    raise RuntimeError("The dataset download redirected away from HTTPS.")
                downloaded = 0
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    downloaded += len(chunk)
                    if downloaded > MAX_DATASET_BYTES:
                        raise RuntimeError("The dataset exceeds the 512 MiB safety limit.")
                    temporary_file.write(chunk)

        count = validate_dataset(temporary_path)
        os.replace(temporary_path, destination)
        return count
    except RuntimeError:
        raise
    except Exception:
        raise RuntimeError(
            "Dataset download failed; verify the HTTPS artifact URL and access permissions."
        ) from None
    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()


def main() -> None:
    if DATASET_PATH.exists():
        count = validate_dataset(DATASET_PATH)
        print(f"Using the existing SQLite dataset ({count:,} movies).")
        return

    url = os.environ.get("CINESCOPE_DATASET_URL", "").strip()
    if not url:
        raise RuntimeError(
            "CINESCOPE_DATASET_URL is required when the SQLite dataset is not present."
        )
    count = download_dataset(url, DATASET_PATH)
    print(f"Installed the SQLite dataset ({count:,} movies) at {DATASET_PATH}.")


if __name__ == "__main__":
    main()
