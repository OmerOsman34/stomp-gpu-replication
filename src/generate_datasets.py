"""
Generate synthetic time series datasets for STOMP benchmarking.
"""

import numpy as np
import pandas as pd
import os
from pathlib import Path
from utils import set_seed, Timer, format_size


def generate_and_save_datasets(seed: int = 2021402216, 
                              sizes: list = None) -> None:
    """
    Generate synthetic time series of various sizes and save as CSV.
    
    Args:
        seed: Random seed for reproducibility (uses student ID)
        sizes: List of dataset sizes in points. Default: [1_000_000, 10_000_000, 50_000_000]
    """
    if sizes is None:
        sizes = [1_000_000, 10_000_000, 50_000_000]
    
    set_seed(seed)
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    print(f"Generating synthetic time series datasets...\n")
    print(f"Output directory: {data_dir}")
    print(f"Student ID (seed): {seed}\n")
    
    for size in sizes:
        print(f"\n{'='*60}")
        print(f"Generating {size:,} points dataset")
        print(f"{'='*60}")
        
        with Timer(f"Generate {size:,} points") as timer:
            # Generate normal distributed random walk
            ts = np.cumsum(np.random.randn(size)) + np.random.randn() * 10
            ts = ts.astype(np.float64)
        
        # Save to CSV
        output_file = data_dir / f"synthetic_timeseries_{size}.csv"
        with Timer(f"Save to {output_file.name}"):
            df = pd.DataFrame({"value": ts})
            df.to_csv(output_file, index=False)
        
        file_size = os.path.getsize(output_file)
        print(f"File size: {format_size(file_size)}")
        print(f"Data points: {len(ts):,}")
        print(f"Mean: {ts.mean():.4f}, Std: {ts.std():.4f}")


def generate_trial_datasets(seed: int = 2021402216, 
                           sizes: list = None,
                           n_trials: int = 3) -> None:
    """
    Generate multiple trial datasets for averaging results.
    
    Args:
        seed: Base random seed
        sizes: List of dataset sizes
        n_trials: Number of trials per size
    """
    if sizes is None:
        sizes = [1_000_000, 10_000_000]  # Smaller set for trials
    
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    print(f"Generating {n_trials} trial datasets for each size...\n")
    
    for size in sizes:
        print(f"\n{'='*60}")
        print(f"Size: {size:,} points, Trials: {n_trials}")
        print(f"{'='*60}")
        
        for trial in range(1, n_trials + 1):
            trial_seed = seed + trial
            set_seed(trial_seed)
            
            with Timer(f"Trial {trial}/{n_trials}") as timer:
                ts = np.cumsum(np.random.randn(size)) + np.random.randn() * 10
                ts = ts.astype(np.float64)
            
            output_file = data_dir / f"synthetic_timeseries_{size}_trial{trial}.csv"
            df = pd.DataFrame({"value": ts})
            df.to_csv(output_file, index=False)
            
            file_size = os.path.getsize(output_file)
            print(f"  Saved: {output_file.name} ({format_size(file_size)})")


if __name__ == "__main__":
    # Generate main datasets
    generate_and_save_datasets(
        seed=2021402216,
        sizes=[1_000_000, 10_000_000, 50_000_000]
    )
    
    print("\n" + "="*60)
    print("Dataset generation complete!")
    print("="*60)
