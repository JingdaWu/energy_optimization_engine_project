from __future__ import annotations

from typing import Dict, Optional

import pandas as pd

from utils.validators import (
    validate_hour_label_groups,
    validate_hour_label_map,
    validate_hour_label_map_has_prices,
    validate_tariff_price_dict,
)


# ============================================================
# Tariff label constants
# ============================================================

TARIFF_LABELS = [
    "critical_peak",
    "peak",
    "flat",
    "valley",
    "super_valley",
]


# ============================================================
# Hour label map builders
# ============================================================

def build_five_level_hour_label_map(
    critical_peak_hours: list[int],
    peak_hours: list[int],
    flat_hours: list[int],
    valley_hours: list[int],
    super_valley_hours: list[int],
) -> Dict[int, str]:
    """
    Build hour -> tariff label mapping for five-level TOU tariff.
    Empty groups are allowed as long as total assigned hours = 24.
    """
    validate_hour_label_groups(
        critical_peak_hours=critical_peak_hours,
        peak_hours=peak_hours,
        flat_hours=flat_hours,
        valley_hours=valley_hours,
        super_valley_hours=super_valley_hours,
        allow_empty_groups=True,
    )

    hour_label_map: Dict[int, str] = {}

    for hour in critical_peak_hours:
        hour_label_map[hour] = "critical_peak"

    for hour in peak_hours:
        hour_label_map[hour] = "peak"

    for hour in flat_hours:
        hour_label_map[hour] = "flat"

    for hour in valley_hours:
        hour_label_map[hour] = "valley"

    for hour in super_valley_hours:
        hour_label_map[hour] = "super_valley"

    validate_hour_label_map(hour_label_map)

    return hour_label_map


def build_price_dict(
    critical_peak_price: Optional[float] = None,
    peak_price: Optional[float] = None,
    flat_price: Optional[float] = None,
    valley_price: Optional[float] = None,
    super_valley_price: Optional[float] = None,
) -> Dict[str, Optional[float]]:
    """
    Build tariff label -> price mapping.
    Unused labels may have None price.
    """
    price_dict: Dict[str, Optional[float]] = {
        "critical_peak": critical_peak_price,
        "peak": peak_price,
        "flat": flat_price,
        "valley": valley_price,
        "super_valley": super_valley_price,
    }

    validate_tariff_price_dict(price_dict, allow_empty=True)
    return price_dict


# ============================================================
# Tariff assignment from hour label map
# ============================================================

def assign_tariff_labels_from_hour_map(
    df: pd.DataFrame,
    hour_label_map: Dict[int, str],
    time_column: str = "time",
    output_column: str = "tariff_period",
) -> pd.DataFrame:
    """
    Assign tariff label to each row based on hour of day.
    """
    if time_column not in df.columns:
        raise ValueError(f"Column '{time_column}' not found in dataframe.")

    validate_hour_label_map(hour_label_map)

    result = df.copy()
    result[time_column] = pd.to_datetime(result[time_column], errors="coerce")

    if result[time_column].isna().any():
        raise ValueError(f"Column '{time_column}' contains invalid datetime values.")

    result["hour"] = result[time_column].dt.hour
    result[output_column] = result["hour"].map(hour_label_map)

    if result[output_column].isna().any():
        raise ValueError("Some rows failed to map to a tariff label.")

    return result


