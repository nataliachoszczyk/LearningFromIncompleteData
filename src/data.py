"""Download the UCI datasets of the project, find them on Kaggle and on the local machine, and load them."""
import hashlib
import io
import json
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

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


WDBC_FEATURES = ["radius", "texture", "perimeter", "area", "smoothness", "compactness",
                 "concavity", "concave_points", "symmetry", "fractal_dimension"]

# For each dataset: the files, the column names in the file order, the class column and the numeric columns.
SPECS = {
    "voting": {
        "files": ["house-votes-84.data"],
        "columns": ["class", "handicapped_infants", "water_project", "budget_resolution",
                    "physician_fee_freeze", "el_salvador_aid", "religious_groups_in_schools",
                    "anti_satellite_test_ban", "aid_to_nicaraguan_contras", "mx_missile", "immigration",
                    "synfuels_cutback", "education_spending", "superfund_right_to_sue", "crime",
                    "duty_free_exports", "export_south_africa"],
        "numeric": [],
    },
    "hepatitis": {
        "files": ["hepatitis.data"],
        "columns": ["class", "age", "sex", "steroid", "antivirals", "fatigue", "malaise", "anorexia",
                    "liver_big", "liver_firm", "spleen_palpable", "spiders", "ascites", "varices",
                    "bilirubin", "alk_phosphate", "sgot", "albumin", "protime", "histology"],
        "numeric": ["age", "bilirubin", "alk_phosphate", "sgot", "albumin", "protime"],
    },
    "mushroom": {
        "files": ["agaricus-lepiota.data"],
        "columns": ["class", "cap_shape", "cap_surface", "cap_color", "bruises", "odor", "gill_attachment",
                    "gill_spacing", "gill_size", "gill_color", "stalk_shape", "stalk_root",
                    "stalk_surface_above_ring", "stalk_surface_below_ring", "stalk_color_above_ring",
                    "stalk_color_below_ring", "veil_type", "veil_color", "ring_number", "ring_type",
                    "spore_print_color", "population", "habitat"],
        "numeric": [],
    },
    "car": {
        "files": ["car.data"],
        "columns": ["buying", "maint", "doors", "persons", "lug_boot", "safety", "class"],
        "numeric": [],
    },
    "wdbc": {
        "files": ["wdbc.data"],
        "columns": ["id", "class"] + [f"{f}_{s}" for s in ("mean", "se", "worst") for f in WDBC_FEATURES],
        "numeric": [f"{f}_{s}" for s in ("mean", "se", "worst") for f in WDBC_FEATURES],
    },
    "adult": {
        "files": ["adult.data", "adult.test"],
        "columns": ["age", "workclass", "fnlwgt", "education", "education_num", "marital_status",
                    "occupation", "relationship", "race", "sex", "capital_gain", "capital_loss",
                    "hours_per_week", "native_country", "class"],
        "numeric": ["age", "fnlwgt", "education_num", "capital_gain", "capital_loss", "hours_per_week"],
    },
}


def load_dataset(name: str) -> pd.DataFrame:
    """Load a dataset in the common form of the project.

    Each row is one record. NaN is a missing value. The column "class" is the last column.
    Numeric attributes have the type float64. Symbolic attributes and the class have the type category.
    """
    spec = SPECS[name]
    parts = []
    for file in spec["files"]:
        path = data_dir() / name / file
        # The first line of adult.test is not a record.
        skip = 1 if file == "adult.test" else 0
        parts.append(pd.read_csv(path, header=None, names=spec["columns"], dtype=str, na_values="?",
                                 skipinitialspace=True, skiprows=skip))
    df = pd.concat(parts, ignore_index=True)
    # adult.test writes the class with a final dot, for example "<=50K.".
    df["class"] = df["class"].str.rstrip(".")
    attributes = [c for c in spec["columns"] if c not in ("class", "id")]
    df = df[attributes + ["class"]]
    for column in df.columns:
        df[column] = df[column].astype(float) if column in spec["numeric"] else df[column].astype("category")
    return df


def numeric_attributes(df: pd.DataFrame) -> list[str]:
    """Return the names of the numeric attributes."""
    return [c for c in df.columns if c != "class" and pd.api.types.is_float_dtype(df[c])]
