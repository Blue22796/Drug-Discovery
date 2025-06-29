import pandas as pd
from pathlib import Path

def process_transfer_learning_csv(csv_path, output_dir, train_ratio=0.8):
    """
    Process a CSV file containing SMILES, split into train/val and write .smi files.

    Args:
        csv_path (str | Path): Path to input CSV file.
        output_dir (str | Path): Directory to save output .smi files.
        train_ratio (float): Proportion of data for training.

    Returns:
        dict: Paths to the generated .smi files.
    """
    csv_path = Path(csv_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load CSV
    df = pd.read_csv(csv_path)

    # Detect SMILES column (case insensitive)
    smiles_col = None
    for col in df.columns:
        if col.strip().lower() == "smiles":
            smiles_col = col
            break

    if not smiles_col:
        raise ValueError("No SMILES column found in CSV. Ensure it contains a column named SMILES (any case).")

    # Shuffle
    df_shuffled = df.sample(frac=1.0, random_state=42).reset_index(drop=True)

    # Split
    n_train = int(len(df_shuffled) * train_ratio)
    train_df = df_shuffled.iloc[:n_train]
    val_df = df_shuffled.iloc[n_train:]

    # Write SMILES to .smi files
    train_smi = output_dir / "compounds.smi"
    val_smi = output_dir / "validation_compounds.smi"

    train_df[smiles_col].to_csv(train_smi, index=False, header=False)
    val_df[smiles_col].to_csv(val_smi, index=False, header=False)

    return {
        "train_smi": str(train_smi.resolve()),
        "val_smi": str(val_smi.resolve())
    }
