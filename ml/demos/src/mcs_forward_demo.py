"""
Module: mcs_forward_demo.py
Purpose: Forward Monte Carlo Simulation (MCS) for credit card rate distribution
Demonstrates how to go from model inputs → distribution of outcomes

Key Concepts:
  - Forward inference: parameters → data
  - Uncertainty quantification through sampling
  - Convergence of empirical to true distribution

Source: turn0browsertab744690698
Author: ML Finance Course - Chapter 1
Date: 2026-03-27

Requirements:
  numpy, pandas, scipy, matplotlib
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Tuple, Dict
from scipy.stats import binom


def forward_mcs_binomial_rates(
    fed_meetings: int = 8,
    prob_raise: float = 0.7,
    base_rate: float = 12.0,
    per_raise_bps: float = 25.0,
    n_simulations: int = 100_000,
    seed: int = 42
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Forward MCS: Sample outcomes from binomial distribution.
    
    Parameters
    ----------
    fed_meetings : int
        Number of Fed meetings
    prob_raise : float
        Probability of rate hike at each meeting
    base_rate : float
        Starting credit card rate (%)
    per_raise_bps : float
        Basis points per hike
    n_simulations : int
        Number of Monte Carlo samples
    seed : int
        Random seed
    
    Returns
    -------
    sample_rates : np.ndarray of shape (n_simulations,)
        Simulated credit card rates
    sample_counts : np.ndarray of shape (n_simulations,)
        Number of hikes in each simulation
    """
    np.random.seed(seed)
    
    # Simulate number of hikes (Binomial)
    sample_counts = np.random.binomial(n=fed_meetings, p=prob_raise, size=n_simulations)
    
    # Convert to rates
    sample_rates = base_rate + (sample_counts * per_raise_bps) / 100.0
    
    return sample_rates, sample_counts


def compare_empirical_vs_theoretical(
    sample_rates: np.ndarray,
    fed_meetings: int = 8,
    prob_raise: float = 0.7,
    base_rate: float = 12.0,
    per_raise_bps: float = 25.0,
    n_bins: int = 30
) -> Dict[str, float]:
    """
    Compare empirical distribution from MCS with theoretical Binomial.
    
    Parameters
    ----------
    sample_rates : np.ndarray
        Simulated rates from MCS
    fed_meetings, prob_raise, base_rate, per_raise_bps : float
        Model parameters
    n_bins : int
        Number of histogram bins
    
    Returns
    -------
    metrics : dict
        Comparison statistics
    """
    # Empirical stats
    emp_mean = sample_rates.mean()
    emp_std = sample_rates.std()
    emp_median = np.median(sample_rates)
    
    # Theoretical stats
    theo_mean = base_rate + (fed_meetings * prob_raise * per_raise_bps) / 100.0
    theo_var = fed_meetings * prob_raise * (1 - prob_raise) * ((per_raise_bps / 100.0) ** 2)
    theo_std = np.sqrt(theo_var)
    
    k = np.arange(0, fed_meetings + 1)
    pmf = binom.pmf(k, fed_meetings, prob_raise)
    theo_rates = base_rate + (k * per_raise_bps) / 100.0
    theo_median = np.sum(pmf * theo_rates)  # Weighted median approximation
    
    return {
        'empirical_mean': emp_mean,
        'empirical_std': emp_std,
        'empirical_median': emp_median,
        'theoretical_mean': theo_mean,
        'theoretical_std': theo_std,
        'theoretical_median': theo_median,
        'mean_error_pct': abs(emp_mean - theo_mean) / theo_mean * 100,
        'std_error_pct': abs(emp_std - theo_std) / theo_std * 100,
    }


