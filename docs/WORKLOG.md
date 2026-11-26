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
- Decision: the kNN imputation uses the Gower distance on the attributes that the two records both have. A numeric attribute gives |x - y| / range. A symbolic attribute gives 0 or 1. The weight of a neighbour is 1 / distance. A numeric value is the weighted mean, a symbolic value is the weighted mode.
- Decision: the error of an imputation has two parts. `nrmse` is the RMS error on the numeric attributes, with each attribute divided by its standard deviation. `error_rate` is the fraction of wrong symbolic values. Troyanskaya et al. divide by the mean of one table, but our attributes have different scales.
- A3: added `src/impute.py` with `impute_mean_mode(df)`, `impute_knn(df, k)` and `imputation_error(true, imputed, removed)`. The kNN calculates the distances in blocks, so the memory stays small. The time is O(incomplete records x records x attributes).
- A local test (seed 0):
  - `wdbc`: kNN is better than the mean (nrmse 0.51-0.55 for k = 5-10 at 5-20%, mean 0.97). k = 1 is the worst kNN.
  - `voting`: kNN is better than the mode (error rate 0.20-0.25, mode 0.43-0.45).
  - `car`: kNN is not better than the mode. Each combination of the attribute values occurs once in `car`, so the attributes are independent and the neighbours give no information.
  - `hepatitis`: kNN is better on the symbolic attributes, but worse than the mean on the numeric attributes. The dataset is small and the numeric attributes are skewed.
  - `adult`: kNN with k = 10 on the natural missing values takes 35 s on the local CPU. On 10000 complete records with 5% MCAR it takes 9 s.
- Problem: the local machine has no PDF tools, so the text of the papers cannot be read automatically.
- Decision: the discretization is equal-frequency (quantiles) with 4 intervals as default. It does not use the class. The cut points come from the known values. `cut_points` and `discretize` are separate functions, so the cut points of the training records also apply to the test records.
- Decision: a tolerance class is a bit set of uint64 words. For each attribute a and value v, the bit set S(a, v) has the records with a = v or a missing. I(x) is the AND of S(a, a(x)). The time is O(|B| n^2 / 64), the memory is n^2 / 8 bytes.
- A4-A5: added `src/rough.py` with `cut_points`, `discretize`, `encode`, `pack`, `unpack`, `count`, `tolerance_classes(codes, attributes)`, `lower_approximation`, `upper_approximation` and `generalized_decision`.
- A local test:
  - The cars of Table 2 in Kryszkiewicz (1998) give the tolerance classes and the generalized decisions of the paper. The lower approximation of "good" is {1, 2}, the upper approximation is {1, 2, 4, 5, 6}.
  - On `voting`, `car`, `hepatitis` and `wdbc` (with MCAR), the bit sets are equal to a direct calculation of SIM, also for a subset of the attributes.
  - Run time: `mushroom` 0.1 s (8 MB), `adult` 1.7 s (299 MB).
- Result: in `voting`, one record has all 16 values missing. It is tolerant to all records, so only 33% of the records have one decision. Without the records with 8 or more missing values, 98% of the records have one decision. The tolerance relation is sensitive to records with many missing values.
- A6: added `tests/test_core.py` (15 pytest tests of A1-A5, 5.5 s on the local CPU) and `pytest` to `requirements.txt`. All tests pass.
- A6: added the job `2026-11-26_03_timing`. It measures the run time of `impute_knn` and `tolerance_classes` for the number of records, the number of attributes, the fraction of missing values and k.
- A7: added `docs/design.md`, the design document of the complete implementation (also the planned modules of B1-B4): scope, technologies, structure with references to the papers, data structures, efficiency and test plan.
- The job `timing` is complete (37 minutes). Downloaded `timing.csv` and `info.json`. Results:
  - `adult` with 45222 records: kNN 434 s, tolerance classes 1.8 s. From 20000 to 45222 records, both times grow approximately with n^2.
  - The times grow approximately linearly with the number of attributes.
  - The time of the tolerance classes does not depend on the fraction of missing values. The mean size of a tolerance class grows fast: `car` 1 (0%), 134 (30%), 535 (50%).
  - k = 1-50 has no effect on the time of kNN.
