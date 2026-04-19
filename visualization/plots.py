from __future__ import annotations

from typing import Optional

import pandas as pd
import plotly.graph_objects as go

from utils.i18n import get_text


# ============================================================
# Internal language / label helpers
# ============================================================

def _contains_chinese(text: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in str(text))


def _infer_language(*texts: str) -> str:
    for text in texts:
        if text and _contains_chinese(text):
            return "zh"
    return "en"


def _plot_text(language: str) -> dict:
    t = get_text(language)
    return {
        "load": t["plot_load"],
        "avg_load": t["plot_avg_load"],
        "price": t["plot_price"],
        "charge_from_grid": t["plot_charge_from_grid"],
        "discharge_to_load": t["plot_discharge_to_load"],
        "soc": t["plot_soc"],
        "original_load": t["plot_original_load"],
        "optimized_net_load": t["plot_optimized_net_load"],
        "cash_flow": t["plot_cash_flow"],
        "kpi_values": t["plot_kpi_values"],
        "payback_years": t["plot_payback_years"],
        "roi": t["plot_roi"],
        "annual_net_benefit": t["plot_annual_net_benefit"],
        "factory_load_curve": t["factory_load_curve"],
        "avg_load_by_hour": t["avg_load_by_hour"],
        "load_curve_with_tariff_price": t["load_with_price"],
        "electricity_cost_share_by_tariff_period": t["tariff_share_pie"],
        "storage_charge_discharge_soc": t["storage_soc_chart"],
        "original_vs_optimized_grid_load": t["optimized_load_chart"],
        "electricity_cost_reduction": t["cost_reduction_chart"],
        "project_cash_flows": t["project_cash_flows"],
        "key_financial_indicators": t["key_financial_indicators"],
        "time": t["time"],
        "hour_of_day": t["hour_of_day"],
        "load_kwh": t["load_kwh_axis"],
        "avg_load_kwh": t["avg_load_kwh_axis"],
        "price_axis": t["price_axis"],
        "charge_discharge_kwh": t["charge_discharge_axis"],
        "soc_axis": t["soc_axis"],
        "relative_cost_pct": t["relative_cost_axis"],
        "year": t["year"],
        "cash_flow_axis": t["cash_flow_axis"],
        "metric": t["metric_axis"],
        "value": t["value_axis"],
        "before_storage": t["before_storage"],
        "after_storage": t["after_storage"],
    }


# ============================================================
# Shared layout helper
# ============================================================

def _build_base_layout(
    title: str,
    xaxis_title: str = "",
    yaxis_title: str = "",
    height: int = 420,
) -> dict:
    return {
        "title": {"text": title, "x": 0.02, "y": 0.97, "pad": {"b": 24}},
        "xaxis": {"title": xaxis_title},
        "yaxis": {"title": yaxis_title},
        "height": height,
        "template": "plotly_white",
        "margin": {"l": 40, "r": 30, "t": 95, "b": 40},
        "legend": {"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
        "hovermode": "x unified",
    }


# ============================================================
# Export config helper
# ============================================================

def get_plot_config(filename: str = "chart") -> dict:
    return {
        "toImageButtonOptions": {
            "format": "png",
            "filename": filename,
            "height": 1800,
            "width": 2800,
            "scale": 4,
        }
    }


# ============================================================
# Load profile plots
# ============================================================

def plot_load_curve(
    df: pd.DataFrame,
    time_column: str = "time",
    load_column: str = "load_kwh",
    title: str = "Factory Load Curve",
    xaxis_title: str = "Time",
    yaxis_title: str = "Load (kWh)",
    load_label: Optional[str] = None,
) -> go.Figure:
    required_columns = [time_column, load_column]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    language = _infer_language(title, xaxis_title, yaxis_title)
    t = _plot_text(language)
    load_label = load_label or t["load"]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df[time_column],
            y=df[load_column],
            mode="lines",
            name=load_label,
        )
    )

    fig.update_layout(
        **_build_base_layout(
            title=title,
            xaxis_title=xaxis_title,
            yaxis_title=yaxis_title,
        )
    )
    return fig


def plot_hourly_average_load(
    hourly_profile_df: pd.DataFrame,
    hour_column: str = "hour",
    avg_load_column: str = "avg_load_kwh",
    title: str = "Average Load by Hour",
    xaxis_title: str = "Hour of Day",
    yaxis_title: str = "Average Load (kWh)",
    avg_load_label: Optional[str] = None,
) -> go.Figure:
    required_columns = [hour_column, avg_load_column]
    missing_columns = [col for col in required_columns if col not in hourly_profile_df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    language = _infer_language(title, xaxis_title, yaxis_title)
    t = _plot_text(language)
    avg_load_label = avg_load_label or t["avg_load"]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=hourly_profile_df[hour_column],
            y=hourly_profile_df[avg_load_column],
            mode="lines+markers",
            name=avg_load_label,
        )
    )

    fig.update_layout(
        **_build_base_layout(
            title=title,
            xaxis_title=xaxis_title,
            yaxis_title=yaxis_title,
        )
    )
    return fig


