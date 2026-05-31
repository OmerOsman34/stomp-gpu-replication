"""
Visualization and analysis of STOMP benchmark results.

Replicates Figure 4 from Zhu et al. (2016): Performance comparison of STOMP.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11


def load_results(results_file: str = None) -> pd.DataFrame:
    """
    Load benchmark results from CSV.
    
    Args:
        results_file: Path to results CSV. If None, searches for it.
    
    Returns:
        DataFrame with results
    """
    if results_file is None:
        results_dir = Path(__file__).parent.parent / "results"
        results_file = results_dir / "performance_metrics.csv"
    
    results_df = pd.read_csv(results_file)
    return results_df


def plot_performance_comparison(results_df: pd.DataFrame,
                               save_path: str = None) -> None:
    """
    Plot performance comparison: Runtime vs Dataset Size.
    
    Replicates Figure 4 from Zhu et al. (2016).
    
    Args:
        results_df: DataFrame with benchmark results
        save_path: Path to save figure (optional)
    """
    # Filter successful runs only
    successful = results_df[results_df['status'] == 'success'].copy()
    
    if len(successful) == 0:
        print("No successful runs to plot!")
        return
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Plot runtime vs dataset size
    sizes = successful['dataset_size'].values / 1e6  # Convert to millions
    runtimes = successful['runtime_seconds'].values
    
    ax.loglog(sizes, runtimes, 'o-', linewidth=2.5, markersize=10, 
             label='STOMP Runtime', color='#2E86AB', markerfacecolor='#A23B72')
    
    # Add annotations for each point
    for i, (size, runtime) in enumerate(zip(sizes, runtimes)):
        runtime_str = f"{runtime:.1f}s" if runtime < 60 else f"{runtime/60:.1f}m"
        ax.annotate(f'{size:.0f}M\n{runtime_str}', 
                   xy=(size, runtime), 
                   xytext=(10, 10),
                   textcoords='offset points',
                   fontsize=9,
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.3))
    
    ax.set_xlabel('Dataset Size (Million points)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Runtime (seconds)', fontsize=12, fontweight='bold')
    ax.set_title('STOMP Performance: Runtime vs Dataset Size\n(Replication of Figure 4 - Zhu et al. 2016)', 
                fontsize=13, fontweight='bold', pad=20)
    
    ax.grid(True, which='both', alpha=0.3)
    ax.legend(fontsize=11, loc='upper left')
    
    plt.tight_layout()
    
    if save_path is None:
        figures_dir = Path(__file__).parent.parent / "figures"
        figures_dir.mkdir(exist_ok=True)
        save_path = figures_dir / "performance_comparison.png"
    
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ Performance comparison plot saved: {save_path}")
    plt.close()


def plot_scaling_analysis(results_df: pd.DataFrame,
                         save_path: str = None) -> None:
    """
    Plot scaling analysis (O(n²) verification).
    
    Args:
        results_df: DataFrame with benchmark results
        save_path: Path to save figure
    """
    successful = results_df[results_df['status'] == 'success'].copy()
    
    if len(successful) < 2:
        print("Not enough data points for scaling analysis")
        return
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    sizes = successful['dataset_size'].values
    runtimes = successful['runtime_seconds'].values
    
    # Plot 1: Linear scale (verify O(n²) relationship)
    sizes_normalized = sizes / sizes[0]  # Normalize to first size
    runtimes_normalized = runtimes / runtimes[0]  # Normalize to first runtime
    
    ax1.plot(sizes_normalized, runtimes_normalized, 'o-', linewidth=2.5, markersize=10,
            label='Measured Runtime', color='#2E86AB')
    
    # Theoretical O(n²) line
    theoretical = sizes_normalized ** 2
    ax1.plot(sizes_normalized, theoretical, 's--', linewidth=2, markersize=8,
            label='O(n²) Theoretical', color='#F18F01', alpha=0.7)
    
    ax1.set_xlabel('Normalized Dataset Size', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Normalized Runtime', fontsize=11, fontweight='bold')
    ax1.set_title('Scaling Analysis: Runtime vs O(n²)', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Data efficiency (MB/second)
    data_sizes_mb = successful['data_size_mb'].values
    throughput = data_sizes_mb / runtimes  # MB per second
    
    ax2.bar(range(len(successful)), throughput, color='#2E86AB', alpha=0.7, edgecolor='black', linewidth=1.5)
    ax2.set_xticks(range(len(successful)))
    ax2.set_xticklabels([f"{int(s/1e6)}M" for s in sizes], fontsize=10)
    ax2.set_ylabel('Throughput (MB/sec)', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Dataset Size', fontsize=11, fontweight='bold')
    ax2.set_title('Data Throughput Analysis', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for i, v in enumerate(throughput):
        ax2.text(i, v + max(throughput)*0.02, f'{v:.1f}', ha='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    
    if save_path is None:
        figures_dir = Path(__file__).parent.parent / "figures"
        figures_dir.mkdir(exist_ok=True)
        save_path = figures_dir / "scaling_analysis.png"
    
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ Scaling analysis plot saved: {save_path}")
    plt.close()


def create_results_summary(results_df: pd.DataFrame,
                          save_path: str = None) -> None:
    """
    Create detailed results summary table.
    
    Args:
        results_df: DataFrame with results
        save_path: Path to save summary
    """
    successful = results_df[results_df['status'] == 'success'].copy()
    
    if len(successful) == 0:
        print("No successful runs to summarize")
        return
    
    summary = successful[['dataset_size', 'runtime_seconds', 'runtime_formatted', 'data_size_mb']].copy()
    summary['dataset_size'] = summary['dataset_size'].apply(lambda x: f"{int(x):,}")
    summary.columns = ['Dataset Size (points)', 'Runtime (seconds)', 'Runtime (formatted)', 'Data Size (MB)']
    
    print("\n" + "="*80)
    print("STOMP BENCHMARK RESULTS SUMMARY")
    print("="*80)
    print(summary.to_string(index=False))
    print("="*80 + "\n")
    
    if save_path is None:
        figures_dir = Path(__file__).parent.parent / "figures"
        figures_dir.mkdir(exist_ok=True)
        save_path = figures_dir / "results_summary.txt"
    
    with open(save_path, 'w') as f:
        f.write("STOMP BENCHMARK RESULTS SUMMARY\n")
        f.write("="*80 + "\n\n")
        f.write(summary.to_string(index=False))
        f.write("\n\n" + "="*80 + "\n")
    
    print(f"✓ Summary saved to: {save_path}")


def main():
    """Main visualization function."""
    
    print("\n" + "="*80)
    print("STOMP RESULTS VISUALIZATION")
    print("="*80 + "\n")
    
    # Load results
    try:
        results_df = load_results()
        print(f"✓ Loaded {len(results_df)} results\n")
    except FileNotFoundError:
        print("❌ Results file not found. Run run_stomp.py first!")
        return
    
    # Create visualizations
    print("Generating visualizations...")
    plot_performance_comparison(results_df)
    plot_scaling_analysis(results_df)
    create_results_summary(results_df)
    
    print("\n" + "="*80)
    print("✓ All visualizations complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
