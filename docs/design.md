# Design of the implementation

Part 1 of the MED project: inference from incomplete data.

This document describes the complete implementation. It also describes the modules that are not written yet (marked "planned").

## 1. Scope

The project compares 4 strategies for missing values in a classification task:

| No. | Strategy | Source |
|---|---|---|
| S1 | Rough sets with the tolerance relation on the raw data | Kryszkiewicz (1998) |
| S2 | Removal of the incomplete training records, then S1 | Kryszkiewicz (1998), section 6 |
| S3 | Mean or mode imputation, then S1 | common baseline |
| S4 | kNN imputation, then S1 | Troyanskaya et al. (2001) |

All 4 strategies use the same classifier: decision rules from the rough set model. Thus the comparison shows only the effect of the strategy for missing values.

The tests measure these properties:

- the quality of the classification and of the imputation at different levels of missing values (0-50%),
- the effect of the parameters (k of kNN, number of intervals of the discretization),
- the run time and the scalability for the number of records and the number of attributes.

## 2. Technologies

| Item | Selection | Reason |
|---|---|---|
| Language | Python 3.12 (local), 3.13 (Kaggle) | popular, good libraries for tables and arrays |
| Tables | pandas | reading of the UCI files, types of the columns |
| Arrays | numpy | vector operations, bit sets of `uint64` |
| Tests | pytest | short tests of each module |
| Compute | Kaggle CPU kernels (4 cores, 30 GB RAM) | the local machine is small |
| Version control | git, GitHub (public repository) | Kaggle kernels clone the code |

The project does not use a library for rough sets or for imputation. All algorithms are our own implementation.

## 3. Structure of the implementation

```
src/
  data.py        load the 6 datasets in one common form
  missing.py     simulation of missing values (MCAR)
  impute.py      kNN imputation, mean or mode imputation, error of an imputation
  rough.py       discretization, tolerance classes, approximations, generalized decision,
                 reducts and decision rules (planned)
  classify.py    classifier with the decision rules (planned)
  experiment.py  the 4 strategies with cross-validation (planned)
tests/
  test_core.py   tests of all modules
jobs/runs/       one folder for each Kaggle job (run.py, kernel-metadata.json, small outputs)
```

The flow of the data:

```
load_dataset --> add_mcar --> [S2: remove | S3: impute_mean_mode | S4: impute_knn] -->
cut_points / discretize --> encode --> tolerance_classes --> generalized_decision -->
local reducts --> decision rules --> classify --> accuracy
```

### 3.1. `src/data.py`

| Function | Step | Description |
|---|---|---|
| `download_all(out)` | data | Downloads the 6 UCI zip files. Writes `manifest.json` with the sizes and the SHA-256 hashes. |
| `data_dir()` | data | Finds the data on Kaggle (`/kaggle/input`) or on the local machine (`data/`). |
| `load_dataset(name)` | data | Gives each dataset in the common form (section 4.1). |
| `numeric_attributes(df)` | data | Gives the names of the numeric attributes. |

`SPECS` is a dictionary. For each dataset, it has the files, the column names, the class column and the numeric columns.

### 3.2. `src/missing.py`

| Function | Step | Description |
|---|---|---|
| `add_mcar(df, fraction, seed)` | simulation | Removes a fraction of the known attribute values at random. Each known value has the same probability (MCAR). The class is not changed. Gives the new table and a mask of the removed values. |

### 3.3. `src/impute.py`

| Function | Step of Troyanskaya et al. (2001) | Description |
|---|---|---|
| `impute_mean_mode(df)` | baseline ("row average") | Mean for a numeric attribute, mode for a symbolic attribute. |
| `_encode(df)` | preparation | Numeric values as floats, symbolic values as category codes, `NaN` if missing. |
| `_gower_distances(values, is_numeric, rows)` | 1. distance to the other records | Gower distance on the attributes that the two records both have (section 5.1). |
| `impute_knn(df, k)` | 2. select the k nearest records that have the value; 3. weighted average | Weight 1 / distance. Weighted mean (numeric), weighted mode (symbolic). Fallback: mean or mode. |
| `imputation_error(true, imputed, removed)` | evaluation (normalized RMS error) | `nrmse` on the numeric attributes, `error_rate` on the symbolic attributes. |

### 3.4. `src/rough.py`

Definitions of Kryszkiewicz (1998). An information system is S = (U, AT ∪ {d}). The value `*` is a missing value.

