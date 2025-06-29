import subprocess
import toml
import pandas as pd 
from sqlalchemy.orm import Session
from backend.models.agent import Agent
from backend.database.database import SessionLocal
from backend.logic.data_proc import process_transfer_learning_csv
from pathlib import Path
from backend.models.prior import Prior
from fastapi import UploadFile, HTTPException
import shutil


DIR = Path(__file__).resolve().parent

async def sample_molecules_logic(req):
    db: Session = SessionLocal()
    agent = db.query(Agent).get(req.agent_id)
    if not agent:
        raise ValueError(f"No agent with id={req.agent_id}")
    
    output_csv = DIR / '../../backend/results/sampling.csv'

    toml_config = {
        'run_type': 'sampling',
        'device': 'cpu',
        'json_out_config': '_sampling.json',
        'parameters': {
            'model_file': agent.agent_path,
            'output_file': str(output_csv),
            'num_smiles': req.num_smiles,
            'randomize_smiles': req.randomize_smiles,
            'unique_molecules': True
        }
    }

    with open('sampling.toml', 'w') as f:
        toml.dump(toml_config, f)

    process = subprocess.run(
        "conda run -n reinvent4 reinvent sampling.toml", 
        shell=True, 
        capture_output=True,
        text=True
    )

    if process.returncode != 0:
        raise Exception(f"Sampling failed: {process.stderr}")

    # Just return the path — the route handles reading it
    return output_csv



async def get_molecule_logic(molecule_id):
    # Placeholder: return dummy molecule or None
    if molecule_id == 1:
        return {"SMILES": "CCO", "score": 0.85}
    return None

async def score_molecules_logic(requests):
    # Placeholder: just echo back with a dummy score
    return [{"SMILES": r.SMILES, "score": 0.9} for r in requests]

async def stage_run_logic(stages):
    # Placeholder: return count of stages
    return len(stages)

async def duplicate_run_logic(run_id, title, model_name, scorer_id):
    # Placeholder: return dummy message
    return f"Run {run_id} duplicated as {title} with model {model_name}"

async def transfer_run_logic(prior_id: int, agent_name: str, epochs: int, file: UploadFile):

    # Save uploaded CSV
    upload_dir = Path("backend/uploads") / f"prior_{prior_id}_{agent_name}"
    upload_dir.mkdir(parents=True, exist_ok=True)
    csv_path = upload_dir / file.filename

    with open(csv_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Process CSV: shuffle, split, write .smi files
    smi_paths = process_transfer_learning_csv(csv_path, upload_dir)

    # Create TOML config
    toml_config = {
        "run_type": "transfer_learning",
        "device": "cuda:0",
        "json_out_config": str(upload_dir / "transfer_config.json"),
        "parameters": {
            "num_epochs": epochs,
            "save_every_n_epochs": epochs,
            "batch_size": 50,
            "num_refs": 100,
            "sample_batch_size": 100,
            "input_model_file": f"REINVENT4/priors/reinvent.prior",
            "smiles_file": str(smi_paths["train_smi"]),
            "validation_smiles_file": str(smi_paths["val_smi"]),
            "output_model_file": str(upload_dir / f"{agent_name}.model"),
        }
    }

    toml_path = upload_dir / "transfer_learning.toml"
    with open(toml_path, "w") as f:
        toml.dump(toml_config, f)

    # Run REINVENT
    process = subprocess.run(
        f"conda run -n reinvent4 reinvent {toml_path}",
        shell=True,
        capture_output=True,
        text=True
    )

    if process.returncode != 0:
        raise HTTPException(status_code=500, detail=f"REINVENT failed: {process.stderr}")

    # Save agent to DB
    db = SessionLocal()
    prior = db.query(Prior).get(prior_id)
    if not prior:
        raise HTTPException(status_code=404, detail="Prior not found")

    agent = Agent(
        name=agent_name,
        prior_id=prior_id,
        takes_file=True,
        epochs=epochs,
        agent_path=str(upload_dir / f"{agent_name}.model")
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)

    return {
        "message": "Transfer learning completed and agent saved.",
        "agent_id": agent.id,
        "agent_name": agent.name,
        "model_path": agent.agent_path
    }

