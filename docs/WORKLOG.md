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
- Added `docs/PLAN.md` (local only, not in git): the plan of the project in two halves. Half A: the base of the code and part 1. Half B: the rules, the experiments and part 2.
- Added `docs/*.pdf` (the papers) and `docs/PLAN.md` (the plan) to `.gitignore`. These files are local only.
- Decision: the plan has two persons who work one after the other. Person A does the first half (weekend 1), person B the second half (weekend 2). Person A needs nothing from person B. The details are in `docs/PLAN.md`.
- Natalia does the half A. The work on it starts on 2026-11-26.
- Downloaded the Kaggle dataset `nataliachoszczyk/med-datasets` into `data/` (6.5 MB, not in git).
- A1: added `load_dataset(name)`, `numeric_attributes(df)` and `SPECS` to `src/data.py`. The common form:
  - one row for each record, `NaN` for a missing value, the column `class` at the end,
  - numeric attributes have the type `float64`, symbolic attributes and the class have the type `category`,
  - `adult` joins `adult.data` and `adult.test`, `wdbc` has no column `id`.
- A local test loaded the 6 datasets. The statistics agree with UCI:

  | Dataset | Records | Attributes | Numeric | Missing cells | Incomplete records |
  |---|---|---|---|---|---|
  | `voting` | 435 | 16 | 0 | 5.63% | 46.7% |
  | `hepatitis` | 155 | 19 | 6 | 5.67% | 48.4% |
  | `mushroom` | 8124 | 22 | 0 | 1.39% | 30.5% |
  | `car` | 1728 | 6 | 0 | 0% | 0% |
  | `wdbc` | 569 | 30 | 30 | 0% | 0% |
  | `adult` | 48842 | 14 | 6 | 0.95% | 7.4% |
- A2: added `src/missing.py` with `add_mcar(df, fraction, seed)`. It removes the given fraction of the known attribute values at random and never removes the class. It returns the new table and a boolean mask of the removed values. The mask gives the true values for the error of an imputation.
- A local test on `car`, `wdbc` and `voting` (0%, 5%, 30%, 50%): the removed fraction is correct, the class and the types of the columns do not change, the same seed gives the same table.

### State for the next session

- Branch: `part1` (pushed). The Kaggle account is `nataliachoszczyk`. The data is in the private dataset `nataliachoszczyk/med-datasets`.
- Jobs: `2026-11-26_01_smoke` and `2026-11-26_02_data` are complete. The next job number is 03.
- `src/data.py` has `DATASETS`, `download_all()` and `data_dir()`. Local data: put a copy of the dataset into `data/` (not in git), or download it with `bash jobs/kaggle.sh datasets download nataliachoszczyk/med-datasets -p data --unzip`.
- Next steps of the half A (`docs/PLAN.md`):
  1. A1: complete.
  2. A2: complete.
  3. A3: `src/impute.py` (kNN, mean and mode, normalized RMS error).
  4. A4-A5: `src/rough.py` (discretization, tolerance classes, approximations, generalized decision).
  5. A6: tests and a Kaggle CPU job with the run times.
  6. A7-A9: `docs/design.md`, the presentation of part 1, chapters 1, 2, 5 and 8 of the final documentation.
- Open decisions for A1-A5: the method of the discretization, the distance and the weights of kNN for symbolic attributes, the form of the bit sets for the tolerance classes.