| Function | Definition in Kryszkiewicz (1998) | Description |
|---|---|---|
| `cut_points(df, bins)`, `discretize(df, cuts)` | preparation (the paper uses only symbolic values) | Equal-frequency intervals from the known values. |
| `encode(df)` | S = (U, AT ∪ {d}) | Matrix of codes, -1 is `*`. Vector of decision codes. |
| `pack`, `unpack`, `count` | sets of objects | Bit sets of `uint64` words (section 4.2). |
| `tolerance_classes(codes, B)` | SIM(B) = {(x, y): ∀a ∈ B, a(x) = a(y) ∨ a(x) = * ∨ a(y) = *}, I_B(x) = {y: (x, y) ∈ SIM(B)} | One bit set for each object (section 5.2). |
| `lower_approximation(classes, X)` | X_B = {x ∈ U: I_B(x) ⊆ X} | Bit operations on each row. |
| `upper_approximation(classes, X)` | X^B = {x ∈ U: I_B(x) ∩ X ≠ ∅} | Bit operations on each row. |
| `generalized_decision(classes, d)` | ∂_B(x) = {d(y): y ∈ I_B(x)} | Boolean matrix objects x decisions. |
| `discernibility(codes, general, i)` (planned, B1) | c_ij = {a ∈ AT: a(x_i) ≠ *, a(x_j) ≠ *, a(x_i) ≠ a(x_j)} if d(x_j) ∉ ∂_AT(x_i), else c_ij = ∅ | Row i of the discernibility matrix, as one attribute mask (`uint64`) for each object j. |
| `local_reduct(codes, general, i)` (planned, B1) | a minimal B ⊆ AT with ∂_B(x_i) = ∂_AT(x_i): a prime implicant of the function Π_{j: c_ij ≠ ∅} Σ c_ij | Greedy set cover: add the attribute that is in the most uncovered c_ij. Then remove the attributes that are not necessary. |
| `reduct(codes, general)` (planned, B1) | a minimal B ⊆ AT with ∂_B = ∂_AT for all objects | The same greedy method on all pairs (i, j). |
| `rules(codes, d, general)` (planned, B2) | optimal rule for x_i: ∧_{a ∈ B, a(x_i) ≠ *} (a = a(x_i)) → d ∈ ∂_AT(x_i) | One rule from the local reduct of each object. A rule is certain if \|∂(x_i)\| = 1, otherwise it is possible. Duplicate rules are joined, the support is added. |

The exact set of all reducts needs all prime implicants. This is exponential in the number of attributes, so the project uses the greedy heuristic.

### 3.5. `src/classify.py` (planned, B3)

| Function | Description |
|---|---|
| `RuleClassifier(bins)` | Keeps the cut points, the rules and the most frequent class of the training records. |
| `fit(df)` | `cut_points`, `discretize`, `encode`, `tolerance_classes`, `generalized_decision`, `rules`. |
| `predict(df)` | A rule matches a record z if, for each condition a = v, a(z) = v or a(z) = `*`. Each matching rule gives its support to each decision in its right side. The decision with the largest sum wins. If no rule matches, the result is the most frequent class. |

### 3.6. `src/experiment.py` (planned, B4)

| Function | Description |
|---|---|
| `prepare(train, test, strategy, k)` | Applies S1-S4 (section 1). S2 removes only training records. S3 and S4 impute the attributes of all records, but they do not use the class. |
| `evaluate(name, fraction, strategy, seed, folds=10, k=10, bins=4)` | `add_mcar`, stratified cross-validation, `prepare`, `RuleClassifier`. Gives accuracy, coverage (fraction of the test records that a rule matches), number of rules and run time. |

## 4. Data structures

### 4.1. Source data

`load_dataset` gives a `pandas.DataFrame`:

- one row for each record, one column for each attribute, the column `class` at the end,
- numeric attribute: type `float64`, missing value `NaN`,
- symbolic attribute and class: type `category`, missing value `NaN` (code -1).

| Dataset | Records | Attributes (numeric) | Missing cells | Incomplete records | Classes |
|---|---|---|---|---|---|
| `voting` | 435 | 16 (0) | 5.63% | 46.7% | 2 |
| `hepatitis` | 155 | 19 (6) | 5.67% | 48.4% | 2 |
| `mushroom` | 8124 | 22 (0) | 1.39% | 30.5% | 2 |
| `car` | 1728 | 6 (0) | 0% | 0% | 4 |
| `wdbc` | 569 | 30 (30) | 0% | 0% | 2 |
| `adult` | 48842 | 14 (6) | 0.95% | 7.4% | 2 |

The mask of `add_mcar` is a boolean `numpy` array (records x attributes). It gives the positions of the true values for `imputation_error`.