def assign_prices_from_label_map(
    df: pd.DataFrame,
    price_dict: Dict[str, Optional[float]],
    tariff_period_column: str = "tariff_period",
    output_column: str = "price",
) -> pd.DataFrame:
    """
    Assign price according to tariff label.
    """
    if tariff_period_column not in df.columns:
        raise ValueError(f"Column '{tariff_period_column}' not found in dataframe.")

    validate_tariff_price_dict(price_dict, allow_empty=True)

    result = df.copy()
    result[output_column] = result[tariff_period_column].map(price_dict)

    if result[output_column].isna().any():
        missing_labels = (
            result.loc[result[output_column].isna(), tariff_period_column]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
        raise ValueError(
            f"Some tariff labels do not have prices assigned: {missing_labels}"
        )

    return result


# ============================================================
# Manual five-level TOU tariff pipeline
# ============================================================

def apply_manual_five_level_tariff(
    df: pd.DataFrame,
    critical_peak_hours: list[int],
    peak_hours: list[int],
    flat_hours: list[int],
    valley_hours: list[int],
    super_valley_hours: list[int],
    critical_peak_price: Optional[float] = None,
    peak_price: Optional[float] = None,
    flat_price: Optional[float] = None,
    valley_price: Optional[float] = None,
    super_valley_price: Optional[float] = None,
    time_column: str = "time",
) -> pd.DataFrame:
    """
    Full manual tariff assignment pipeline for five-level TOU tariff.
    """
    hour_label_map = build_five_level_hour_label_map(
        critical_peak_hours=critical_peak_hours,
        peak_hours=peak_hours,
        flat_hours=flat_hours,
        valley_hours=valley_hours,
        super_valley_hours=super_valley_hours,
    )

    price_dict = build_price_dict(
        critical_peak_price=critical_peak_price,
        peak_price=peak_price,
        flat_price=flat_price,
        valley_price=valley_price,
        super_valley_price=super_valley_price,
    )

    validate_hour_label_map_has_prices(hour_label_map, price_dict)

    result = assign_tariff_labels_from_hour_map(
        df=df,
        hour_label_map=hour_label_map,
        time_column=time_column,
        output_column="tariff_period",
    )

    result = assign_prices_from_label_map(
        df=result,
        price_dict=price_dict,
        tariff_period_column="tariff_period",
        output_column="price",
    )

    result = calculate_energy_cost(
        df=result,
        load_column="load_kwh",
        price_column="price",
        output_column="energy_cost",
    )

    return result


# ============================================================
# Monthly tariff table support
# ============================================================

def validate_monthly_hour_price_table(price_table_df: pd.DataFrame) -> None:
    """
    Validate monthly 12x24 tariff price table.

    Expected format:
    - 12 rows, one for each month
    - one column named 'month'
    - 24 hourly columns named: h00, h01, ..., h23
    """
    required_columns = ["month"] + [f"h{i:02d}" for i in range(24)]
    missing_columns = [col for col in required_columns if col not in price_table_df.columns]

    if missing_columns:
        raise ValueError(
            f"Monthly tariff table is missing required columns: {missing_columns}"
        )

    if price_table_df.empty:
        raise ValueError("Monthly tariff table is empty.")

    month_values = sorted(price_table_df["month"].astype(int).tolist())
    if month_values != list(range(1, 13)):
        raise ValueError("Monthly tariff table must contain month values 1~12 exactly once.")

    for col in [f"h{i:02d}" for i in range(24)]:
        if price_table_df[col].isna().any():
            raise ValueError(f"Column '{col}' in monthly tariff table contains missing values.")


def apply_monthly_hour_price_table(
    df: pd.DataFrame,
    price_table_df: pd.DataFrame,
    time_column: str = "time",
    output_price_column: str = "price",
    output_label_column: str = "tariff_period",
) -> pd.DataFrame:
    """
    Assign price to each row using a monthly 12x24 tariff table.
    """
    if time_column not in df.columns:
        raise ValueError(f"Column '{time_column}' not found in dataframe.")

    validate_monthly_hour_price_table(price_table_df)

    result = df.copy()
    result[time_column] = pd.to_datetime(result[time_column], errors="coerce")

    if result[time_column].isna().any():
        raise ValueError(f"Column '{time_column}' contains invalid datetime values.")

    result["month"] = result[time_column].dt.month
    result["hour"] = result[time_column].dt.hour

    tariff_lookup = price_table_df.set_index("month")

    assigned_prices = []
    assigned_labels = []

    for _, row in result.iterrows():
        month = int(row["month"])
        hour = int(row["hour"])
        price_col = f"h{hour:02d}"

        price = float(tariff_lookup.loc[month, price_col])
        assigned_prices.append(price)

        # For monthly 12x24 table mode, use generic period label.
        assigned_labels.append(f"month_{month}_hour_{hour:02d}")

    result[output_price_column] = assigned_prices
    result[output_label_column] = assigned_labels

    result = calculate_energy_cost(
        df=result,
        load_column="load_kwh",
        price_column=output_price_column,
        output_column="energy_cost",
    )

    return result


# ============================================================
# Electricity cost calculation
# ============================================================

def calculate_energy_cost(
    df: pd.DataFrame,
    load_column: str = "load_kwh",
    price_column: str = "price",
    output_column: str = "energy_cost",
) -> pd.DataFrame:
    """
    Calculate electricity cost for each row.

    Formula:
    energy_cost = load * price
    """
    required_columns = [load_column, price_column]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns for cost calculation: {missing_columns}")

    result = df.copy()
    result[output_column] = result[load_column] * result[price_column]
    return result


def calculate_total_energy_cost(
    df: pd.DataFrame,
    cost_column: str = "energy_cost",
) -> float:
    """
    Calculate total electricity cost.
    """
    if cost_column not in df.columns:
        raise ValueError(f"Column '{cost_column}' not found in dataframe.")

    return float(df[cost_column].sum())


def calculate_weighted_average_price(
    df: pd.DataFrame,
    load_column: str = "load_kwh",
    price_column: str = "price",
) -> float:
    """
    Calculate weighted average electricity price.
    """
    required_columns = [load_column, price_column]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    total_load = df[load_column].sum()
    if total_load <= 0:
        raise ValueError("Total load must be greater than 0.")

    weighted_avg_price = (df[load_column] * df[price_column]).sum() / total_load
    return float(weighted_avg_price)


# ============================================================
# Tariff breakdown
# ============================================================

def calculate_tariff_breakdown(
    df: pd.DataFrame,
    tariff_period_column: str = "tariff_period",
    load_column: str = "load_kwh",
    price_column: str = "price",
    cost_column: str = "energy_cost",
) -> pd.DataFrame:
    """
    Calculate load/cost breakdown by tariff period.
    """
    required_columns = [tariff_period_column, load_column, price_column, cost_column]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    summary = (
        df.groupby(tariff_period_column, as_index=False)
        .agg(
            total_load_kwh=(load_column, "sum"),
            avg_price=(price_column, "mean"),
            total_cost=(cost_column, "sum"),
        )
    )

    total_load = summary["total_load_kwh"].sum()
    total_cost = summary["total_cost"].sum()

    summary["load_share_pct"] = (
        summary["total_load_kwh"] / total_load * 100 if total_load > 0 else 0.0
    )
    summary["cost_share_pct"] = (
        summary["total_cost"] / total_cost * 100 if total_cost > 0 else 0.0
    )

    return summary.reset_index(drop=True)


def calculate_five_level_tariff_breakdown(
    df: pd.DataFrame,
    tariff_period_column: str = "tariff_period",
    load_column: str = "load_kwh",
    price_column: str = "price",
    cost_column: str = "energy_cost",
) -> pd.DataFrame:
    """
    Calculate tariff breakdown and sort by the preferred five-level order.
    """
    summary = calculate_tariff_breakdown(
        df=df,
        tariff_period_column=tariff_period_column,
        load_column=load_column,
        price_column=price_column,
        cost_column=cost_column,
    )

    tariff_order = {
        "critical_peak": 0,
        "peak": 1,
        "flat": 2,
        "valley": 3,
        "super_valley": 4,
    }

    summary["sort_key"] = summary[tariff_period_column].map(tariff_order).fillna(999)
    summary = summary.sort_values("sort_key").drop(columns=["sort_key"]).reset_index(drop=True)

    return summary


# ============================================================
# Annual cost estimation from sample load
# ============================================================

def estimate_annual_energy_cost_from_sample(
    load_df: pd.DataFrame,
    monthly_price_table_df: pd.DataFrame,
    time_column: str = "time",
    load_column: str = "load_kwh",
) -> Dict[str, object]:
    """
    Estimate annual energy cost by assuming the uploaded sample load pattern
    repeats through future months, while each month uses its own 24-hour tariff.

    Method
    ------
    1. Group sample load by hour and compute average load per hour.
    2. For each month, apply the 24-hour tariff to the average hourly load.
    3. Multiply by number of days in that month.
    """
    if time_column not in load_df.columns or load_column not in load_df.columns:
        raise ValueError(f"Load dataframe must contain '{time_column}' and '{load_column}'.")

    validate_monthly_hour_price_table(monthly_price_table_df)

    result = load_df.copy()
    result[time_column] = pd.to_datetime(result[time_column], errors="coerce")

    if result[time_column].isna().any():
        raise ValueError(f"Column '{time_column}' contains invalid datetime values.")

    result["hour"] = result[time_column].dt.hour

    avg_hourly_load = (
        result.groupby("hour", as_index=False)
        .agg(avg_load_kwh=(load_column, "mean"))
        .sort_values("hour")
        .reset_index(drop=True)
    )

    if sorted(avg_hourly_load["hour"].tolist()) != list(range(24)):
        raise ValueError(
            "Sample load must contain all 24 hours in order to estimate annual energy cost."
        )

    monthly_records = []

    for _, month_row in monthly_price_table_df.sort_values("month").iterrows():
        month = int(month_row["month"])
        days_in_month = pd.Timestamp(year=2025, month=month, day=1).days_in_month

        daily_cost = 0.0
        daily_load = 0.0

        for hour in range(24):
            avg_load = float(avg_hourly_load.loc[avg_hourly_load["hour"] == hour, "avg_load_kwh"].iloc[0])
            price = float(month_row[f"h{hour:02d}"])

            daily_load += avg_load
            daily_cost += avg_load * price

        monthly_load = daily_load * days_in_month
        monthly_cost = daily_cost * days_in_month

        monthly_records.append(
            {
                "month": month,
                "days_in_month": days_in_month,
                "estimated_monthly_load_kwh": monthly_load,
                "estimated_monthly_energy_cost": monthly_cost,
            }
        )

    monthly_summary_df = pd.DataFrame(monthly_records)
    annual_total_energy_cost = float(monthly_summary_df["estimated_monthly_energy_cost"].sum())
    annual_total_load_kwh = float(monthly_summary_df["estimated_monthly_load_kwh"].sum())
    weighted_average_price = (
        annual_total_energy_cost / annual_total_load_kwh if annual_total_load_kwh > 0 else 0.0
    )

    return {
        "monthly_summary_df": monthly_summary_df,
        "annual_total_energy_cost": annual_total_energy_cost,
        "annual_total_load_kwh": annual_total_load_kwh,
        "weighted_average_price": float(weighted_average_price),
        "avg_hourly_load_df": avg_hourly_load,
    }


# ============================================================
# Compact summary helper
# ============================================================

def summarize_tariff_results(
    df: pd.DataFrame,
    load_column: str = "load_kwh",
    price_column: str = "price",
    cost_column: str = "energy_cost",
    tariff_period_column: str = "tariff_period",
) -> Dict[str, object]:
    """
    Return a compact tariff summary dictionary for UI display.
    """
    total_energy_cost = calculate_total_energy_cost(df, cost_column=cost_column)
    weighted_average_price = calculate_weighted_average_price(
        df,
        load_column=load_column,
        price_column=price_column,
    )

    tariff_breakdown = calculate_tariff_breakdown(
        df,
        tariff_period_column=tariff_period_column,
        load_column=load_column,
        price_column=price_column,
        cost_column=cost_column,
    )

    return {
        "total_energy_cost": total_energy_cost,
        "weighted_average_price": weighted_average_price,
        "tariff_breakdown": tariff_breakdown,
    }