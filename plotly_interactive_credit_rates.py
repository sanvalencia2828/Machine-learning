"""
Module: plotly_interactive_credit_rates.py
Purpose: Interactive Plotly visualization with slider for parameter uncertainty exploration.

Allows users to adjust probability of Fed rate hikes in real-time and see 
distribution of predicted credit card rates update dynamically.

Source: turn0browsertab744690698
Author: ML Finance Course - Chapter 1
Date: 2026-03-27

Requirements:
  plotly, numpy, pandas
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def make_figure_interactive_slider(
    initial_p=0.7, 
    fed_meetings=8, 
    base_rate=12.0, 
    per_raise_bps=25
):
    """
    Create interactive Plotly figure with slider to vary p (probability of rate hike).
    
    Parameters:
    -----------
    initial_p : float
        Initial probability displayed (0 <= p <= 1).
    fed_meetings : int
        Number of Fed meetings.
    base_rate : float
        Starting credit card rate (%).
    per_raise_bps : float
        Basis points added per hike.
    
    Returns:
    --------
    plotly.graph_objects.Figure
    
    Usage:
    ------
    fig = make_figure_interactive_slider(initial_p=0.7)
    fig.show()
    # or save to HTML
    fig.write_html('interactive_credit_rates.html')
    """
    
    # Import directly here to compute binomial PMF
    from scipy.stats import binom
    
    def compute_distribution(p):
        """Helper: compute binomial distribution for given p."""
        k = np.arange(0, fed_meetings + 1)
        pmf = binom.pmf(k, n=fed_meetings, p=p)
        cc_rates = base_rate + (k * per_raise_bps) / 100.0
        return cc_rates, pmf
    
    # Initial data
    cc_rates_init, pmf_init = compute_distribution(initial_p)
    
    # Create figure
    fig = go.Figure()
    
    # Add initial trace
    fig.add_trace(
        go.Bar(
            x=cc_rates_init,
            y=pmf_init,
            name=f'p={initial_p}',
            marker=dict(color='rgba(31, 119, 180, 0.7)', line=dict(color='darkblue', width=1.5)),
            hovertemplate='<b>Rate: %{x:.2f}%</b><br>Probability: %{y:.4f}<extra></extra>'
        )
    )
    
    # Create frames for slider animation
    ps = np.round(np.arange(0.0, 1.01, 0.05), 2).tolist()
    frames = []
    
    for p in ps:
        cc_rates_p, pmf_p = compute_distribution(p)
        frames.append(
            go.Frame(
                data=[
                    go.Bar(
                        x=cc_rates_p,
                        y=pmf_p,
                        marker=dict(color='rgba(31, 119, 180, 0.7)', line=dict(color='darkblue', width=1.5)),
                        hovertemplate='<b>Rate: %{x:.2f}%</b><br>Probability: %{y:.4f}<extra></extra>'
                    )
                ],
                name=str(p)
            )
        )
    
    fig.frames = frames
    
    # Create slider steps
    slider_steps = []
    for p in ps:
        slider_steps.append(
            dict(
                args=[
                    [str(p)],
                    {'frame': {'duration': 250, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 250}}
                ],
                label=f'{p:.2f}',
                method='animate'
            )
        )
    
    # Add slider
    sliders = [
        dict(
            active=int(initial_p * 100 / 5),
            steps=slider_steps,
            transition={'duration': 300, 'easing': 'cubic-in-out'},
            x=0.0,
            y=-0.15,
            len=1.0,
            xanchor='left',
            yanchor='top',
            pad=dict(b=10, t=50),
            currentvalue=dict(
                prefix='Probability of Fed rate hike (p) = ',
                xanchor='center',
                visible=True,
                font=dict(size=12)
            ),
            tickcolor='lightgray'
        )
    ]
    
    # Add play/pause buttons
    updatemenus = [
        dict(
            type='buttons',
            showactive=False,
            buttons=[
                dict(
                    label='▶ Play',
                    method='animate',
                    args=[None, {
                        'frame': {'duration': 300, 'redraw': True},
                        'fromcurrent': True,
                        'transition': {'duration': 200, 'easing': 'quadratic-in-out'}
                    }]
                ),
                dict(
                    label='⏸ Pause',
                    method='animate',
                    args=[[None], {
                        'frame': {'duration': 0, 'redraw': False},
                        'mode': 'immediate',
                        'transition': {'duration': 0}
                    }]
                )
            ],
            x=0.0,
            y=-0.05,
            xanchor='left',
            yanchor='top'
        )
    ]
    
    # Update layout
    fig.update_layout(
        updatemenus=updatemenus,
        sliders=sliders,
        title=dict(
            text=f'<b>Credit Card Rate Distribution — Binomial Model</b><br>' +
                 f'<sub>Fed meetings: {fed_meetings} | Base rate: {base_rate}% | Per-hike: {per_raise_bps} bps</sub>',
            x=0.5,
            xanchor='center',
            font=dict(size=14)
        ),
        xaxis_title='Predicted Credit Card Rate (%)',
        yaxis_title='Probability',
        hovermode='x unified',
        height=700,
        margin=dict(b=150, t=100, l=80, r=80),
        plot_bgcolor='rgba(240, 240, 240, 0.5)',
        paper_bgcolor='white',
        font=dict(family='Arial, sans-serif', size=11),
        showlegend=False
    )
    
    fig.update_xaxes(gridcolor='lightgray', zeroline=False)
    fig.update_yaxes(gridcolor='lightgray', zeroline=True)
    
    return fig


def make_comparison_figure(ps=[0.5, 0.7, 0.9]):
    """
    Create a comparison figure showing three distributions side-by-side.
    
    Parameters:
    -----------
    ps : list
        List of probabilities to compare.
    
    Returns:
    --------
    plotly.graph_objects.Figure with subplots
    """
    from scipy.stats import binom
    
    n_rows = 1
    n_cols = len(ps)
    colors = ['rgba(31, 119, 180, 0.7)', 'rgba(255, 127, 14, 0.7)', 'rgba(44, 160, 44, 0.7)']
    
    fig = make_subplots(
        rows=n_rows,
        cols=n_cols,
        subplot_titles=[f'p = {p}' for p in ps],
        vertical_spacing=0.1
    )
    
    for col, p in enumerate(ps, start=1):
        k = np.arange(0, 9)  # 8 meetings
        pmf = binom.pmf(k, n=8, p=p)
        cc_rates = 12.0 + (k * 25) / 100.0
        
        mean_rate = (cc_rates * pmf).sum()
        
        fig.add_trace(
            go.Bar(
                x=cc_rates,
                y=pmf,
                marker=dict(color=colors[col - 1], line=dict(color='black', width=1)),
                name=f'p={p}',
                hovertemplate='<b>Rate: %{x:.2f}%</b><br>Prob: %{y:.4f}<extra></extra>',
                showlegend=False
            ),
            row=1,
            col=col
        )
        
        # Add mean line
        fig.add_vline(x=mean_rate, line_dash='dash', line_color='red', 
                      row=1, col=col, annotation_text=f'μ={mean_rate:.2f}%',
                      annotation_position='top right')
    
    fig.update_xaxes(title_text='Credit Card Rate (%)', row=1, col=1)
    fig.update_xaxes(title_text='Credit Card Rate (%)', row=1, col=2)
    fig.update_xaxes(title_text='Credit Card Rate (%)', row=1, col=3)
    
    fig.update_yaxes(title_text='Probability', row=1, col=1)
    
    fig.update_layout(
        title_text='<b>Sensitivity Analysis: How Probability Affects Credit Card Rate Distribution</b>',
        height=500,
        showlegend=False,
        plot_bgcolor='rgba(240, 240, 240, 0.5)'
    )
    
    return fig


def make_waterfall_sensitivity():
    """
    Create Waterfall chart showing sensitivity of mean rate to changes in p.
    
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    from scipy.stats import binom
    
    ps = np.arange(0.0, 1.01, 0.1)
    means = []
    
    for p in ps:
        k = np.arange(0, 9)
        pmf = binom.pmf(k, n=8, p=p)
        cc_rates = 12.0 + (k * 25) / 100.0
        mean_rate = (cc_rates * pmf).sum()
        means.append(mean_rate)
    
    fig = go.Figure(
        data=[
            go.Scatter(
                x=ps,
                y=means,
                mode='lines+markers',
                name='Expected Rate',
                line=dict(color='blue', width=3),
                marker=dict(size=8, color='blue'),
                fill='tozeroy',
                fillcolor='rgba(31, 119, 180, 0.2)',
                hovertemplate='<b>p = %{x:.2f}</b><br>E[rate] = %{y:.3f}%<extra></extra>'
            )
        ]
    )
    
    fig.update_layout(
        title='<b>Sensitivity: Expected Credit Card Rate vs. Probability of Hike</b>',
        xaxis_title='Probability of Fed rate hike (p)',
        yaxis_title='Expected Credit Card Rate (%)',
        hovermode='x unified',
        height=500,
        plot_bgcolor='rgba(240, 240, 240, 0.5)',
        font=dict(family='Arial, sans-serif', size=11)
    )
    
    return fig


if __name__ == '__main__':
    """
    Example: Generate and save interactive figures.
    """
    
    # 1. Main interactive slider figure
    print("📊 Generating interactive slider figure...")
    fig_slider = make_figure_interactive_slider(initial_p=0.7)
    fig_slider.write_html('interactive_credit_rates_slider.html')
    print("✓ Saved: interactive_credit_rates_slider.html")
    
    # 2. Comparison figure
    print("📊 Generating comparison figure (p=0.5, 0.7, 0.9)...")
    fig_compare = make_comparison_figure(ps=[0.5, 0.7, 0.9])
    fig_compare.write_html('comparison_three_scenarios.html')
    print("✓ Saved: comparison_three_scenarios.html")
    
    # 3. Sensitivity analysis
    print("📊 Generating sensitivity analysis figure...")
    fig_sensitivity = make_waterfall_sensitivity()
    fig_sensitivity.write_html('sensitivity_expected_rate.html')
    print("✓ Saved: sensitivity_expected_rate.html")
    
    print("\n✅ All interactive figures generated successfully!")
    print("   Open .html files in a web browser to explore.")
