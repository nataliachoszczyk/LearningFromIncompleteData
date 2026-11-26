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
| 2026-11-26 | smoke | `2026-11-26_01_smoke` | [med-smoke](https://www.kaggle.com/code/nataliachoszczyk/med-smoke) | Test of the setup: clone of the repository, versions of the libraries, CPU count | to run |
