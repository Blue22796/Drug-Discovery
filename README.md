[readme(1).md](https://github.com/user-attachments/files/22130412/readme.1.md)# Drug-Discovery

[![Project Status](https://img.shields.io/badge/status-experimental-orange.svg)](https://github.com/Blue22796/Drug-Discovery)

> **REINVENT4-inspired molecular generative & sampling system**

---

A compact, reproducible codebase implementing a sampling pipeline for molecular generation inspired by REINVENT4. This repo contains configuration-driven sampling, a lightweight backend and frontend for experiment control, and a local SQLite database for storing traces.

---

## Highlights

- ✅ **Reproducible experiments** via `sampling.toml` / `_sampling.json` configuration files
- ✅ **Lightweight orchestration**: `main.py` runs sampling jobs and persists results to `reinvent.db`
- ✅ **Small frontend + backend** for launching and browsing experiments (prototype)
- ✅ **Designed for extension** — plug in model checkpoints, scoring functions, or cheminformatics tools

---

## Quick links
- `main.py` — sampling orchestration
- `sampling.toml` — example config (tune hyperparameters here)
- `_sampling.json` — example recorded sampling profile / trace
- `reinvent.db` — SQLite database with results
- `backend/`, `frontend/` — minimal UI and API

---

## Table of contents
1. [Quick Start](#quick-start)
2. [How it works](#how-it-works)
3. [Configuration](#configuration)
4. [Database & results](#database--results)
5. [Frontend / Backend](#frontend--backend)
6. [Extending the project](#extending-the-project)
7. [Contributing](#contributing)
8. [License](#license)

---

## Quick Start
> Minimal steps to run a sampling experiment locally.

```bash
# 1. clone
git clone https://github.com/Blue22796/Drug-Discovery.git
cd Drug-Discovery

# 2. create venv and install (edit requirements.txt as needed)
python -m venv venv
source venv/bin/activate    # Windows: venv\\Scripts\\activate
pip install -r requirements.txt

# 3. run the backend server
python main.py
```

> Note: if `requirements.txt` is missing, add `numpy pandas sqlite3 flask` and any ML / chemistry packages you need (e.g. `rdkit`, `torch`).

---

## How it works (high level)

The system is driven by backend APIs that expose multiple **run modes** (for example: `sample`, `optimize`, `fine-tune`, `inference`). The typical user workflow is:

1. **Frontend → Backend:** The frontend UI collects user inputs (target properties, scoring weights, filters, budget, run mode, etc.) and submits a run request to the backend API (e.g. `POST /runs`).

2. **Config generation:** The backend validates parameters and programmatically generates reproducible configuration files (TOML/JSON). These files capture the exact model checkpoint, scoring functions, sampling hyperparameters and filters used for the run.

3. **Launch RL / sampling loop:** Depending on the requested run mode, the backend assembles the appropriate REINVENT invocation and launches the reinforcement-learning or sampling loop (either by invoking `main.py`, a CLI, or a worker process). The backend manages the run lifecycle (start, monitor, pause/resume, cancel).

4. **Streaming & persistence:** As the run proceeds the backend streams progress, logs and intermediate candidates to the `reinvent.db` database and to any subscribed frontend clients (via REST/WebSocket endpoints). Results include generated SMILES, scores, and run metadata.

5. **Frontend interaction & control:** The frontend provides interactive controls for users to inspect live results, download the exact TOML/JSON used for a run, and adjust or relaunch experiments.

**Implementation notes:**
- Backend endpoints are responsible for configuration generation, job orchestration, and persisting results.
- The generated TOML/JSON files are stored alongside run metadata so experiments are fully reproducible.
- The modular design lets you swap scoring components, model checkpoints, or the persistence layer without changing the UI.

---

## Configuration
Open `sampling.toml` to see a documented example. Typical sections:

- `model` — model checkpoint paths and model type
- `sampling` — number of samples, batch sizes, temperature / exploration parameters
- `filters` — post-generation filters (e.g., QED, MW, or custom Python callbacks)
- `logging` — where to persist logs and DB connection

**Tip:** keep sampling configs small and version-controlled so experiments are reproducible.

---

## Database & results
Results are stored in the SQLite file `reinvent.db`. The schema is lightweight and includes tables for:
- `runs` — run metadata + config
- `molecules` — generated items, SMILES, scores, and timestamps
- `metrics` — aggregated statistics per run

Use `sqlite3` or a GUI (DB Browser for SQLite) to explore. Export to CSV for downstream analysis.

---

## Frontend / Backend
A prototype frontend is available in `frontend/` and a small Python backend in `backend/`.

To run server:
```bash
python main.py
```
---

## Extending the project
Ideas to extend:
- Add GPU model support and model checkpoints for generative models
- Replace SQLite with PostgreSQL for multi-user experiments
- Add experiment dashboards with plots and metrics

---

## Example: Interpreting a sampling run
A typical sampling run is saved to reinvent.db. Use the corresponding API endpoints to retrieve a run summary and the top-scoring molecules.

**Example curl (download CSV):**

```bash
curl -X POST "http://localhost:8000/run/sample" \
-H "Content-Type: application/json" \
-d '{"agent_id": 42, "num_smiles": 100, "randomize_smiles": true}' \
--output sampling_results.csv
```

---

<!-- end of README -->

