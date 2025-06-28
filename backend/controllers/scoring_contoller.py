# backend/controllers/scorers.py
from fastapi import APIRouter
from typing import List
from backend.logic.scorers import list_scorers_logic, list_scorer_types_logic, create_scorers_logic
#from backend.models.schemas import Scorer, ScorerType, ScorerCreateRequest

router = APIRouter(prefix="/scorers", tags=["scorers"])

@router.get("", response_model=None)
async def list_scorers():
    return await list_scorers_logic()

@router.get("/types", response_model=None)
async def list_scorer_types():
    return await list_scorer_types_logic()

@router.post("/create" , response_model=None)
async def create_scorers():
    return {"message": "Scorers created", "scorers": []}
