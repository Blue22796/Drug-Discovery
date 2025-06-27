import os
import shutil
import uuid
from datetime import datetime
import toml
import subprocess

# Base directories (adjust as needed)
PRIORS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend/priors'))
CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), './configs'))

os.makedirs(PRIORS_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

import os
import shutil
from datetime import datetime
from uuid import uuid4
from sqlalchemy.orm import Session
from Models.prior import Prior
from Models.agent import Agent
from db.database import SessionLocal, PRIORS_DIR

def initiate_CL(prior_id: int, model_name: str, db: Session = None) -> Agent:
    # 1) Acquire a session if none provided
    external_session = db is not None
    if not external_session:
        db = SessionLocal()

    try:
        # 2) Fetch the Prior record
        prior = db.query(Prior).get(prior_id)
        if not prior:
            raise ValueError(f"No Prior with ID {prior_id}")

        # 3) Ensure the .prior file exists
        if not os.path.isfile(prior.prior_path):
            raise FileNotFoundError(f"Missing prior file at {prior.prior_path}")

        # 4) Copy the prior file to create the agent checkpoint
        ext = os.path.splitext(prior.prior_path)[1]
        new_filename = f"agent_{datetime.utcnow():%Y%m%d_%H%M%S}_{uuid4().hex}{ext}"
        os.makedirs(PRIORS_DIR, exist_ok=True)
        dest_path = os.path.join(PRIORS_DIR, new_filename)
        shutil.copy(prior.prior_path, dest_path)

        # 5) Create and save the Agent record
        agent = Agent(
            name=model_name,
            prior_id=prior.id,
            takes_file=prior.takes_file,
            epochs=0,
            agent_path=dest_path
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)

        return agent

    finally:
        if not external_session:
            db.close()

global_params = {
    # **Add these two** so the top of your TOML is valid
    "run_type": "staged_learning",
    "device":   "cpu",

    "parameters": {
        "summary_csv_prefix": "my_curriculum_run",
        "batch_size":         64,
        "randomize_smiles":   True,
        "unique_sequences":   True,
    },
    "learning_strategy": {
        "type":  "dap",
        "sigma": 128,
        "rate":  1e-4,
    },
    "diversity_filter": {
        "type":        "IdenticalMurckoScaffold",
        "bucket_size": 25,
        "minscore":    0.4,
    },
}


def perform_stage(
    prior_file: str,
    agent_file: str,
    output_dir: str,
    stage_params: dict,
    toml_prefix: str = "stage"
) -> str:
    """
    Create a unique TOML config for a staged learning stage and invoke REINVENT4.

    Args:
        prior_file: Path to the .prior file for this stage.
        agent_file: Path to the agent (.prior or .chkpt) for this stage.
        output_dir: Directory where checkpoints and logs will be written.
        stage_params: Dict containing stage-specific parameters (epochs, steps, scoring, etc.).
        global_params: Optional dict of the [parameters], [learning_strategy], [diversity_filter] blocks.
        toml_prefix: Prefix for the generated TOML filename (default 'stage').

    Returns:
        toml_path: Path to the generated TOML file.
    """
    # assemble config dict
    config = {}
    if global_params:
        config.update(global_params)

    # Ensure parameters block exists
    if 'parameters' not in config:
        config['parameters'] = {}
    params = config['parameters']
    params['prior_file'] = prior_file
    params['agent_file'] = agent_file
    # you can add more defaults here

    # insert stage block
    if 'stage' not in config:
        config['stage'] = []
    config['stage'].append(stage_params)

    # write TOML
    unique_name = f"{toml_prefix}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex}.toml"
    toml_path = os.path.join(CONFIG_DIR, unique_name)
    with open(toml_path, 'w') as f:
        toml.dump(config, f)

    # invoke REINVENT4
    subprocess.run("reinvent " + toml_path, check=True)
    return toml_path



params = {
    "chkpt_file": "stage1.chkpt",
    "termination": "simple",
    "max_score": 0.6,
    "min_steps": 25,
    "max_steps": 100,
    # This nested dict becomes [stage.scoring] in TOML
    "scoring": {
        "type": "geometric_mean",
        # list of components; each entry becomes a [[stage.scoring.component]]
        "component": [
            {
                # Custom SMARTS‐alerts component
                "custom_alerts": {
                    "endpoint": {
                        "name": "Unwanted SMARTS",
                        "weight": 0.79,
                        "params": {
                            "smarts": [
                                "[*;r8]",
                                "[#8][#8]",
                                "C#C",
                            ]
                        },
                    }
                },
                "comment" : "abcd"
            },
            {
                "MolecularWeight": {
                    "endpoint": {
                        "name": "Molecular weight",
                        "weight": 0.342,
                    },
                    "transform": {
                        "type": "double_sigmoid",
                        "low": 200.0,
                        "high": 500.0,
                        "coef_div": 500.0,
                        "coef_si": 20.0,
                        "coef_se": 20.0,
                    },
                    "comment" : "abcd"
                }
            }
        ]
    }
}
pri = "../../reinvent4/priors/reinvent.prior"
agent = initiate_CL(pri)
perform_stage(pri, agent.agent_path, "../../backend/output/"+pri+agent+"stage_1", params) 