"""
components/charts.py — Fonctions graphiques réutilisables.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import PLOTLY_LAYOUT, COLOR_PRIMARY, COLOR_ACCENT, COLOR_SEQ


def bar_horizontal(df, x, y, color=None, title=""):
    fig = px.bar(
        df, x=x, y=y, orientation='h',
        color_discrete_sequence=[color or COLOR_PRIMARY]
    )
    fig.update_layout(**PLOTLY_LAYOUT, title=title)
    return fig


def bar_grouped(df, x, y, color, color_seq=None, title=""):
    fig = px.bar(
        df, x=x, y=y, color=color, barmode='group',
        color_discrete_sequence=color_seq or COLOR_SEQ
    )
    fig.update_layout(**PLOTLY_LAYOUT, title=title)
    return fig


def bar_stacked(df, x, y, color, color_seq=None, title=""):
    fig = px.bar(
        df, x=x, y=y, color=color, barmode='stack',
        color_discrete_sequence=color_seq or COLOR_SEQ
    )
    fig.update_layout(
        **PLOTLY_LAYOUT,
        xaxis_tickangle=-30,
        legend=dict(orientation='h', y=-0.25, title=''),
        title=title
    )
    return fig


def line_chart(df, x, y, color=None, color_seq=None, title=""):
    kwargs = dict(color_discrete_sequence=color_seq or [COLOR_PRIMARY])
    if color:
        kwargs['color'] = color
    fig = px.line(df, x=x, y=y, markers=True, **kwargs)
    fig.update_traces(line_width=2, marker_size=5)
    fig.update_layout(
        **PLOTLY_LAYOUT,
        xaxis_tickangle=-30,
        legend=dict(orientation='h', y=-0.25, title=''),
        title=title
    )
    return fig


def area_chart(df, x, y, color=None, title=""):
    fig = px.area(
        df, x=x, y=y,
        color_discrete_sequence=[color or COLOR_PRIMARY]
    )
    fig.update_traces(
        line_width=2,
        fill='tozeroy',
        fillcolor='rgba(37,99,235,0.08)'
    )
    fig.update_layout(**PLOTLY_LAYOUT, xaxis_tickangle=-30, title=title)
    return fig


def pie_chart(df, values, names, color_seq=None, title=""):
    fig = px.pie(
        df, values=values, names=names,
        color_discrete_sequence=color_seq or COLOR_SEQ,
        hole=0.45
    )
    fig.update_traces(textposition='outside', textinfo='percent+label')
    fig.update_layout(**PLOTLY_LAYOUT, title=title)
    return fig


def scatter_chart(df, x, y, size, hover, color_seq=None, title=""):
    fig = px.scatter(
        df, x=x, y=y, size=size, hover_name=hover,
        color_discrete_sequence=color_seq or [COLOR_PRIMARY]
    )
    fig.update_layout(**PLOTLY_LAYOUT, title=title)
    return fig


def heatmap(df, title="", color_scale="Blues"):
    fig = px.imshow(
        df, aspect='auto',
        color_continuous_scale=color_scale,
        labels=dict(color="CA (R$)")
    )
    fig.update_layout(**PLOTLY_LAYOUT, title=title)
    return fig


def bar_with_vline(df, x, y, vline_value, vline_label, color=None, title=""):
    fig = px.bar(
        df, x=x, y=y, orientation='h',
        color_discrete_sequence=[color or COLOR_ACCENT]
    )
    fig.add_vline(
        x=vline_value,
        line_dash="dot",
        line_color="#6b7280",
        line_width=1.5,
        annotation_text=vline_label,
        annotation_font_size=11,
        annotation_font_color="#6b7280"
    )
    fig.update_layout(**PLOTLY_LAYOUT, title=title)
    return fig