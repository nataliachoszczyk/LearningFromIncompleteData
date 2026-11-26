"""Test the setup: clone the repository, import src and write the versions of the libraries."""
import json
import os
import platform
import subprocess
import sys

REPO = "https://github.com/nataliachoszczyk/LearningFromIncompleteData.git"
BRANCH = "main"
CLONE = "/tmp/repo"  # Not in the output folder, so the clone is not an output.

subprocess.run(["git", "clone", "--depth", "1", "--branch", BRANCH, REPO, CLONE], check=True)
commit = subprocess.run(["git", "-C", CLONE, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
print("commit", commit)
sys.path.insert(0, CLONE)

import numpy
import pandas
import scipy
import sklearn

import src  # noqa: F401

info = {
    "commit": commit,
    "python": platform.python_version(),
    "cpu_count": os.cpu_count(),
    "numpy": numpy.__version__,
    "pandas": pandas.__version__,
    "scipy": scipy.__version__,
    "sklearn": sklearn.__version__,
}
print(info)
os.makedirs("/kaggle/working/smoke", exist_ok=True)
with open("/kaggle/working/smoke/info.json", "w") as f:
    json.dump(info, f, indent=2)
