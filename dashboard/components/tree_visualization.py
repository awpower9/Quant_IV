"""
tree_visualization.py — Binomial/trinomial tree renderer component.

Placeholder for interactive tree visualization using Plotly.
"""

from dash import html, dcc
import plotly.graph_objects as go


def create_tree_chart(
    tree_data: list[list[float]] | None = None,
    title: str = "Option Price Tree",
) -> dcc.Graph:
    """
    Create a Plotly figure showing a binomial/trinomial tree.

    Args:
        tree_data: Nested list of node values per time step.
        title:     Chart title.

    Returns:
        A dcc.Graph component.
    """
    fig = go.Figure()

    if tree_data and len(tree_data) > 1:
        # Plot nodes at each time step
        for step, values in enumerate(tree_data):
            n = len(values)
            for i, val in enumerate(values):
                y_pos = (n - 1) / 2.0 - i  # center vertically
                fig.add_trace(go.Scatter(
                    x=[step], y=[y_pos],
                    mode="markers+text",
                    text=[f"{val:.2f}"],
                    textposition="top center",
                    marker=dict(size=8, color="#00d4ff"),
                    showlegend=False,
                ))

    fig.update_layout(
        title=title,
        template="plotly_dark",
        xaxis_title="Time Step",
        yaxis_title="Node Position",
        height=500,
    )

    return dcc.Graph(figure=fig, id="tree-chart")