### 4.2. Data structures of the algorithms

| Structure | Type and shape | Memory | Use |
|---|---|---|---|
| attribute codes | `int32`, n x m, -1 is `*` | 4nm bytes | all rough set functions |
| decision codes | `int32`, n | 4n bytes | generalized decision, rules |
| set of objects | `uint64`, ceil(n / 64) words, bit y is object y | n / 8 bytes | X, I(x), decision classes |
| tolerance classes | `uint64`, n x ceil(n / 64) | n^2 / 8 bytes (`adult`: 299 MB) | approximations, generalized decision |
| S(a, v) | `uint64`, (values + 1) x ceil(n / 64) for each attribute | sum of values x n / 8 bytes | construction of the tolerance classes |
| generalized decision | `bool`, n x number of decisions | n x decisions bytes | reducts, rules |
| row of the discernibility matrix | `uint64`, n, bit a is attribute a (m ≤ 64) | 8n bytes | local reduct |
| rule | conditions (attribute index, value code), decision set (bit mask), support | small | classifier |
| kNN block of distances | `float64`, block x n | at most 5 million values (40 MB) | kNN imputation |

The bit sets make the tolerance classes fast: one AND of two 64-bit words compares 64 objects. `numpy.bitwise_count` counts the members of a set.

## 5. Algorithms

### 5.1. kNN imputation (Troyanskaya et al. 2001)

For each record x with missing values:

1. Calculate the distance from x to all records. The distance uses only the attributes that both records have. Gower distance: |x_a - y_a| / range(a) for a numeric attribute, 0 or 1 for a symbolic attribute, the mean over the common attributes.
2. For each missing attribute a of x, select the k nearest records that have a value of a.
3. Estimate a(x): the weighted mean (numeric) or the weighted mode (symbolic) of the k values. The weight is 1 / distance.

Changes from the paper:

- The paper has only numeric values (gene expression) and the Euclidean distance. Our datasets are mixed, so we use the Gower distance.
- The paper divides the RMS error by the mean of the data. Our attributes have different scales, so we divide the error of each attribute by its standard deviation.

### 5.2. Tolerance classes (Kryszkiewicz 1998)

For each attribute a and each value v, make the bit set S(a, v) = {y: a(y) = v or a(y) = *}. Then:

I_B(x) = ∩_{a ∈ B, a(x) ≠ *} S(a, a(x)).

The code makes the matrix in blocks of rows, so the memory of the temporary arrays stays small.

### 5.3. Reducts and rules (planned)

1. Calculate ∂_AT(x) for each object.
2. For each object x_i, calculate the row c_ij of the discernibility matrix as attribute masks.
3. Find a local reduct with the greedy set cover.
4. Make the rule of x_i from its local reduct and ∂_AT(x_i).

## 6. Efficiency

n is the number of records, m the number of attributes, n_inc the number of incomplete records, k the number of neighbours, D the number of decisions.

| Operation | Time | Memory |
|---|---|---|
| `load_dataset` | O(nm) | O(nm) |
| `add_mcar` | O(nm) | O(nm) |
| `impute_mean_mode` | O(nm) | O(nm) |
| `impute_knn` | O(n_inc · n · m) | O(block · n) |
| `tolerance_classes` | O(m · n^2 / 64) | O(n^2 / 8) |
| approximation of one set | O(n^2 / 64) | O(n) |
| `generalized_decision` | O(D · n^2 / 64) | O(nD) |
| local reduct of one object (planned) | O(nm + n m^2) | O(n) |
| rules of all objects (planned) | O(n^2 m^2) | O(nm) |
| `predict` of t records (planned) | O(t · rules · m) | O(t · rules / 8) |

The tolerance classes are not the slow part: `adult` (48842 records) needs 1.7 s on the local CPU. The kNN imputation is the slow part when many records are incomplete. The rules of all objects are the slowest planned step. For `adult` they need a sample of the records.

### 6.1. Measured run times

The job `timing` (`jobs/runs/2026-11-26_03_timing/`) measured the run times on a Kaggle CPU (4 cores, Python 3.13, numpy 2.1.3). Each value is the median of 3 seeds. The fraction of MCAR values is 10%, k = 10.

Number of records (`adult`, complete records, 14 attributes):

| Records | kNN (s) | Tolerance classes (s) | Mean \|I(x)\| |
|---|---|---|---|
| 1000 | 0.17 | 0.001 | 1.8 |
| 2000 | 0.62 | 0.003 | 2.8 |
| 5000 | 4.7 | 0.011 | 5.0 |
| 10000 | 18.7 | 0.063 | 9.3 |
| 20000 | 82.5 | 0.37 | 17.2 |
| 45222 | 434 | 1.76 | 38.4 |