def convergence_analysis(
    fed_meetings: int = 8,
    prob_raise: float = 0.7,
    base_rate: float = 12.0,
    per_raise_bps: float = 25.0,
    n_samples_list: list = None,
    n_trials: int = 10,
    seed: int = 42
) -> pd.DataFrame:
    """
    Analyze convergence of empirical distribution as n_simulations increases.
    
    Parameters
    ----------
    fed_meetings, prob_raise, base_rate, per_raise_bps : float
        Model parameters
    n_samples_list : list
        List of sample sizes to test (e.g., [100, 1000, 10000, ...])
    n_trials : int
        Number of independent trials for each sample size
    seed : int
        Random seed
    
    Returns
    -------
    results : pd.DataFrame
        Convergence results
    """
    if n_samples_list is None:
        n_samples_list = [10, 100, 1_000, 10_000, 100_000]
    
    np.random.seed(seed)
    
    # Theoretical parameters
    theo_mean = base_rate + (fed_meetings * prob_raise * per_raise_bps) / 100.0
    theo_var = fed_meetings * prob_raise * (1 - prob_raise) * ((per_raise_bps / 100.0) ** 2)
    theo_std = np.sqrt(theo_var)
    
    results = []
    
    for n_samples in n_samples_list:
        errors_mean = []
        errors_std = []
        
        for trial in range(n_trials):
            np.random.seed(seed + trial)
            sample_counts = np.random.binomial(n=fed_meetings, p=prob_raise, size=n_samples)
            sample_rates = base_rate + (sample_counts * per_raise_bps) / 100.0
            
            emp_mean = sample_rates.mean()
            emp_std = sample_rates.std()
            
            errors_mean.append(abs(emp_mean - theo_mean) / theo_mean * 100)
            errors_std.append(abs(emp_std - theo_std) / theo_std * 100)
        
        results.append({
            'n_samples': n_samples,
            'mean_error_min': np.min(errors_mean),
            'mean_error_max': np.max(errors_mean),
            'mean_error_mean': np.mean(errors_mean),
            'std_error_min': np.min(errors_std),
            'std_error_max': np.max(errors_std),
            'std_error_mean': np.mean(errors_std),
        })
    
    return pd.DataFrame(results)


