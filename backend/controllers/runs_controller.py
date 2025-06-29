from typing import List, Optional, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Body, Query
from fastapi.responses import StreamingResponse
# Import logic and schemas
from backend.logic.runs import get_all_runs, create_run_logic
from backend.logic.run_ops import (
    sample_molecules_logic,
    get_molecule_logic,
    score_molecules_logic,
    stage_run_logic,
    duplicate_run_logic,
    transfer_run_logic,
)
from backend.schemas import (
    SampleRequest,
    RunResponse,
    RunCreateRequest,
    MoleculeDetail,
    ScoreRequest,
)

router = APIRouter()

# ---- Runs Endpoints ----
@router.get("/runs", response_model=List[RunResponse], tags=["runs"])
async def list_runs():
    """
    List all runs.
    """
    return await get_all_runs()

@router.post("/runs/create", tags=["runs"])
async def create_run(req: RunCreateRequest):
    """
    Create a new run.
    """
    new_id = await create_run_logic(req)
    return {"message": "Run created", "run_id": new_id}

# ---- Run Operations Endpoints ----
@router.post("/run/sample", tags=["run_operations"])
async def sample_run(req: SampleRequest):
    csv_path = await sample_molecules_logic(req)
    
    # Return the CSV file as a downloadable stream
    return StreamingResponse(
        open(csv_path, mode="rb"),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sampling_results.csv"}
    )


@router.get("/run/molecule/{molecule_id}", response_model=MoleculeDetail, tags=["run_operations"])
async def get_molecule(molecule_id: int):
    """
    Get detailed HTML view of a molecule.
    """
    m = await get_molecule_logic(molecule_id)
    if not m:
        raise HTTPException(status_code=404, detail="Molecule not found")
    return m

@router.put("/run/score", response_model=List[MoleculeDetail], tags=["run_operations"])
async def score_molecules(requests: List[ScoreRequest] = Body(...)):
    """
    Score a list of molecules.
    """
    return await score_molecules_logic(requests)

@router.post("/run/stage", tags=["run_operations"])
async def stage_run(stages: List[Any] = Body(...)):
    """
    Stage a run with given epochs and options.
    """
    count = await stage_run_logic(stages)
    return {"message": "Stages processed", "count": count}

@router.post("/run/duplicate", tags=["run_operations"])
async def duplicate_run(
    run_id: int = Query(...),
    title: str = Query(...),
    model_name: str = Query(...),
    scorer_id: Optional[int] = Query(None),
):
    """
    Duplicate an existing run.
    """
    msg = await duplicate_run_logic(run_id, title, model_name, scorer_id)
    return {"message": msg}

@router.post("/run/transfer", tags=["run_operations"])
async def transfer_run(
    prior_id: int = Form(...),
    agent_name: str = Form(...),
    epochs: int = Form(...),
    file: UploadFile = File(...)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    return await transfer_run_logic(prior_id, agent_name, epochs, file)