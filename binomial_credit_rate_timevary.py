"""
Module: binomial_credit_rate_timevary.py
Purpose: Reproducible binomial and trinomial credit rate distribution models
for Chapter 1 - Parameter Uncertainty and Structural Change.

Source: turn0browsertab744690698
Author: ML Finance Course - Chapter 1
Date: 2026-03-27

Requirements:
  numpy, pandas, scipy, matplotlib
"""

import numpy as np
import pandas as pd
from scipy.stats import binom
import matplotlib.pyplot as plt


def credit_rate_distribution(fed_meetings=8, prob_raise=0.7, base_rate=12.0, per_raise_bps=25):
    """
    Binomial model: constant probability of rate hike each meeting.
    
    Parameters:
    -----------
    fed_meetings : int
        Number of Fed meetings over the period (e.g., 12 months).
    prob_raise : float
        Probability that the Fed raises rates at each meeting (0 <= p <= 1).
    base_rate : float
        Starting credit card rate (%).
    per_raise_bps : float
        Basis points added per hike (e.g., 25).
    
    Returns:
    --------
    pd.DataFrame with columns:
      - cc_rate: predicted credit card rate (%)
      - prob: probability of that rate (PMF)
    
    Notes:
    ------
    Reproduces Figure 1-2: Predicted range of credit card rates.
    Each outcome (0 to fed_meetings raises) has probability given by binomial PMF.
    """
    k = np.arange(0, fed_meetings + 1)
    pmf = binom.pmf(k, n=fed_meetings, p=prob_raise)
    cc_rates = base_rate + (k * per_raise_bps) / 100.0
    
    return pd.DataFrame({"cc_rate": cc_rates, "prob": pmf})


def credit_rate_timevary(fed_meetings=8, prob_schedule=None, base_rate=12.0, per_raise_bps=25):
    """
    Time-varying probability model: each meeting has its own probability of hike.
    Uses convolution of Bernoulli trials to compute exact distribution.
    
    Parameters:
    -----------
    fed_meetings : int
        Number of Fed meetings.
    prob_schedule : array-like, shape (fed_meetings,)
        Per-meeting probability of rate hike. If None, defaults to [0.7, 0.7, ..., 0.7].
    base_rate : float
        Starting credit card rate (%).
    per_raise_bps : float
        Basis points per hike.
    
    Returns:
    --------
    pd.DataFrame with columns:
      - cc_rate: predicted rate
      - prob: probability of that rate
    
    Notes:
    ------
    Example: If policy is tightening, prob_schedule might be [0.5, 0.6, 0.7, 0.8, 0.8, 0.7, 0.5, 0.4]
    (increasing then decreasing).
    
    Computation: Start with pmf=[1], then convolve with Bernoulli(p) for each meeting.
    """
    if prob_schedule is None:
        prob_schedule = np.repeat(0.7, fed_meetings)
    prob_schedule = np.asarray(prob_schedule)
    
    # Start with pmf for 0 raises
    pmf = np.array([1.0])
    
    # Convolve with Bernoulli outcomes for each meeting
    for p in prob_schedule:
        # Bernoulli(p): outcome is 0 with prob (1-p), outcome is 1 with prob p
        pmf = np.convolve(pmf, np.array([1 - p, p]))
    
    # Map outcomes to credit card rates
    k = np.arange(0, len(pmf))
    cc_rates = base_rate + (k * per_raise_bps) / 100.0
    
    return pd.DataFrame({"cc_rate": cc_rates, "prob": pmf})


def convert_to_trinomial_after_change(
    fed_meetings=8,
    prob_schedule=None,
    change_step=None,
    base_rate=12.0,
    per_raise_bps=25
):
    """
    Structural change model: binomial before change, trinomial after.
    
    After a structural break (e.g., policy pivot), each meeting outcome can be:
      -1: rate cut (probability p_cut)
       0: neutral (probability p_neutral)
      +1: rate hike (probability p_raise)
    
    Parameters:
    -----------
    fed_meetings : int
        Total number of meetings.
    prob_schedule : array-like
        Per-meeting probabilities; before change: Bernoulli probabilities.
        After change: interpreted as p_raise for trinomial.
    change_step : int (1-based)
        Meeting index after which trinomial starts.
        E.g., change_step=5 means meetings 1-4 are binomial, 5-8 are trinomial.
    base_rate : float
        Starting rate.
    per_raise_bps : float
        Basis points per unit change.
    
    Returns:
    --------
    pd.DataFrame: distribution of final rate, accounting for cuts and hikes.
    
    Notes:
    ------
    This demonstrates adaptation to regime change (e.g., pivot from tightening to cutting).
    """
    if prob_schedule is None:
        prob_schedule = np.repeat(0.7, fed_meetings)
    prob_schedule = list(prob_schedule)
    
    # If no change or change after last meeting, return binomial timevary
    if change_step is None or change_step >= fed_meetings:
        return credit_rate_timevary(fed_meetings, prob_schedule, base_rate, per_raise_bps)
    
    # Split into before and after
    before = prob_schedule[:change_step]
    after = prob_schedule[change_step:]
    
    # Build pmf before change (binomial-like)
    pmf_before = np.array([1.0])
    for p in before:
        pmf_before = np.convolve(pmf_before, np.array([1 - p, p]))
    
    # Build pmf after change (trinomial): outcomes in {-1, 0, +1}
    # Parameterization: p_raise = p, p_neutral = 0.1, p_cut = 1 - p_raise - p_neutral
    pmf_after = np.array([1.0])
    p_neutral = 0.1
    
    for p in after:
        p_raise = min(max(p, 0.0), 1.0)  # clamp to [0,1]
        p_cut = max(0.0, 1.0 - p_raise - p_neutral)
        p_neu = 1.0 - p_raise - p_cut
        # Trinomial outcome in [-1, 0, +1]
        pmf_after = np.convolve(pmf_after, np.array([p_cut, p_neu, p_raise]))
    
    # Combine distributions:
    # before_count (0 to len(pmf_before)-1) + after_net (-len(pmf_after)//2 to +len(pmf_after)//2)
    totals_dict = {}
    for i, pb in enumerate(pmf_before):
        for j, pa in enumerate(pmf_after):
            # after is indexed from -(len-1)//2 to +(len-1)//2 approximately
            after_idx = j - (len(pmf_after) - 1) // 2
            total = i + after_idx
            totals_dict[total] = totals_dict.get(total, 0.0) + pb * pa
    
    # Convert to sorted DataFrame
    totals_sorted = sorted(totals_dict.items(), key=lambda x: x[0])
    k_vals = np.array([t[0] for t in totals_sorted])
    probs = np.array([t[1] for t in totals_sorted])
    cc_rates = base_rate + (k_vals * per_raise_bps) / 100.0
    
    return pd.DataFrame({"cc_rate": cc_rates, "prob": probs})