- Added the measured run times to section 6.1 of `docs/design.md`.
- Read the two papers with `pypdf` in a temporary uv environment (`uv run --no-project --with pypdf`). `requirements.txt` does not change. Results:
  - Kryszkiewicz (1998): the definitions of SIM, the tolerance class S_A(x), the approximations and the generalized decision agree with `src/rough.py`. The discernibility function for x is Δ*(x) = Π Σ α_AT(x, y) over the y with d(y) ∉ ∂_AT(x). α_AT(x, y) has the attributes with both values known and different. Examples 4.2 and 5.2 give the expected reducts and rules of Table 2 for the tests of B1-B2.
  - Troyanskaya et al. (2001): the normalized RMS error is the RMS difference divided by the mean of the complete data. The paper weights the neighbours by similarity, but gives no formula. The paper uses the Euclidean distance. Its row average is the mean of a gene (a row), not of a column.
- Fixed the docstring of `impute_knn`: the weight 1 / distance is our selection, not a formula of the paper.
- Decision: the design document of part 1 is in Polish. Renamed `docs/design.md` to `docs/SUMMARY.md` and translated it. The final documentation and the presentations are also in Polish. The README is in English.
- Added the corrections from the papers to `docs/SUMMARY.md`: the notation of Kryszkiewicz (S_A(x), α_AT(x, y), Δ*(x)), the differences from Troyanskaya et al. and the expected reducts and rules of Table 2.
- A9: added `docs/DOKUMENTACJA.md` (Polish), the final documentation with 9 chapters. Chapters 1, 2, 5 and 8 are complete. Chapters 3, 4, 6, 7 and 9 have only a heading for person B.
- Checked the facts of chapter 5 on the data: `protime` has 43.2% missing values, `veil_type` has one value, `mushroom` has missing values only in `stalk_root`, `adult` only in `workclass`, `occupation` and `native_country`.
- Result: `voting.names` tells that "?" is not an unknown value, but a vote that is not "yea" or "nay". Chapter 5 tells this and why we use "?" as a missing value.
- A8: made the presentation of part 1 in Canva (14 slides, Polish, white background, no decoration): title, problem, 4 strategies, tolerance relation, reducts and rules, kNN imputation, datasets, technologies, structure, data structures, efficiency, test plan, status, bibliography.

- Renamed the documents, so that the name tells the deadline:
  - `docs/DESIGN.md`: the design of the implementation for part 1 (2026-12-17). Before, `docs/SUMMARY.md`.
  - `docs/SUMMARY.md`: the final documentation with 9 chapters for part 2 (2027-01-21). Before, `docs/DOKUMENTACJA.md`.
- Saved the edits of the presentation of part 1 in Canva (design `DAHcDKYk1rw`, title "Wnioskowanie z danych").

### State for the next session

- Branch: `part1` (pushed). The Kaggle account is `nataliachoszczyk`. The data is in the private dataset `nataliachoszczyk/med-datasets`.
- Jobs: `01_smoke`, `02_data` and `03_timing` are complete. The next job number is 04.
- Local data: download it with `bash jobs/kaggle.sh datasets download nataliachoszczyk/med-datasets -p data --unzip` (Windows: give `-p` a Windows path, `cygpath -w`).
- Run the tests with `.venv/Scripts/python.exe -m pytest -q tests` (15 tests, approximately 6 s).

#### Half A (person A): complete

| Step | Result |
|---|---|
| A1-A5 | `src/data.py`, `src/missing.py`, `src/impute.py`, `src/rough.py` |
| A6 | `tests/test_core.py`, job `03_timing` |
| A7 | `docs/DESIGN.md` (Polish), the design of the complete implementation, also of B1-B4 |
| A8 | presentation of part 1 in Canva (14 slides, Polish) |
| A9 | `docs/SUMMARY.md`, chapters 1, 2, 5 and 8 |