# ============================================================
# Tariff and cost plots
# ============================================================

def plot_tariff_load_curve(
    df: pd.DataFrame,
    time_column: str = "time",
    load_column: str = "load_kwh",
    price_column: str = "price",
    title: str = "Load Curve with Tariff Price",
    xaxis_title: str = "Time",
    yaxis_title_left: str = "Load (kWh)",
    yaxis_title_right: str = "Price",
    load_label: Optional[str] = None,
    price_label: Optional[str] = None,
) -> go.Figure:
    required_columns = [time_column, load_column, price_column]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    language = _infer_language(title, xaxis_title, yaxis_title_left, yaxis_title_right)
    t = _plot_text(language)
    load_label = load_label or t["load"]
    price_label = price_label or t["price"]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df[time_column],
            y=df[load_column],
            mode="lines",
            name=load_label,
            yaxis="y1",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df[time_column],
            y=df[price_column],
            mode="lines",
            name=price_label,
            yaxis="y2",
        )
    )

    fig.update_layout(
        title={"text": title, "x": 0.02, "y": 0.97, "pad": {"b": 24}},
        xaxis={"title": xaxis_title},
        yaxis={"title": yaxis_title_left},
        yaxis2={
            "title": yaxis_title_right,
            "overlaying": "y",
            "side": "right",
        },
        height=420,
        template="plotly_white",
        margin={"l": 40, "r": 40, "t": 95, "b": 40},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
        hovermode="x unified",
    )
    return fig


def plot_tariff_cost_share_pie(
    breakdown_df: pd.DataFrame,
    label_column: str = "tariff_period",
    value_column: str = "total_cost",
    title: str = "Electricity Cost Share by Tariff Period",
) -> go.Figure:
    required_columns = [label_column, value_column]
    missing_columns = [col for col in required_columns if col not in breakdown_df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    fig = go.Figure(
        data=[
            go.Pie(
                labels=breakdown_df[label_column],
                values=breakdown_df[value_column],
                hole=0.25,
            )
        ]
    )

    fig.update_layout(
        title={"text": title, "x": 0.02, "y": 0.97, "pad": {"b": 24}},
        height=430,
        template="plotly_white",
        margin={"l": 30, "r": 30, "t": 95, "b": 30},
    )
    return fig


# ============================================================
# Storage operation plots
# ============================================================

def plot_storage_operation(
    df: pd.DataFrame,
    time_column: str = "time",
    charge_column: str = "storage_charge_kwh_grid",
    discharge_column: str = "storage_discharge_kwh_load",
    soc_column: str = "soc_kwh",
    title: str = "Storage Charge, Discharge, and SOC",
    xaxis_title: str = "Time",
    yaxis_title_left: str = "Charge / Discharge (kWh)",
    yaxis_title_right: str = "SOC (kWh)",
    charge_label: Optional[str] = None,
    discharge_label: Optional[str] = None,
    soc_label: Optional[str] = None,
) -> go.Figure:
    required_columns = [time_column, charge_column, discharge_column, soc_column]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    language = _infer_language(title, xaxis_title, yaxis_title_left, yaxis_title_right)
    t = _plot_text(language)
    charge_label = charge_label or t["charge_from_grid"]
    discharge_label = discharge_label or t["discharge_to_load"]
    soc_label = soc_label or t["soc"]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df[time_column],
            y=df[charge_column],
            name=charge_label,
            yaxis="y1",
        )
    )

    fig.add_trace(
        go.Bar(
            x=df[time_column],
            y=df[discharge_column],
            name=discharge_label,
            yaxis="y1",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df[time_column],
            y=df[soc_column],
            mode="lines",
            name=soc_label,
            yaxis="y2",
        )
    )

    fig.update_layout(
        title={"text": title, "x": 0.02, "y": 0.97, "pad": {"b": 24}},
        xaxis={"title": xaxis_title},
        yaxis={"title": yaxis_title_left},
        yaxis2={
            "title": yaxis_title_right,
            "overlaying": "y",
            "side": "right",
        },
        barmode="group",
        height=460,
        template="plotly_white",
        margin={"l": 40, "r": 40, "t": 95, "b": 40},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
        hovermode="x unified",
    )
    return fig


