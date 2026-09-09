# hds-practical — Lab 1: Reproducible Computing Setup

Applied / Practical Computing in Health Data Science (PUBH 4201), Fall 2026.

This repo started as the Week 1 practical (`git` + GitHub + a toy patient
roster) and is extended here for **Lab 1**: a reproducible Python
environment managed with [`uv`](https://docs.astral.sh/uv/), a small
deterministic analysis script, a `Dockerfile`, and documentation of the AI
assistance used along the way.

## What's in this repo

| Path | What it is |
|---|---|
| `data/patients.csv` | Toy patient roster (10 rows): `patient_id, age, site, systolic_bp, cohort`. The only input. |
| `src/analysis.py` | Reads `data/patients.csv`, prints a summary, writes `data/age_summary.csv`. |
| `pyproject.toml` | Project + dependency declaration (`pandas`). |
| `uv.lock` | Fully resolved lockfile — the file that makes the environment reproducible. |
| `.python-version` | Shows that I used Python 3.13. |
| `Dockerfile` | Builds a container that reproduces the environment at the OS level. |
| `AI_USAGE.md` | Which AI model was used, for what, and how its suggestions were verified. |

## Prerequisites

- **[`uv`](https://docs.astral.sh/uv/getting-started/installation/)** (tested with 0.10.4). That's it:
  `uv` downloads the correct Python (3.13) itself; you do **not** need conda,
  a system Python, or a manually created virtualenv.
- Optional: **Docker** (tested with 29.x) if you want to run the container instead.

Install `uv` if you don't have it:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Setup

From the repo root, one command builds the environment from the lockfile:

```bash
git clone https://github.com/aadityageddam-ux/hds-practical.git
cd hds-practical
uv sync --locked
```

`uv sync --locked` creates `.venv/` and installs the exact versions pinned
in `uv.lock` (it fails instead of silently drifting if `uv.lock` is out of
date). Expected tail of the output:

```text
Installed 5 packages in ...
 + numpy==2.5.3
 + pandas==3.0.5
 + python-dateutil==2.9.0.post0
 + six==1.17.0
 + tzdata==2026.3
```

## Run the analysis

```bash
uv run python src/analysis.py
```

- **Input:** `data/patients.csv` (already in the repo).
- **Output:** the summary below on stdout, plus a written file
  `data/age_summary.csv` (git-ignored — it is regenerated every run).

Expected output (this is exactly what a fresh `uv sync --locked` produces):

```text
pandas 3.0.5
loaded 10 rows from data/patients.csv

age summary:
count    10.00
mean     56.00
std      11.17
min      39.00
25%      48.00
50%      56.00
75%      64.75
max      72.00

by site:
      n  mean_age  mean_systolic_bp
site
DC    4     52.50            129.00
MD    3     47.67            130.33
VA    3     69.00            147.33

by cohort:
        n  mean_age
cohort
A       5      60.8
B       5      51.2

wrote data/age_summary.csv
```

## Verify reproducibility (the "new teammate" test)

Delete the environment and rebuild it from nothing but the lockfile.

```bash
rm -rf .venv
uv sync --locked
uv run python src/analysis.py   # same output as above
```

## Run it in a container (optional)

```bash
docker build -t hds-practical .
docker run --rm hds-practical
```

`docker run` executes `src/analysis.py` inside the image and prints the
same summary as the native run above. Verified with Docker 29.x: the
container's stdout is byte-for-byte identical to `uv run python
src/analysis.py` run natively.

## Comments for Instructor

- **Environment tool:** `uv` (`pyproject.toml` + `uv.lock`), which the lab
  lists as an alternative to conda/`environment.yml`. conda/mamba
  is not installed on my machine; `uv` is.
- **Container:** the `Dockerfile` is included (undergrad bonus). It follows
  the `uv` image pattern (`FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim`,
  `COPY` the lock files, `uv sync --locked`, `COPY` the code, `CMD` runs the
  script). Verified on my machine:

  ```bash
  docker build -t hds-practical .
  docker run --rm hds-practical   # same output as `uv run python src/analysis.py`
  ```