Decisions of half A (details in `docs/DESIGN.md`):

- Discretization: equal-frequency, 4 intervals as default. The cut points come from the training records (`cut_points`, then `discretize`).
- kNN: Gower distance on the attributes that the two records both have, weight 1 / distance, weighted mean or weighted mode.
- Error of an imputation: `nrmse` (each numeric attribute divided by its standard deviation) and `error_rate` (symbolic attributes).
- Tolerance classes: bit sets of `uint64` words, n x ceil(n / 64).
- In `voting`, "?" is a missing value. `voting.names` tells that "?" is a third position, not an unknown value. `docs/SUMMARY.md`, chapter 5.2, tells this.

#### Before 2026-12-17 (part 1): tasks of the team

1. Agree the scope of the project with the teacher. A team of two must do this (`docs/task.md`, "Liczność grup").
2. Agree the date of the consultation with the teacher.
3. Add the names of the authors to the title slide in Canva. Optional: use the font of the titles also for the bullet points.
4. Export the presentation from Canva (`.pptx` or PDF).
5. Upload `docs/DESIGN.md` (as PDF) to https://leon.pw.edu.pl/course/view.php?id=2333 before the presentation.

#### Half B (person B): open work

Code (the interfaces are in `docs/DESIGN.md`, sections 3.4-3.6 and 5.3):

| Step | Work | Result |
|---|---|---|
| B1 | `discernibility(codes, general, x)`: α_AT(x, y) for the y with d(y) ∉ ∂_AT(x), as an attribute mask. `local_reduct(codes, general, x)`: greedy set cover, then remove the attributes that are not necessary. `reduct(codes, general)` for the complete table. | `src/rough.py` |
| B2 | `rules(codes, d, general)`: one rule for each object from its local reduct and ∂_AT(x). Skip the conditions (a, *). Join the duplicate rules and add their support. | `src/rough.py` |
| B3 | `RuleClassifier`: `fit` and `predict`. A rule matches a record if each condition (a, v) has a(z) = v or a(z) = *. Vote with the support. No match: the most frequent class. | `src/classify.py` |
| B4 | `prepare` (strategies S1-S4) and `evaluate` (`add_mcar`, stratified 10-fold cross-validation). S2 removes only training records. | `src/experiment.py` |
| B5 | Kaggle jobs (from number 04): MCAR 0-50% with S1-S4 on all datasets, natural missing values, k = 1-50, 2-8 intervals, 5 or more seeds. Use a sample of `adult` (kNN takes 434 s on all records). | `jobs/runs/` |
| B6 | Figures and tables of the results. | figures, `docs/RESULTS.md` |

Tests to add to `tests/test_core.py`:

- Table 2 of Kryszkiewicz (1998), Example 5.2: the reduct of the table is {Size, Max-Speed}. The local reduct of objects 1 and 2 is {Max-Speed}, of objects 3-6 it is {Size}.
- Example 4.2: the rules are (X, low) → good, (S, compact) → poor, (S, full) → good ∨ excel.

Documentation (Polish):

| Step | Work | Result |
|---|---|---|
| B7 | Chapters 3 (implementation, from `docs/DESIGN.md`), 4 (user guide), 6 (results), 7 (conclusions) and 9 (source code) | `docs/SUMMARY.md` |
| B8 | Presentation of part 2 (main topics of the project) and a demonstration of the software | `.pptx`, demonstration notebook |
| end | `README.md` in English. Upload `docs/SUMMARY.md` (as PDF) to leon before 2027-01-21. | `README.md` |

Questions for the experiments of person B:

- Compare "?" in `voting` as a missing value and as a third value.
- Records with many missing values make the tolerance classes very large (`voting`: one record with 16 missing values). Show this effect in the results.
- `car`: kNN is not better than the mode, because the attributes are independent. Explain this in chapter 7.