From 20000 to 45222 records (x 2.26), the time of kNN grows x 5.3 and the time of the tolerance classes grows x 4.8. Both agree with O(n^2) (2.26^2 = 5.1).

Number of attributes (`wdbc` 569 records, `mushroom` 8124 records):

| Dataset | Attributes | kNN (s) | Tolerance classes (s) | Mean \|I(x)\| |
|---|---|---|---|---|
| `wdbc` | 5 / 10 / 20 / 30 | 0.015 / 0.035 / 0.086 / 0.128 | 0.0004 / 0.0006 / 0.0013 / 0.0016 | 21.4 / 2.5 / 1.0 / 1.0 |
| `mushroom` | 5 / 10 / 15 / 22 | 2.7 / 6.8 / 12.1 / 18.1 | 0.016 / 0.025 / 0.039 / 0.050 | 233 / 84 / 19.5 / 6.5 |

The time grows approximately linearly with m, as in the table above. More attributes make the tolerance classes smaller.

Fraction of missing values (`car` 1728 records, `mushroom` 8124 records):

| Fraction | 0% | 10% | 20% | 30% | 40% | 50% |
|---|---|---|---|---|---|---|
| `car` kNN (s) | 0.004 | 0.10 | 0.21 | 0.28 | 0.31 | 0.33 |
| `car` mean \|I(x)\| | 1 | 10 | 47 | 134 | 297 | 535 |
| `mushroom` kNN (s) | 5.5 | 18.2 | 21.7 | 24.8 | 27.8 | 30.9 |
| `mushroom` mean \|I(x)\| | 1 | 6.5 | 26 | 78 | 212 | 563 |

The time of kNN grows with the number of incomplete records n_inc. The time of the tolerance classes does not depend on the fraction (`car` 0.001 s, `mushroom` 0.05 s). The tolerance classes grow very fast with the fraction: at 50%, one class of `car` has 31% of all records. Thus the generalized decision has more decisions and the rules become less certain.

The number of neighbours k = 1-50 has no effect on the time of kNN (`wdbc`: 0.13 s for each k). The distances are the slow part, not the selection of the neighbours.

## 7. Test plan

### 7.1. Tests of the code (`tests/test_core.py`)

- `load_dataset`: the numbers of records, attributes and numeric attributes agree with the UCI descriptions.
- `add_mcar`: the fraction of removed values is correct, the class and the types do not change, the same seed gives the same table.
- `impute_knn`: no missing values after the imputation, the types do not change, the error is smaller than the error of the mean or mode.
- `tolerance_classes`: Table 2 of Kryszkiewicz (1998) gives the tolerance classes, the generalized decisions and the approximations of the paper. On 4 datasets, the bit sets are equal to a direct calculation of SIM.
- Planned: the reducts and the rules of Table 2 agree with the paper.

### 7.2. Experiments (Kaggle CPU)

| Study | Datasets | Parameters | Measures |
|---|---|---|---|
| Robustness to missing values | all 6 (`adult`: a sample) | MCAR 0, 5, 10, 20, 30, 40, 50%; strategies S1-S4 | accuracy, coverage, number of rules |
| Natural missing values | `voting`, `hepatitis`, `mushroom`, `adult` | strategies S1-S4 | accuracy, coverage |
| Quality of the imputation | `wdbc`, `hepatitis`, `voting`, `car` | MCAR 5-50%; k = 1, 5, 10, 20, 50 | nrmse, error rate |
| Discretization | `wdbc`, `hepatitis` | 2, 3, 4, 6, 8 intervals | accuracy |
| Scalability (records) | `adult` | 1000 to 45222 records | run time |
| Scalability (attributes) | `wdbc`, `mushroom` | 5 to 30 attributes | run time |

Each result is the mean of 5 or more seeds of `add_mcar` and stratified 10-fold cross-validation.

## 8. References

- Kryszkiewicz, M. (1998). Rough set approach to incomplete information systems. *Information Sciences*, 112(1-4), 39-49.
- Troyanskaya, O., Cantor, M., Sherlock, G., Brown, P., Hastie, T., Tibshirani, R., Botstein, D., Altman, R. B. (2001). Missing value estimation methods for DNA microarrays. *Bioinformatics*, 17(6), 520-525.
- Dua, D., Graff, C. (2019). UCI Machine Learning Repository. University of California, Irvine.
