from fastapi import APIRouter
from typing import List
from backend.logic.priors import get_all_priors
from backend.models.prior import Prior

router = APIRouter(prefix="/priors", tags=["priors"])

@router.get("", response_model=None)
async def list_priors():
    return await get_all_priors()
