"""Download the six UCI datasets. The output of this job becomes the private dataset med-datasets."""
import shutil
import subprocess
import sys
from pathlib import Path

REPO = "https://github.com/nataliachoszczyk/LearningFromIncompleteData.git"
BRANCH = "part1"
CLONE = "/tmp/repo"  # Not in the output folder, so the clone is not an output.

subprocess.run(["git", "clone", "--depth", "1", "--branch", BRANCH, REPO, CLONE], check=True)
print("commit", subprocess.run(["git", "-C", CLONE, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip())
sys.path.insert(0, CLONE)

from src.data import download_all

out = Path("/kaggle/working")
download_all(out)
# The kernel output must contain only the data of the dataset.
shutil.rmtree(out / ".virtual_documents", ignore_errors=True)
