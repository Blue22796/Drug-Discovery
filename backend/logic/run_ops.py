import subprocess
import toml
import pandas as pd 
from pathlib import Path

DIR = Path(__file__).resolve().parent

async def sample_molecules_logic(req):
    toml_config = {
        'run_type': 'sampling',
        'device': 'cuda:0',
        'json_out_config': '_sampling.json',
        'parameters': {
            'model_file': req.model_path,
            'output_file': str(DIR / '../../Backend/Results/sampling.csv'),
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

    csv_path = DIR / '../../Backend/Results/sampling.csv'
    df = pd.read_csv(csv_path)

    result = df.to_dict(orient="records")

    return {
        "message": "Sampling completed",
        "molecules": result
    }



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

async def transfer_run_logic(run_id, epochs, molecules):
    # Placeholder: return dummy message
    return f"Transferred {len(molecules)} molecules to run {run_id} with {epochs} epochs"
