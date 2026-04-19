from __future__ import annotations

from typing import Dict

import pandas as pd


# ============================================================
# Basic load metric calculation
# ============================================================

def calculate_basic_load_metrics(
    df: pd.DataFrame,
    load_column: str = "load_kwh",
) -> Dict[str, float]:
    """
    Calculate core load profile metrics for MVP.

    Metrics:
    - peak_load_kwh
    - min_load_kwh
    - avg_load_kwh
    - peak_valley_diff_kwh
    - load_factor
    - total_load_kwh
    """
    if load_column not in df.columns:
        raise ValueError(f"Column '{load_column}' not found in dataframe.")

    if df.empty:
        raise ValueError("Input dataframe is empty.")

    peak_load = float(df[load_column].max())
    min_load = float(df[load_column].min())
    avg_load = float(df[load_column].mean())
    total_load = float(df[load_column].sum())
    peak_valley_diff = peak_load - min_load

    if peak_load > 0:
        load_factor = avg_load / peak_load
    else:
        load_factor = 0.0

    return {
        "peak_load_kwh": peak_load,
        "min_load_kwh": min_load,
        "avg_load_kwh": avg_load,
        "peak_valley_diff_kwh": float(peak_valley_diff),
        "load_factor": float(load_factor),
        "total_load_kwh": total_load,
    }


# ============================================================
# Time feature preparation
# ============================================================

def add_load_time_features(
    df: pd.DataFrame,
    time_column: str = "time",
) -> pd.DataFrame:
    """
    Add common time-based columns for analysis.
    """
    if time_column not in df.columns:
        raise ValueError(f"Column '{time_column}' not found in dataframe.")

    result = df.copy()
    result[time_column] = pd.to_datetime(result[time_column], errors="coerce")

    if result[time_column].isna().any():
        raise ValueError(f"Column '{time_column}' contains invalid datetime values.")

    result["date"] = result[time_column].dt.date
    result["hour"] = result[time_column].dt.hour
    result["month"] = result[time_column].dt.month
    result["day_of_week"] = result[time_column].dt.dayofweek
    result["day_name"] = result[time_column].dt.day_name()

    return result


# ============================================================
# Hourly load pattern analysis
# ============================================================

def calculate_hourly_load_profile(
    df: pd.DataFrame,
    load_column: str = "load_kwh",
    hour_column: str = "hour",
) -> pd.DataFrame:
    """
    Aggregate average load by hour of day.
    """
    required_columns = [load_column, hour_column]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    summary = (
        df.groupby(hour_column, as_index=False)
        .agg(
            avg_load_kwh=(load_column, "mean"),
            max_load_kwh=(load_column, "max"),
            min_load_kwh=(load_column, "min"),
        )
        .sort_values(hour_column)
        .reset_index(drop=True)
    )

    return summary


# ============================================================
# Daily load aggregation
# ============================================================

def calculate_daily_load_summary(
    df: pd.DataFrame,
    load_column: str = "load_kwh",
    date_column: str = "date",
) -> pd.DataFrame:
    """
    Aggregate daily load statistics.
    """
    required_columns = [load_column, date_column]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    summary = (
        df.groupby(date_column, as_index=False)
        .agg(
            total_load_kwh=(load_column, "sum"),
            avg_load_kwh=(load_column, "mean"),
            peak_load_kwh=(load_column, "max"),
            min_load_kwh=(load_column, "min"),
        )
    )

    summary["peak_valley_diff_kwh"] = (
        summary["peak_load_kwh"] - summary["min_load_kwh"]
    )

    return summary


# ============================================================
# Day-of-week analysis
# ============================================================

def calculate_weekday_load_summary(
    df: pd.DataFrame,
    load_column: str = "load_kwh",
    day_name_column: str = "day_name",
    day_of_week_column: str = "day_of_week",
) -> pd.DataFrame:
    """
    Aggregate average load by weekday.
    """
    required_columns = [load_column, day_name_column, day_of_week_column]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    summary = (
        df.groupby([day_of_week_column, day_name_column], as_index=False)
        .agg(
            avg_load_kwh=(load_column, "mean"),
            total_load_kwh=(load_column, "sum"),
        )
        .sort_values(day_of_week_column)
        .reset_index(drop=True)
    )

    return summary


# ============================================================
# Peak hour identification
# ============================================================

def identify_top_peak_hours(
    df: pd.DataFrame,
    top_n: int = 10,
    time_column: str = "time",
    load_column: str = "load_kwh",
) -> pd.DataFrame:
    """
    Identify top N peak load timestamps.
    """
    required_columns = [time_column, load_column]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    result = (
        df[[time_column, load_column]]
        .sort_values(load_column, ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )

    return result


# ============================================================
# End-to-end helper for MVP
# ============================================================

def summarize_load_analysis(
    df: pd.DataFrame,
    load_column: str = "load_kwh",
    time_column: str = "time",
    top_n_peaks: int = 10,
) -> Dict[str, object]:
    """
    Full MVP load analysis pipeline.

    Returns
    -------
    Dict[str, object]
        Includes:
        - basic_metrics
        - hourly_profile
        - daily_summary
        - weekday_summary
        - top_peak_hours
        - enriched_df
    """
    enriched_df = add_load_time_features(df, time_column=time_column)

    basic_metrics = calculate_basic_load_metrics(
        enriched_df,
        load_column=load_column,
    )

    hourly_profile = calculate_hourly_load_profile(
        enriched_df,
        load_column=load_column,
        hour_column="hour",
    )

    daily_summary = calculate_daily_load_summary(
        enriched_df,
        load_column=load_column,
        date_column="date",
    )

    weekday_summary = calculate_weekday_load_summary(
        enriched_df,
        load_column=load_column,
        day_name_column="day_name",
        day_of_week_column="day_of_week",
    )

    top_peak_hours = identify_top_peak_hours(
        enriched_df,
        top_n=top_n_peaks,
        time_column=time_column,
        load_column=load_column,
    )

    return {
        "basic_metrics": basic_metrics,
        "hourly_profile": hourly_profile,
        "daily_summary": daily_summary,
        "weekday_summary": weekday_summary,
        "top_peak_hours": top_peak_hours,
        "enriched_df": enriched_df,
    }