def plot_figure_1_2_timevary(probs=[0.6, 0.7, 0.8, 0.9], fed_meetings=8, 
                              base_rate=12.0, per_raise_bps=25, timevary=False):
    """
    Reproduce Figure 1-2: Distribution of credit card rates for different p values.
    
    Parameters:
    -----------
    probs : list
        Probabilities to plot (usually [0.6, 0.7, 0.8, 0.9]).
    fed_meetings : int
        Number of Fed meetings.
    base_rate : float
        Base credit card rate.
    per_raise_bps : float
        Basis points per hike.
    timevary : bool
        If True, use time-varying probabilities (schedule: p + 0.02*meeting_idx).
        If False, use constant probabilities.
    
    Returns:
    --------
    matplotlib.figure.Figure
    """
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    axs = axs.flatten()
    
    for i, p in enumerate(probs):
        if not timevary:
            df = credit_rate_distribution(fed_meetings, p, base_rate, per_raise_bps)
        else:
            # Time-varying schedule: start at p, increase by 0.02 per meeting (tightening)
            schedule = np.clip(p + 0.02 * np.arange(fed_meetings), 0.0, 1.0)
            df = credit_rate_timevary(fed_meetings, schedule, base_rate, per_raise_bps)
        
        axs[i].bar(df["cc_rate"], df["prob"], width=0.18, alpha=0.7, edgecolor="black")
        axs[i].set_title(f"Probability of raising rates at each meeting: {p}")
        axs[i].set_xlabel("Predicted range of credit card rates after 12 months (%)")
        axs[i].set_ylabel("Probability of credit card rate")
        axs[i].grid(axis="y", alpha=0.3)
        
        # Compute and display mean
        mean_rate = (df["cc_rate"] * df["prob"]).sum()
        axs[i].axvline(mean_rate, color="red", linestyle="--", linewidth=2, label=f"Mean: {mean_rate:.2f}%")
        axs[i].legend()
    
    fig.suptitle("Figure 1-2: Predicted Credit Card Rates (Binomial Model)", fontsize=14, fontweight="bold")
    plt.tight_layout()
    
    return fig


def summary_statistics(df):
    """
    Compute summary statistics from a distribution DataFrame.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Must have columns 'cc_rate' and 'prob'.
    
    Returns:
    --------
    dict with keys: mean, median, std, min, max, mode, prob_exceed_threshold
    """
    cc_rate = df["cc_rate"].values
    prob = df["prob"].values
    
    mean = (cc_rate * prob).sum()
    median_idx = np.where(prob.cumsum() >= 0.5)[0][0]
    median = cc_rate[median_idx]
    variance = ((cc_rate - mean) ** 2 * prob).sum()
    std = np.sqrt(variance)
    
    mode_idx = np.argmax(prob)
    mode = cc_rate[mode_idx]
    
    return {
        "mean": mean,
        "median": median,
        "std": std,
        "min": cc_rate.min(),
        "max": cc_rate.max(),
        "mode": mode,
        "mode_prob": prob[mode_idx]
    }


if __name__ == "__main__":
    """
    Example execution: reproduce Figure 1-2 and save.
    """
    # Static binomial model
    fig_const = plot_figure_1_2_timevary(probs=[0.6, 0.7, 0.8, 0.9], timevary=False)
    fig_const.savefig("figure_1_2_credit_rates_constant_p.png", dpi=150, bbox_inches="tight")
    print("✓ Saved: figure_1_2_credit_rates_constant_p.png")
    
    # Time-varying model
    fig_vary = plot_figure_1_2_timevary(probs=[0.6, 0.7, 0.8, 0.9], timevary=True)
    fig_vary.savefig("figure_1_2_credit_rates_timevary_p.png", dpi=150, bbox_inches="tight")
    print("✓ Saved: figure_1_2_credit_rates_timevary_p.png")
    
    # Example: trinomial after structural change
    print("\n--- Example: Trinomial model after policy change ---")
    prob_before = np.repeat(0.7, 4)  # 4 meetings of tightening
    prob_after = np.repeat(0.4, 4)   # 4 meetings of cutting bias
    combined_schedule = np.concatenate([prob_before, prob_after])
    
    df_trinomial = convert_to_trinomial_after_change(
        fed_meetings=8,
        prob_schedule=combined_schedule,
        change_step=4
    )
    
    stats = summary_statistics(df_trinomial)
    print(f"Mean rate: {stats['mean']:.3f}%")
    print(f"Median rate: {stats['median']:.3f}%")
    print(f"Std dev: {stats['std']:.3f}%")
    
    plt.show()
