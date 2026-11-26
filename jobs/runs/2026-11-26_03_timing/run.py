"""Measure the run time of the kNN imputation and of the tolerance classes for different sizes and parameters."""
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

REPO = "https://github.com/nataliachoszczyk/LearningFromIncompleteData.git"
BRANCH = "part1"
CLONE = "/tmp/repo"  # Not in the output folder, so the clone is not an output.
REPEATS = 3
FRACTION = 0.1

subprocess.run(["git", "clone", "--depth", "1", "--branch", BRANCH, REPO, CLONE], check=True)
commit = subprocess.run(["git", "-C", CLONE, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
print("commit", commit)
sys.path.insert(0, CLONE)

import numpy as np
import pandas as pd

from src.data import load_dataset
from src.impute import impute_knn
from src.missing import add_mcar
from src.rough import count, cut_points, discretize, encode, tolerance_classes

out = Path("/kaggle/working/timing")
out.mkdir(parents=True, exist_ok=True)
rows = []


def measure(study, dataset, df, fraction=FRACTION, k=10):
    """Run kNN and the tolerance classes REPEATS times with different seeds. Keep the median time."""
    knn, tolerance, sizes = [], [], []
    for seed in range(REPEATS):
        missing, _ = add_mcar(df, fraction, seed)
        start = time.perf_counter()
        impute_knn(missing, k)
        knn.append(time.perf_counter() - start)
        codes, _, _ = encode(discretize(missing, cut_points(missing, 4)))
        start = time.perf_counter()
        classes = tolerance_classes(codes)
        tolerance.append(time.perf_counter() - start)
        sizes.append(count(classes).mean())
    row = {"study": study, "dataset": dataset, "records": len(df), "attributes": df.shape[1] - 1,
           "fraction": fraction, "k": k, "knn_s": float(np.median(knn)),
           "tolerance_s": float(np.median(tolerance)), "mean_class_size": float(np.mean(sizes))}
    print(row, flush=True)
    rows.append(row)
    pd.DataFrame(rows).to_csv(out / "timing.csv", index=False)


# Records: complete records of adult, so the fraction of missing values is the same for each size.
adult = load_dataset("adult").dropna().reset_index(drop=True)
for n in [1000, 2000, 5000, 10000, 20000, len(adult)]:
    measure("records", "adult", adult.sample(n, random_state=0).reset_index(drop=True))

# Attributes: the first m attributes of wdbc and of mushroom.
for name, sizes in [("wdbc", [5, 10, 15, 20, 25, 30]), ("mushroom", [5, 10, 15, 22])]:
    df = load_dataset(name)
    for m in sizes:
        measure("attributes", name, df[list(df.columns[:m]) + ["class"]])

# Fraction of missing values.
for name in ["car", "mushroom"]:
    df = load_dataset(name)
    for fraction in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]:
        measure("fraction", name, df, fraction=fraction)

# Number of neighbours.
wdbc = load_dataset("wdbc")
for k in [1, 5, 10, 20, 50]:
    measure("k", "wdbc", wdbc, k=k)

info = {"commit": commit, "python": platform.python_version(), "cpus": os.cpu_count(),
        "numpy": np.__version__, "pandas": pd.__version__, "repeats": REPEATS}
(out / "info.json").write_text(json.dumps(info, indent=2))
