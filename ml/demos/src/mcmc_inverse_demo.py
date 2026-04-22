"""
Module: mcmc_inverse_demo.py
Purpose: Inverse inference using MCMC (Markov Chain Monte Carlo)
Demonstrates Bayesian parameter estimation for the Binomial credit rate model

Key Concepts:
  - Inverse inference: observations → posterior distribution over parameters
  - MCMC for sampling from posterior (approximates exact Bayesian inference)
  - Posterior predictive checks (PPC) for model validation

Source: turn0browsertab744690698
Author: ML Finance Course - Chapter 1
Date: 2026-03-27

Requirements:
  numpy, pandas, pymc (or emcee for pure MH), matplotlib
  
Note: This demo uses a simple Metropolis-Hastings sampler from scratch
      For production, use PyMC or stan.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List
from scipy.stats import binom, beta


class MetropolisHastingsSampler:
    """
    Simple Metropolis-Hastings MCMC sampler for Binomial success probability.
    """
    
    def __init__(self, seed: int = 42):
        """Initialize sampler with random seed."""
        self.seed = seed
        np.random.seed(seed)
    
    def log_likelihood(self, data: np.ndarray, n: int, p: float) -> float:
        """
        Log-likelihood of observing `data` (count of successes) given Binomial(n, p).
        
        Parameters
        ----------
        data : np.ndarray
            Observed counts of successes (shape: (n_observations,))
        n : int
            Number of trials per observation
        p : float
            Success probability (0 <= p <= 1)
        
        Returns
        -------
        log_lik : float
            Sum of log-likelihoods for all observations
        """
        # Avoid log(0)
        p = np.clip(p, 1e-10, 1 - 1e-10)
        
        # Log-likelihood for Binomial: log P(k | n, p) = log C(n,k) + k*log(p) + (n-k)*log(1-p)
        # We drop C(n,k) since it's constant w.r.t. p
        log_lik = (data * np.log(p) + (n - data) * np.log(1 - p)).sum()
        return log_lik
    
    def log_prior(self, p: float, alpha: float = 1.0, beta_param: float = 1.0) -> float:
        """
        Log prior for p under Beta(alpha, beta_param) distribution.
        
        Parameters
        ----------
        p : float
            Success probability
        alpha, beta_param : float
            Beta distribution parameters
        
        Returns
        -------
        log_prior : float
        """
        if p <= 0 or p >= 1:
            return -np.inf
        
        # Beta distribution shape
        log_prior = (alpha - 1) * np.log(p) + (beta_param - 1) * np.log(1 - p)
        return log_prior
    
    def log_posterior(
        self,
        data: np.ndarray,
        n: int,
        p: float,
        alpha: float = 1.0,
        beta_param: float = 1.0
    ) -> float:
        """Log posterior = log likelihood + log prior."""
        ll = self.log_likelihood(data, n, p)
        lp = self.log_prior(p, alpha, beta_param)
        return ll + lp
    
    def sample(
        self,
        data: np.ndarray,
        n: int,
        n_iter: int = 10_000,
        proposal_std: float = 0.05,
        alpha: float = 1.0,
        beta_param: float = 1.0
    ) -> Tuple[np.ndarray, float]:
        """
        Run Metropolis-Hastings MCMC.
        
        Parameters
        ----------
        data : np.ndarray
            Observed counts of successes
        n : int
            Number of trials per observation
        n_iter : int
            Number of MCMC iterations
        proposal_std : float
            Standard deviation of Gaussian proposal
        alpha, beta_param : float
            Beta prior parameters
        
        Returns
        -------
        samples : np.ndarray of shape (n_iter,)
            Posterior samples of p
        acceptance_rate : float
            Proportion of accepted proposals
        """
        np.random.seed(self.seed)
        
        samples = np.zeros(n_iter)
        p_current = 0.5  # Initial guess
        
        log_posterior_current = self.log_posterior(data, n, p_current, alpha, beta_param)
        
        n_accepted = 0
        
        for i in range(n_iter):
            # Proposal: p_proposed ~ N(p_current, proposal_std^2)
            p_proposed = p_current + np.random.normal(0, proposal_std)
            
            # Reject if out of bounds
            if p_proposed <= 0 or p_proposed >= 1:
                samples[i] = p_current
                continue
            
            # Compute log acceptance ratio
            log_posterior_proposed = self.log_posterior(data, n, p_proposed, alpha, beta_param)
            log_alpha = log_posterior_proposed - log_posterior_current
            
            # Metropolis-Hastings acceptance
            if np.log(np.random.uniform()) < log_alpha:
                p_current = p_proposed
                log_posterior_current = log_posterior_proposed
                n_accepted += 1
            
            samples[i] = p_current
        
        acceptance_rate = n_accepted / n_iter
        return samples, acceptance_rate


def posterior_predictive_check(
    posterior_samples: np.ndarray,
    observed_data: np.ndarray,
    n_trials: int = 8,
    n_ppc_samples: int = 1000
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Posterior Predictive Check: Generate synthetic data from posterior.
    
    Parameters
    ----------
    posterior_samples : np.ndarray
        Posterior samples of p from MCMC
    observed_data : np.ndarray
        Original observations
    n_trials : int
        Number of trials per binomial
    n_ppc_samples : int
        Number of synthetic observations per posterior sample
    
    Returns
    -------
    ppc_samples : np.ndarray of shape (len(posterior_samples), n_ppc_samples)
        Synthetic data generated from posterior
    observed_data : np.ndarray
        Original data (for reference)
    """
    n_posterior = len(posterior_samples)
    ppc_samples = np.zeros((n_posterior, n_ppc_samples))
    
    for i, p in enumerate(posterior_samples):
        ppc_samples[i, :] = np.random.binomial(n_trials, p, size=n_ppc_samples)
    
    return ppc_samples, observed_data


