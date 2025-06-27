from pydantic import BaseModel
from typing import Optional
class SampleRequest(BaseModel):
    model_path: str
    num_smiles: int = 157
    randomize_smiles: bool = True

class RunResponse(BaseModel):
    run_id: int
    title: str = "Placeholder Run"

class RunCreateRequest(BaseModel):
    title: str

class MoleculeDetail(BaseModel):
    SMILES: str
    score: Optional[float] = None

class ScoreRequest(BaseModel):
    SMILES: str