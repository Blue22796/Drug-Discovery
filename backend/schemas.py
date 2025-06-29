from pydantic import BaseModel
from typing import Optional , List
class SampleRequest(BaseModel):
    agent_id:          int
    num_smiles:        Optional[int]     = 174
    randomize_smiles:  Optional[bool]    = True

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

class TransferRequest(BaseModel):
    agent_id: int
    epochs: int
    smiles: List[str]