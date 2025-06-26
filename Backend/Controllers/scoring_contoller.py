# backend/controllers/scorers.py
from fastapi import APIRouter
from typing import List
from backend.logic.scorers import list_scorers_logic, list_scorer_types_logic, create_scorers_logic
from backend.models.schemas import Scorer, ScorerType, ScorerCreateRequest

router = APIRouter(prefix="/scorers", tags=["scorers"])

@router.get("", response_model=List[Scorer])
async def list_scorers():
    return await list_scorers_logic()

@router.get("/types", response_model=List[ScorerType])
async def list_scorer_types():
    return await list_scorer_types_logic()

@router.post("/create")
async def create_scorers(reqs: List[ScorerCreateRequest]):
    created = await create_scorers_logic(reqs)
    return {"message": "Scorers created", "scorers": created}
