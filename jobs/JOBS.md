# Jobs

All Kaggle jobs of the project. The full rules are in `KAGGLE.md`. All jobs run on the account `nataliachoszczyk`.

## Procedure

1. Commit and push the code.
2. Add a row to the table with the status `to run`.
3. Push the kernel and follow it:

   ```bash
   bash jobs/kaggle.sh kernels push -p jobs/runs/YYYY-MM-DD_NN_<job name>
   bash jobs/wait.sh nataliachoszczyk/med-<job name> <job name>
   ```

4. List the outputs, then download only the small files:

   ```bash
   bash jobs/kaggle.sh kernels files nataliachoszczyk/med-<job name>
   bash jobs/kaggle.sh kernels output nataliachoszczyk/med-<job name> -p jobs/runs/YYYY-MM-DD_NN_<job name>/output --file-pattern '(json|csv|png)$'
   ```

## Status values

Use only these values in the column Status: to run, waiting for another job, queued, running, complete, failed, cancelled. `wait.sh` changes the status cell, so the cell has one value and no other text. Put results into the column Comment.

| Date | Job | Folder | Link | Comment | Status |
|---|---|---|---|---|---|
| 2026-11-26 | smoke | `2026-11-26_01_smoke` | [med-smoke](https://www.kaggle.com/code/nataliachoszczyk/med-smoke) | Test of the setup. Version 1: the clone and the import of `src` work. Kaggle has Python 3.13.18, 4 CPUs, numpy 2.1.3, pandas 2.3.3, scipy 1.16.3, scikit-learn 1.6.1 | complete |
| 2026-11-26 | data | `2026-11-26_02_data` | [med-data](https://www.kaggle.com/code/nataliachoszczyk/med-data) | Download of the 6 UCI datasets (voting, hepatitis, mushroom, car, wdbc, adult). Version 1: complete in 1 minute. The output is the private dataset `nataliachoszczyk/med-datasets` (6.5 MB) | complete |
| 2026-11-26 | timing | `2026-11-26_03_timing` | [med-timing](https://www.kaggle.com/code/nataliachoszczyk/med-timing) | Run times of the kNN imputation and of the tolerance classes: records (adult, 1000-45222), attributes (wdbc, mushroom), fraction of missing values 0-50% (car, mushroom), k = 1-50 (wdbc). 10% MCAR, 3 repeats, median | to run |
