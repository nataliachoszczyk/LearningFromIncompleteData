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