def plot_original_vs_optimized_load(
    df: pd.DataFrame,
    time_column: str = "time",
    original_load_column: str = "load_kwh",
    optimized_load_column: str = "net_load_kwh",
    title: str = "Original vs Optimized Grid Load",
    xaxis_title: str = "Time",
    yaxis_title: str = "Load (kWh)",
    original_label: Optional[str] = None,
    optimized_label: Optional[str] = None,
) -> go.Figure:
    required_columns = [time_column, original_load_column, optimized_load_column]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    language = _infer_language(title, xaxis_title, yaxis_title)
    t = _plot_text(language)
    original_label = original_label or t["original_load"]
    optimized_label = optimized_label or t["optimized_net_load"]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df[time_column],
            y=df[original_load_column],
            mode="lines",
            name=original_label,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df[time_column],
            y=df[optimized_load_column],
            mode="lines",
            name=optimized_label,
        )
    )

    fig.update_layout(
        **_build_base_layout(
            title=title,
            xaxis_title=xaxis_title,
            yaxis_title=yaxis_title,
        )
    )
    return fig


# ============================================================
# Cost comparison plots
# ============================================================

def plot_cost_reduction_horizontal_bar(
    original_cost: float,
    optimized_cost: float,
    title: str = "Electricity Cost Reduction",
    xaxis_title: str = "Relative Cost (%)",
    original_label: str = "Before Storage",
    optimized_label: str = "After Storage",
) -> go.Figure:
    if original_cost <= 0:
        raise ValueError("original_cost must be greater than 0.")

    original_pct = 100.0
    optimized_pct = optimized_cost / original_cost * 100.0

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=[original_pct],
            y=[""],
            orientation="h",
            name=original_label,
            text=[f"{original_pct:.1f}%"],
            textposition="inside",
            width=0.22,
        )
    )

    fig.add_trace(
        go.Bar(
            x=[optimized_pct],
            y=[""],
            orientation="h",
            name=optimized_label,
            text=[f"{optimized_pct:.1f}%"],
            textposition="inside",
            width=0.22,
        )
    )

    fig.update_layout(
        title={"text": title, "x": 0.02, "y": 0.95, "pad": {"b": 0}},
        xaxis={"title": xaxis_title},
        yaxis={"showticklabels": False, "title": ""},
        height=300,
        template="plotly_white",
        margin={"l": 40, "r": 30, "t": 40, "b": 120},
        hovermode="x unified",
        barmode="overlay",
        showlegend=False,
    )
    return fig


# ============================================================
# Finance plots
# ============================================================

def plot_project_cash_flows(
    cash_flows: list[float],
    title: str = "Project Cash Flows",
    xaxis_title: str = "Year",
    yaxis_title: str = "Cash Flow",
    cash_flow_label: Optional[str] = None,
) -> go.Figure:
    years = list(range(len(cash_flows)))
    language = _infer_language(title, xaxis_title, yaxis_title)
    t = _plot_text(language)
    cash_flow_label = cash_flow_label or t["cash_flow"]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=years,
            y=cash_flows,
            name=cash_flow_label,
        )
    )

    fig.update_layout(
        **_build_base_layout(
            title=title,
            xaxis_title=xaxis_title,
            yaxis_title=yaxis_title,
        )
    )
    return fig


# ============================================================
# Optional summary chart
# ============================================================

def plot_kpi_comparison(
    payback_years: Optional[float],
    roi: Optional[float],
    annual_net_benefit: Optional[float],
    title: str = "Key Financial Indicators",
    xaxis_title: str = "Metric",
    yaxis_title: str = "Value",
    payback_label: Optional[str] = None,
    roi_label: Optional[str] = None,
    annual_net_benefit_label: Optional[str] = None,
    kpi_values_label: Optional[str] = None,
) -> go.Figure:
    language = _infer_language(title, xaxis_title, yaxis_title)
    t = _plot_text(language)

    payback_label = payback_label or t["payback_years"]
    roi_label = roi_label or t["roi"]
    annual_net_benefit_label = annual_net_benefit_label or t["annual_net_benefit"]
    kpi_values_label = kpi_values_label or t["kpi_values"]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=[payback_label, roi_label, annual_net_benefit_label],
            y=[
                payback_years if payback_years is not None else 0.0,
                roi if roi is not None else 0.0,
                annual_net_benefit if annual_net_benefit is not None else 0.0,
            ],
            name=kpi_values_label,
        )
    )

    fig.update_layout(
        **_build_base_layout(
            title=title,
            xaxis_title=xaxis_title,
            yaxis_title=yaxis_title,
            height=380,
        )
    )
    return fig