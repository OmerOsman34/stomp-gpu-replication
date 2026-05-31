"""
STOMP Fast Replication - Scaled Down for Faster Results

This script computes STOMP on smaller datasets (100K, 1M, 10M) 
to demonstrate O(n²) scaling relationship quickly.

Reference: 
    Zhu et al. (2016). Matrix Profile II: Exploiting a Novel Algorithm 
    and GPUs to Break the One Hundred Million Barrier. IEEE ICDM.
"""

import numpy as np
import pandas as pd
import stumpy
import os
from pathlib import Path
from utils import set_seed, Timer, get_system_info, format_size, format_time
import json
import warnings

warnings.filterwarnings('ignore')


class STOMPFastReplicator:
    """Fast version of STOMP replicator with smaller datasets."""
    
    def __init__(self, seed: int = 2021402216):
        self.seed = seed
        self.results = []
        self.system_info = get_system_info()
        set_seed(seed)
    
    def compute_matrix_profile(self, ts: np.ndarray, 
                              subsequence_length: int = 50) -> tuple:
        """Compute matrix profile using STUMPY's STUMP algorithm."""
        with Timer(f"STOMP computation (n={len(ts):,}, m={subsequence_length})") as timer:
            mp = stumpy.stump(ts, m=subsequence_length)
        
        matrix_profile = mp[:, 0]
        matrix_profile_index = mp[:, 1].astype(int)
        
        return matrix_profile, matrix_profile_index, timer.elapsed
    
    def run_fast_benchmark(self, sizes: list = None, 
                          subsequence_length: int = 50) -> pd.DataFrame:
        """Run benchmark on smaller, faster dataset sizes."""
        
        if sizes is None:
            # Smaller sizes for faster testing: 100K, 1M, 10M
            sizes = [100_000, 1_000_000, 10_000_000]
        
        results_dir = Path(__file__).parent.parent / "results"
        results_dir.mkdir(exist_ok=True)
        
        print("\n" + "="*70)
        print("STOMP FAST BENCHMARK (Reduced Dataset Sizes)")
        print("="*70)
        print(f"Student ID (Seed): {self.seed}")
        print(f"Subsequence Length: {subsequence_length}")
        print(f"Datasets to process: {len(sizes)}")
        print(f"Note: Using {len(sizes)} sizes to demonstrate O(n²) scaling")
        print("="*70 + "\n")
        
        results_list = []
        
        for size in sizes:
            print(f"\n{'─'*70}")
            print(f"Dataset Size: {size:,} points")
            print(f"{'─'*70}")
            
            # Generate data
            with Timer(f"Generate {size:,} points") as gen_timer:
                set_seed(self.seed)
                ts = np.cumsum(np.random.randn(size)) + np.random.randn() * 10
                ts = ts.astype(np.float64)
            
            data_size_bytes = ts.nbytes
            print(f"Data size in memory: {format_size(data_size_bytes)}")
            print(f"Min: {ts.min():.4f}, Max: {ts.max():.4f}, Mean: {ts.mean():.4f}")
            
            # Compute matrix profile
            try:
                mp, mp_idx, mp_time = self.compute_matrix_profile(
                    ts, 
                    subsequence_length=subsequence_length
                )
                
                # Record results
                result = {
                    'dataset_size': size,
                    'subsequence_length': subsequence_length,
                    'n_subsequences': len(mp),
                    'runtime_seconds': mp_time,
                    'runtime_formatted': format_time(mp_time),
                    'data_size_mb': data_size_bytes / (1024**2),
                    'status': 'success',
                    'min_mp': float(mp.min()),
                    'max_mp': float(mp.max()),
                    'mean_mp': float(mp.mean()),
                }
                
                results_list.append(result)
                
                print(f"Status: SUCCESS ✓")
                print(f"Matrix Profile computed in {result['runtime_formatted']}")
                print(f"MP range: [{result['min_mp']:.4f}, {result['max_mp']:.4f}]")
                
            except Exception as e:
                print(f"Status: FAILED ✗")
                print(f"Error: {str(e)}")
                
                result = {
                    'dataset_size': size,
                    'subsequence_length': subsequence_length,
                    'status': 'failed',
                    'error_message': str(e),
                }
                results_list.append(result)
        
        # Create results dataframe
        results_df = pd.DataFrame(results_list)
        
        # Save results
        results_file = results_dir / "performance_metrics_fast.csv"
        results_df.to_csv(results_file, index=False)
        print(f"\n✓ Results saved to: {results_file}")
        
        # Print summary
        print("\n" + "="*70)
        print("BENCHMARK SUMMARY")
        print("="*70)
        print(results_df.to_string(index=False))
        
        # Verify O(n²) scaling
        successful = results_df[results_df['status'] == 'success'].copy()
        if len(successful) >= 2:
            print("\n" + "="*70)
            print("O(n²) SCALING VERIFICATION")
            print("="*70)
            
            sizes_array = successful['dataset_size'].values
            runtimes_array = successful['runtime_seconds'].values
            
            for i in range(len(successful) - 1):
                size_ratio = sizes_array[i+1] / sizes_array[i]
                runtime_ratio = runtimes_array[i+1] / runtimes_array[i]
                expected_ratio = size_ratio ** 2
                
                print(f"\nSize {int(sizes_array[i]):,} → {int(sizes_array[i+1]):,}")
                print(f"  Size ratio: {size_ratio:.1f}x")
                print(f"  Runtime ratio: {runtime_ratio:.1f}x")
                print(f"  Expected (O(n²)): {expected_ratio:.1f}x")
                
                deviation = abs(runtime_ratio - expected_ratio) / expected_ratio * 100
                print(f"  Deviation: {deviation:.1f}% {'✓' if deviation < 50 else '⚠'}")
        
        # Save system info
        system_info_file = results_dir / "system_info.json"
        with open(system_info_file, 'w') as f:
            json.dump(self.system_info, f, indent=2, default=str)
        print(f"\n✓ System info saved to: {system_info_file}")
        
        self.results = results_df
        return results_df


def main():
    """Main execution function."""
    
    # Initialize
    replicator = STOMPFastReplicator(seed=2021402216)
    
    # Run fast benchmark on smaller sizes
    results = replicator.run_fast_benchmark(
        sizes=[100_000, 1_000_000, 10_000_000],  # 100K, 1M, 10M (faster)
        subsequence_length=50
    )
    
    print("\n" + "="*70)
    print("✓ STOMP fast benchmarking complete!")
    print("="*70)


if __name__ == "__main__":
    main()
