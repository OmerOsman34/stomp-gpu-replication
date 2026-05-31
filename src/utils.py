"""
Utility functions for STOMP replication project.
"""

import numpy as np
import time
import psutil
import os
from datetime import datetime


def set_seed(seed_value: int) -> None:
    """
    Set random seed for reproducibility.
    
    Args:
        seed_value: Integer seed value
    """
    np.random.seed(seed_value)
    print(f"Random seed set to: {seed_value}")


def get_system_info() -> dict:
    """
    Get system information for reproducibility documentation.
    
    Returns:
        Dictionary with system information
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu_count": os.cpu_count(),
        "total_memory_gb": psutil.virtual_memory().total / (1024**3),
        "available_memory_gb": psutil.virtual_memory().available / (1024**3),
        "python_version": f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}",
    }


class Timer:
    """Context manager for timing code execution."""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.elapsed = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        print(f"[{self.name}] Starting...")
        return self
    
    def __exit__(self, *args):
        self.end_time = time.perf_counter()
        self.elapsed = self.end_time - self.start_time
        print(f"[{self.name}] Completed in {self.elapsed:.4f} seconds ({self.elapsed/60:.2f} minutes)")
    
    def get_elapsed(self) -> float:
        """Get elapsed time in seconds."""
        return self.elapsed


def generate_synthetic_timeseries(n_points: int, seed: int = None) -> np.ndarray:
    """
    Generate synthetic random time series for benchmarking.
    
    Args:
        n_points: Number of data points
        seed: Random seed for reproducibility
    
    Returns:
        Numpy array with synthetic time series
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Generate normal distributed random walk
    ts = np.cumsum(np.random.randn(n_points)) + np.random.randn() * 10
    return ts.astype(np.float64)


def format_size(n_bytes: int) -> str:
    """Format byte size to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if n_bytes < 1024.0:
            return f"{n_bytes:.2f} {unit}"
        n_bytes /= 1024.0
    return f"{n_bytes:.2f} PB"


def format_time(seconds: float) -> str:
    """Format seconds to human-readable time format."""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        return f"{seconds/60:.2f}m"
    else:
        return f"{seconds/3600:.2f}h"


if __name__ == "__main__":
    # Quick test
    set_seed(2021402216)
    info = get_system_info()
    print("System Information:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\nGenerating sample time series...")
    ts = generate_synthetic_timeseries(1000, seed=2021402216)
    print(f"  Generated {len(ts)} points, shape: {ts.shape}")