def plot_mcmc_diagnostics(
    posterior_samples: np.ndarray,
    burnin: int = 1000,
    figsize: Tuple[int, int] = (14, 8),
    save_path: str = None
) -> plt.Figure:
    """
    Plot MCMC diagnostics: trace plot, posterior distribution, ACF.
    
    Parameters
    ----------
    posterior_samples : np.ndarray
        Posterior samples from MCMC
    burnin : int
        Number of initial samples to discard (burn-in)
    figsize : tuple
        Figure size
    save_path : str, optional
        Path to save figure
    
    Returns
    -------
    fig : plt.Figure
    """
    samples_post_burnin = posterior_samples[burnin:]
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    
    # Subplot 1: Trace plot (full)
    ax1 = axes[0, 0]
    ax1.plot(posterior_samples, linewidth=0.5, alpha=0.7, color='steelblue')
    ax1.axvline(burnin, color='red', linestyle='--', linewidth=2, label=f'Burn-in (n={burnin})')
    ax1.set_xlabel('Iteration', fontsize=11)
    ax1.set_ylabel('p (success probability)', fontsize=11)
    ax1.set_title('Trace Plot (Full Chain)', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Subplot 2: Trace plot (post burn-in)
    ax2 = axes[0, 1]
    iterations = np.arange(burnin, len(posterior_samples))
    ax2.plot(iterations, samples_post_burnin, linewidth=0.5, alpha=0.7, color='steelblue')
    ax2.set_xlabel('Iteration (post burn-in)', fontsize=11)
    ax2.set_ylabel('p (success probability)', fontsize=11)
    ax2.set_title('Trace Plot (After Burn-in)', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Subplot 3: Posterior histogram + KDE
    ax3 = axes[1, 0]
    ax3.hist(samples_post_burnin, bins=50, density=True, alpha=0.6, 
             color='steelblue', edgecolor='black', label='Posterior (MCMC)')
    
    # Overlay theoretical (Beta) posterior
    p_range = np.linspace(0.01, 0.99, 200)
    # Approximate Beta posterior (for visualization)
    beta_pdf = beta.pdf(p_range, a=5, b=5)  # Example shape
    ax3.plot(p_range, beta_pdf, 'r-', linewidth=2, label='Reference (Beta)')
    
    ax3.set_xlabel('p (success probability)', fontsize=11)
    ax3.set_ylabel('Probability Density', fontsize=11)
    ax3.set_title('Posterior Distribution of p', fontsize=12, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    
    # Subplot 4: Autocorrelation
    ax4 = axes[1, 1]
    max_lag = min(100, len(samples_post_burnin) // 2)
    acf_values = []
    for lag in range(max_lag):
        acf = np.corrcoef(samples_post_burnin[:-lag], samples_post_burnin[lag:])[0, 1]
        acf_values .append(acf)
    
    ax4.bar(range(max_lag), acf_values, color='steelblue', edgecolor='black', alpha=0.7)
    ax4.axhline(0, color='black', linestyle='-', linewidth=0.5)
    ax4.axhline(0.05, color='red', linestyle='--', linewidth=1, alpha=0.5, label='5% threshold')
    ax4.set_xlabel('Lag', fontsize=11)
    ax4.set_ylabel('Autocorrelation', fontsize=11)
    ax4.set_title('Autocorrelation Function (ACF)', fontsize=12, fontweight='bold')
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✓ Saved: {save_path}")
    
    return fig


def plot_posterior_predictive_check(
    ppc_samples: np.ndarray,
    observed_data: np.ndarray,
    figsize: Tuple[int, int] = (12, 5),
    save_path: str = None
) -> plt.Figure:
    """
    Plot posterior predictive check: compare observed vs model-generated data.
    
    Parameters
    ----------
    ppc_samples : np.ndarray of shape (n_posterior, n_ppc)
        Synthetic data from posterior
    observed_data : np.ndarray
        Observed counts
    figsize : tuple
        Figure size
    save_path : str, optional
        Path to save figure
    
    Returns
    -------
    fig : plt.Figure
    """
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    
    # Subplot 1: Observed vs PPC histogram comparison
    ax1 = axes[0]
    ax1.hist(observed_data, bins=range(0, 10), alpha=0.5, label='Observed Data', 
             color='blue', edgecolor='black')
    ppc_flat = ppc_samples.flatten()
    ax1.hist(ppc_flat, bins=range(0, 10), alpha=0.5, label='PPC Samples', 
             color='red', edgecolor='black')
    ax1.set_xlabel('Number of Raises (k)', fontsize=11)
    ax1.set_ylabel('Frequency', fontsize=11)
    ax1.set_title('Posterior Predictive Check — Distribution', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Subplot 2: T-statistics comparison
    ax2 = axes[1]
    observed_mean = observed_data.mean()
    ppc_means = ppc_samples.mean(axis=1)
    
    ax2.hist(ppc_means, bins=30, alpha=0.6, color='red', edgecolor='black', label='PPC Mean Distribution')
    ax2.axvline(observed_mean, color='blue', linestyle='--', linewidth=2.5, label=f'Observed Mean = {observed_mean:.2f}')
    ax2.set_xlabel('Mean (number of raises)', fontsize=11)
    ax2.set_ylabel('Frequency', fontsize=11)
    ax2.set_title('Posterior Predictive Check — Mean', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✓ Saved: {save_path}")
    
    return fig


# ============= MAIN EXECUTION =============

if __name__ == "__main__":
    print("=" * 80)
    print("INVERSE INFERENCE USING MCMC (Markov Chain Monte Carlo)")
    print("=" * 80)
    
    # Simulate observed data from true model
    np.random.seed(42)
    TRUE_P = 0.7
    N_TRIALS = 8
    N_OBSERVATIONS = 20
    
    print(f"\n[1] Generating Synthetic Observed Data...")
    print(f"    True p (success probability): {TRUE_P}")
    print(f"    Number of trials per observation: {N_TRIALS}")
    print(f"    Number of observations: {N_OBSERVATIONS}")
    
    observed_counts = np.random.binomial(N_TRIALS, TRUE_P, size=N_OBSERVATIONS)
    print(f"    Observed counts: {observed_counts}")
    
    # Run MCMC
    print(f"\n[2] Running Metropolis-Hastings MCMC (10,000 iterations)...")
    sampler = MetropolisHastingsSampler(seed=42)
    posterior_samples, acceptance_rate = sampler.sample(
        data=observed_counts,
        n=N_TRIALS,
        n_iter=10_000,
        proposal_std=0.05,
        alpha=1.0,
        beta_param=1.0
    )
    print(f"    ✓ MCMC complete. Acceptance rate: {acceptance_rate:.1%}")
    
    # Analyze posterior
    burnin = 1000
    post_burnin = posterior_samples[burnin:]
    print(f"\n[3] Posterior Analysis (after {burnin} burn-in iterations)...")
    print(f"    Posterior mean: {post_burnin.mean():.4f}")
    print(f"    Posterior median: {np.median(post_burnin):.4f}")
    print(f"    Posterior std: {post_burnin.std():.4f}")
    print(f"    95% HPD interval: [{np.percentile(post_burnin, 2.5):.4f}, {np.percentile(post_burnin, 97.5):.4f}]")
    print(f"    True value: {TRUE_P:.4f}")
    
    # Posterior predictive check
    print(f"\n[4] Running Posterior Predictive Check (PPC)...")
    ppc_samples, _ = posterior_predictive_check(
        posterior_samples[burnin::10],  # Thin the chain
        observed_counts,
        n_trials=N_TRIALS,
        n_ppc_samples=100
    )
    print(f"    ✓ Generated {ppc_samples.size:,} synthetic observations")
    
    # Plots
    print(f"\n[5] Generating diagnostic plots...")
    fig1 = plot_mcmc_diagnostics(
        posterior_samples,
        burnin=burnin,
        save_path="mcmc_diagnostics.png"
    )
    
    fig2 = plot_posterior_predictive_check(
        ppc_samples,
        observed_counts,
        save_path="mcmc_posterior_predictive_check.png"
    )
    
    print("\n" + "=" * 80)
    print("✓ MCMC Inference complete!")
    print("   Outputs:")
    print("     - mcmc_diagnostics.png")
    print("     - mcmc_posterior_predictive_check.png")
    print("=" * 80)
    
    plt.close('all')
