from fastapi import FastAPI, APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional, Any
import uvicorn

app = FastAPI(title="Drug Discovery", version="0.1.0")

# In-memory dummy storage with initial values
from datetime import date as _date

# Priors
# id, name, description
display_priors = [
    {"id": 1, "name": "Default Prior", "description": "A default prior for baseline."},
    {"id": 2, "name": "Advanced Prior", "description": "An advanced prior for deep search."}
]

# Model metadata nested inside runs
# Runs: id, title, creation_date, model_id, model
display_runs = [
    {
        "id": 1,
        "title": "Initial Test Run",
        "creation_date": _date(2025, 6, 25),
        "model_id": 1,
        "model": {
            "id": 1,
            "name": "TestModelV1",
            "description": "Dummy model for initial run",
            "epochs": 5,
            "parent_id": None,
            "run_id": 1
        }
    }
]

# Scorer types
display_scorer_types = [
    {"id": 1, "title": "Regression"},
    {"id": 2, "title": "Classification"}
]

# Scorers: id, type_id, type, run_id
display_scorers = [
    {"id": 1, "type_id": 1, "type": "Regression", "run_id": 1}
]

# Molecules: id, SMILES, run_id, score
display_molecules = [
    {"id": 1, "SMILES": "CCO", "run_id": 1, "score": 0.45},
    {"id": 2, "SMILES": "C1CCCCC1", "run_id": 1, "score": 0.78},
    {"id": 3, "SMILES": "O=C=O", "run_id": 1, "score": 0.12}
]

# Pydantic models
class Prior(BaseModel):
    id: int
    name: str
    description: str

class ModelMeta(BaseModel):
    id: int
    name: str
    description: str
    epochs: int
    parent_id: Optional[int]
    run_id: Optional[int]

class RunResponse(BaseModel):
    id: int
    title: str
    creation_date: date
    model_id: int
    model: ModelMeta

class RunCreateRequest(BaseModel):
    title: str
    prior_id: int = Field(..., alias="priod_id")
    model_name: str
    scorer_id: Optional[int] = None

class Scorer(BaseModel):
    id: int
    type_id: int
    type: str
    run_id: int

class ScorerType(BaseModel):
    id: int
    title: str

class Molecule(BaseModel):
    id: int
    SMILES: str
    run_id: int
    score: float

class MoleculeDetail(Molecule):
    view: str

class ScoreRequest(BaseModel):
    SMILES: str

# Routers
prior_router = APIRouter(prefix="/priors", tags=["priors"])

@prior_router.get("", response_model=List[Prior])
def list_priors():
    return display_priors

run_router = APIRouter(prefix="/runs", tags=["runs"])

@run_router.get("", response_model=List[RunResponse])
def list_runs():
    return display_runs

@run_router.post("/create")
def create_run(req: RunCreateRequest):
    new_id = len(display_runs) + 1
    run_date = date.today()
    model_meta = ModelMeta(
        id=new_id,
        name=req.model_name,
        description="Generated model",
        epochs=0,
        parent_id=None,
        run_id=new_id
    )
    run_obj = RunResponse(
        id=new_id,
        title=req.title,
        creation_date=run_date,
        model_id=new_id,
        model=model_meta
    )
    display_runs.append(run_obj.dict())
    return {"message": "Run created", "run_id": new_id}

scorer_router = APIRouter(prefix="/scorers", tags=["scorers"])

@scorer_router.get("", response_model=List[Scorer])
def list_scorers():
    return display_scorers

@scorer_router.get("/types", response_model=List[ScorerType])
def list_scorer_types():
    return display_scorer_types

class ScorerCreateRequest(BaseModel):
    type_id: int
    run_id: int

@scorer_router.post("/create")
def create_scorers(reqs: List[ScorerCreateRequest]):
    created = []
    for req in reqs:
        new_id = len(display_scorers) + 1
        typ = next((t for t in display_scorer_types if t['id'] == req.type_id), None)
        type_title = typ['title'] if typ else "Unknown"
        scorer = Scorer(id=new_id, type_id=req.type_id, type=type_title, run_id=req.run_id)
        display_scorers.append(scorer.dict())
        created.append(scorer.dict())
    return {"message": "Scorers created", "scorers": created}

run_ops_router = APIRouter(prefix="/run", tags=["run_operations"])

@run_ops_router.put("/sample", response_model=List[Molecule])
def sample_run(run_id: int = Query(...)):
    return [m for m in display_molecules if m['run_id'] == run_id]

@run_ops_router.put("/molecules", response_model=List[Molecule])
def put_molecules(run_id: int = Query(...)):
    return [m for m in display_molecules if m['run_id'] == run_id]

@run_ops_router.get("/molecules", response_model=List[Molecule])
def get_molecules(run_id: int = Query(...)):
    return [m for m in display_molecules if m['run_id'] == run_id]

@run_ops_router.get("/molecule/{molecule_id}", response_model=MoleculeDetail)
def get_molecule(molecule_id: int):
    m = next((m for m in display_molecules if m['id'] == molecule_id), None)
    if not m:
        raise HTTPException(status_code=404, detail="Molecule not found")
    return MoleculeDetail(**m, view=f"<html><body><h1>{m['SMILES']}</h1></body></html>")

@run_ops_router.put("/score", response_model=List[Molecule])
def score_molecules(requests: List[ScoreRequest] = Body(...)):
    result = []
    for idx, req in enumerate(requests, start=1):
        result.append({"id": idx, "SMILES": req.SMILES, "run_id": 0, "score": 0.0})
    return result

@run_ops_router.post("/stage")
def stage_run(stages: List[Any] = Body(...)):
    return {"message": "Stages processed", "count": len(stages)}

@run_ops_router.post("/duplicate")
def duplicate_run(run_id: int = Query(...), title: str = Query(...), model_name: str = Query(...), scorer_id: Optional[int] = Query(None)):
    return {"message": f"Run {run_id} duplicated as '{title}' with model '{model_name}' and scorer {scorer_id}"}

@run_ops_router.post("/transfer")
def transfer_run(run_id: int = Query(...), epochs: int = Query(...), molecules: List[ScoreRequest] = Body(...)):
    return {"message": f"Transferred {len(molecules)} molecules to run {run_id} for {epochs} epochs"}

# Include routers
app.include_router(prior_router)
app.include_router(run_router)
app.include_router(scorer_router)
app.include_router(run_ops_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Molecule Run API"}

if __name__ == "__main__":
    # Start Uvicorn server when running `python main.py`
    uvicorn.run("dummies:app", host="0.0.0.0", port=8000, reload=True)