def plot_mcs_results(
    sample_rates: np.ndarray,
    fed_meetings: int = 8,
    prob_raise: float = 0.7,
    base_rate: float = 12.0,
    per_raise_bps: float = 25.0,
    figsize: Tuple[int, int] = (14, 5),
    save_path: str = None
) -> plt.Figure:
    """
    Plot MCS results vs theoretical distribution.
    
    Parameters
    ----------
    sample_rates : np.ndarray
        Simulated rates
    Other parameters : float
        Model parameters
    figsize : tuple
        Figure size
    save_path : str, optional
        Path to save figure
    
    Returns
    -------
    fig : plt.Figure
    """
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    
    # Subplot 1: Histogram vs PMF
    ax1 = axes[0]
    counts, bins, patches = ax1.hist(sample_rates, bins=40, density=True, alpha=0.6, 
                                      color='steelblue', edgecolor='black', label='MCS (Empirical)')
    
    k = np.arange(0, fed_meetings + 1)
    pmf = binom.pmf(k, fed_meetings, prob_raise)
    theo_rates = base_rate + (k * per_raise_bps) / 100.0
    ax1.scatter(theo_rates, pmf, color='red', s=100, marker='o', zorder=5, 
                label='Theoretical Binomial PMF', edgecolor='darkred', linewidth=1.5)
    
    ax1.set_xlabel('Credit Card Rate (%)', fontsize=11)
    ax1.set_ylabel('Probability Density', fontsize=11)
    ax1.set_title('Forward MCS: Empirical vs Theoretical Distribution', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Subplot 2: Cumulative distribution
    ax2 = axes[1]
    sorted_rates = np.sort(sample_rates)
    empirical_cdf = np.arange(1, len(sorted_rates) + 1) / len(sorted_rates)
    ax2.plot(sorted_rates, empirical_cdf, 'o-', color='steelblue', alpha=0.6, 
             markersize=4, label='Empirical CDF (MCS)')
    
    theo_cdf = binom.cdf(k, fed_meetings, prob_raise)
    ax2.step(theo_rates, theo_cdf, 'r-', where='mid', linewidth=2.5, 
             label='Theoretical CDF (Binomial)', alpha=0.8)
    
    ax2.set_xlabel('Credit Card Rate (%)', fontsize=11)
    ax2.set_ylabel('Cumulative Probability', fontsize=11)
    ax2.set_title('Cumulative Distribution Function (CDF)', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✓ Saved: {save_path}")
    
    return fig


# ============= MAIN EXECUTION =============

if __name__ == "__main__":
    print("=" * 80)
    print("FORWARD MONTE CARLO SIMULATION (MCS) — Credit Card Rates")
    print("=" * 80)
    
    # Parameters
    FED_MEETINGS = 8
    PROB_RAISE = 0.7
    BASE_RATE = 12.0
    PER_RAISE_BPS = 25.0
    N_SIMULATIONS = 100_000
    
    # Run forward MCS
    print(f"\n[1] Running Forward MCS with {N_SIMULATIONS:,} simulations...")
    sample_rates, sample_counts = forward_mcs_binomial_rates(
        fed_meetings=FED_MEETINGS,
        prob_raise=PROB_RAISE,
        base_rate=BASE_RATE,
        per_raise_bps=PER_RAISE_BPS,
        n_simulations=N_SIMULATIONS
    )
    print(f"    ✓ Generated {len(sample_rates):,} samples")
    
    # Compare empirical vs theoretical
    print(f"\n[2] Comparing Empirical vs Theoretical Distribution...")
    metrics = compare_empirical_vs_theoretical(
        sample_rates,
        fed_meetings=FED_MEETINGS,
        prob_raise=PROB_RAISE,
        base_rate=BASE_RATE,
        per_raise_bps=PER_RAISE_BPS
    )
    
    print(f"\n    Empirical Statistics (from MCS):")
    print(f"      Mean: {metrics['empirical_mean']:.4f}%")
    print(f"      Std Dev: {metrics['empirical_std']:.4f}%")
    print(f"      Median: {metrics['empirical_median']:.4f}%")
    
    print(f"\n    Theoretical Statistics (Binomial):")
    print(f"      Mean: {metrics['theoretical_mean']:.4f}%")
    print(f"      Std Dev: {metrics['theoretical_std']:.4f}%")
    print(f"      Median: {metrics['theoretical_median']:.4f}%")
    
    print(f"\n    Convergence Error:")
    print(f"      Mean Error: {metrics['mean_error_pct']:.3f}%")
    print(f"      Std Error: {metrics['std_error_pct']:.3f}%")
    
    # Convergence analysis
    print(f"\n[3] Convergence Analysis (10 trials per sample size)...")
    convergence_df = convergence_analysis(
        fed_meetings=FED_MEETINGS,
        prob_raise=PROB_RAISE,
        base_rate=BASE_RATE,
        per_raise_bps=PER_RAISE_BPS,
        n_samples_list=[10, 100, 1_000, 10_000, 100_000, 1_000_000],
        n_trials=10
    )
    
    print("\n    n_samples | Mean Error (%) | Std Error (%)")
    print("    " + "-" * 45)
    for _, row in convergence_df.iterrows():
        print(f"    {int(row['n_samples']):>9,} | {row['mean_error_mean']:>13.4f} | {row['std_error_mean']:>12.4f}")
    
    # Plot results
    print(f"\n[4] Generating plots...")
    fig = plot_mcs_results(
        sample_rates,
        fed_meetings=FED_MEETINGS,
        prob_raise=PROB_RAISE,
        base_rate=BASE_RATE,
        per_raise_bps=PER_RAISE_BPS,
        save_path="mcs_forward_analysis.png"
    )
    
    print("\n" + "=" * 80)
    print("✓ Forward MCS complete!")
    print("   Output: mcs_forward_analysis.png")
    print("=" * 80)
    
    plt.close('all')
