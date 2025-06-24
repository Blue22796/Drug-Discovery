from molSimplify.Classes.mol3D import mol3D
from rdkit import Chem
from rdkit.Chem import AllChem
import py3Dmol
import pandas as pd
import subprocess
import toml

def visualize_3d_from_smiles(smiles, output_html="mol_view.html"):
    mol = Chem.MolFromSmiles(smiles)
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol, AllChem.ETKDG())
    AllChem.UFFOptimizeMolecule(mol)
    block = Chem.MolToMolBlock(mol)

    viewer = py3Dmol.view(width=400, height=400)
    viewer.addModel(block, 'mol')
    viewer.setStyle({'stick': {}})
    viewer.zoomTo()
    
    # Save to HTML file
    with open(output_html, "w") as f:
        f.write(viewer._make_html())
    print(f"Visualization saved to {output_html}")
    
def create_toml(num_smiles = 157, randomize_smiles = True):
   
    config = {}
    config['run_type'] = 'sampling'
    config['device'] = 'cpu'
    config['json_out_config'] = '_sampling.json'
    
    config['parameters'] = {}
    config['parameters']['model_file'] = 'priors/reinvent.prior'
    config['parameters']['output_file'] = 'results/sampling.csv'
    config['parameters']['num_smiles'] = num_smiles
    config['parameters']['randomize_smiles'] = randomize_smiles
    config['parameters']['unique_molecules'] = True
    with open('sampling.toml', 'w') as f:
        toml.dump(config, f)

create_toml()
subprocess.run("reinvent sampling.toml")
mols = pd.read_csv('results/sampling.csv')
mol = mols['SMILES'][0]
visualize_3d_from_smiles(mol, output_html = 'mol.html')
