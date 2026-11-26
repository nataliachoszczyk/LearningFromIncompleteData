# Worklog

## 2026-11-26

- Selected the topic: inference from incomplete data, a combination of 7.1 (rough sets, Kryszkiewicz 1998) and 7.3 (kNN imputation, Troyanskaya et al. 2001).
- Made the repository structure from the model of the repository AISecurity:
  - `CLAUDE.md`: the rules of work (local only, not in git).
  - `KAGGLE.md`: the method to run jobs on Kaggle, with the values of this project in section 0.
  - `docs/task.md` (Polish, original) and `docs/task_eng.md` (English).
  - `docs/WORKLOG.md`: this file.
  - `jobs/JOBS.md`, `jobs/kaggle.sh`, `jobs/wait.sh`, `jobs/runs/`.
  - `src/`, `data/` (not in git), `.gitignore`, `requirements.txt`.
- Made `.venv` with uv: Python 3.12.10, scikit-learn 1.9.1, numpy 2.5.5, pandas 3.1.1, Kaggle CLI 2.2.5.
- Checked the connection to Kaggle: `jobs/kaggle.sh` uses the account `nataliachoszczyk` (personal credentials in `~/.kaggle/`). `kernels list --mine` works.
- Added the job `2026-11-26_01_smoke`. It clones the repository on a Kaggle CPU kernel and writes the versions of the libraries. It needs the first push of the repository.
- Pushed the first commit to `main`.
- The job `smoke` is complete (approximately 1 minute). The kernel has internet, so the phone verification of the account is done. The clone of the repository and the import of `src` work.
- Kaggle has Python 3.13.18, 4 CPUs, numpy 2.1.3, pandas 2.3.3, scipy 1.16.3 and scikit-learn 1.6.1. The local versions are newer, so the code must not use new features of these libraries.
- Started the branch `part1` for part 1 of the project. Kaggle kernels clone this branch (`CLAUDE.md`, `KAGGLE.md`).
- Added the PDF files of the two papers to `docs/` (not in git, because of the copyright). Read the two papers:
  - Kryszkiewicz (1998) uses no real dataset. It has one example table of 6 cars (Table 2) with the expected tolerance classes, approximations, generalized decisions, reducts and rules. This table can be a test of our code.
  - Troyanskaya et al. (2001) use 3 yeast microarray datasets: Spellman et al. (1998), DeRisi et al. (1997) and Gasch et al. (2000). They remove the incomplete rows and columns, delete 1-20% of the values at random and measure the normalized RMS error. K = 10-20 is the best.
- Checked the data sources. The Stanford pages of the papers do not answer. GEO has the Spellman data: GDS38 (7680 genes, 16 arrays, 6.1% missing) and GDS39 (7680 genes, 14 arrays, 3.2% missing). The UCI files are available. The FIMI page gives 404.
- Decision: the project uses 6 UCI datasets, all in one private Kaggle dataset `nataliachoszczyk/med-datasets`:
  - `voting` (435 x 16, symbolic, natural missing values): rough sets directly on the missing values.
  - `hepatitis` (155 x 19, mixed, natural missing values): comparison of the strategies.
  - `mushroom` (8124 x 22, symbolic, natural missing values): scalability for the number of records.
  - `car` (1728 x 6, symbolic, complete): robustness for 5-50% of simulated missing values.
  - `wdbc` (569 x 30, numeric, complete): error of the kNN imputation for different k, scalability for the number of attributes.
  - `adult` (48842 x 14, mixed, natural missing values): run time for a large number of records.
- Decision: no example table from Kryszkiewicz (1998) and no microarray data from Troyanskaya et al. (2001).
- Renamed the branch `rough-set-knn` to `part1`.
- Added `src/data.py`: the URLs of the datasets, `download_all()` and `data_dir()`. A local test downloaded all 6 datasets.
- Added the job `2026-11-26_02_data`. It downloads the datasets on a Kaggle CPU kernel.
- The job `data` is complete (1 minute). Made the private dataset `nataliachoszczyk/med-datasets` from its output with the Kaggle CLI (`datasets create --dir-mode zip`). Kaggle extracted each folder, so the dataset has the folders `adult/`, `car/`, `hepatitis/`, `mushroom/`, `voting/`, `wdbc/` and `manifest.json`. License: CC BY 4.0 (UCI).
- Problem: the Kaggle CLI on Windows fails with a Git Bash path (`C:/...`). Give it a Windows path (`cygpath -w`).
