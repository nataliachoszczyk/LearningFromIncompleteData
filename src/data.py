"""Download the UCI datasets of the project and find them on Kaggle and on the local machine."""
import hashlib
import io
import json
import urllib.request
import zipfile
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
KAGGLE_INPUT = Path("/kaggle/input")

UCI = "https://archive.ics.uci.edu/static/public"
DATASETS = {
    "voting": f"{UCI}/105/congressional+voting+records.zip",
    "hepatitis": f"{UCI}/46/hepatitis.zip",
    "mushroom": f"{UCI}/73/mushroom.zip",
    "car": f"{UCI}/19/car+evaluation.zip",
    "wdbc": f"{UCI}/17/breast+cancer+wisconsin+diagnostic.zip",
    "adult": f"{UCI}/2/adult.zip",
}


def data_dir() -> Path:
    """Return the folder that contains one subfolder for each dataset."""
    if KAGGLE_INPUT.exists():
        # The path of a dataset under /kaggle/input can change, so search for a known file.
        matches = sorted(KAGGLE_INPUT.rglob("manifest.json"))
        assert matches, "no project data in /kaggle/input"
        return matches[0].parent
    return PROJECT_DIR / "data"


def download_all(out: Path) -> dict:
    """Download and extract each dataset into out/<name>/. Write a manifest with the sizes and hashes."""
    manifest = {}
    for name, url in DATASETS.items():
        with urllib.request.urlopen(url, timeout=60) as response:
            raw = response.read()
        folder = out / name
        folder.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            archive.extractall(folder)
        files = sorted(p for p in folder.rglob("*") if p.is_file())
        manifest[name] = {
            "url": url,
            "sha256_zip": hashlib.sha256(raw).hexdigest(),
            "files": {p.relative_to(folder).as_posix(): p.stat().st_size for p in files},
        }
        print(name, len(raw), "bytes,", len(files), "files")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest
