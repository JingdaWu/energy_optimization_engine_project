from __future__ import annotations

from pathlib import Path
from typing import BinaryIO, Union

import pandas as pd


DataSource = Union[str, Path, BinaryIO]


REQUIRED_COLUMNS = ["time", "load_kwh"]


# ============================================================
# Generic energy load data loading
# ============================================================

def load_energy_data(source: DataSource) -> pd.DataFrame:
    """
    Load energy data from a CSV file path or Streamlit uploaded file.

    Required columns:
    - time
    - load_kwh

    Optional columns:
    - tariff_period
    - price

    Returns
    -------
    pd.DataFrame
        Standardized dataframe sorted by time.
    """
    df = pd.read_csv(source)
    df.columns = [str(col).strip().lower() for col in df.columns]

    _check_required_columns(df)
    df = _standardize_time_column(df)
    df = _standardize_load_column(df)
    df = _keep_supported_columns(df)
    df = df.sort_values("time").reset_index(drop=True)

    return df


def load_sample_data(sample_path: Union[str, Path] = "data/sample_load.csv") -> pd.DataFrame:
    """
    Load built-in sample CSV data.
    """
    sample_path = Path(sample_path)
    if not sample_path.exists():
        raise FileNotFoundError(
            f"Sample data file not found: {sample_path}. "
            "Please create data/sample_load.csv first."
        )

    return load_energy_data(sample_path)


# ============================================================
# Monthly tariff table loading
# ============================================================

def load_monthly_tariff_table(source: DataSource) -> pd.DataFrame:
    """
    Load 12x24 monthly tariff table.

    Expected columns:
    - month
    - h00 ... h23
    """
    df = pd.read_csv(source)
    df.columns = [str(col).strip().lower() for col in df.columns]

    required_columns = ["month"] + [f"h{i:02d}" for i in range(24)]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(
            f"Monthly tariff table is missing required columns: {missing_columns}"
        )

    df["month"] = pd.to_numeric(df["month"], errors="coerce")

    if df["month"].isna().any():
        raise ValueError("Column 'month' contains invalid values.")

    df["month"] = df["month"].astype(int)

    for col in [f"h{i:02d}" for i in range(24)]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        if df[col].isna().any():
            raise ValueError(f"Column '{col}' contains invalid numeric values.")

        if (df[col] < 0).any():
            raise ValueError(f"Column '{col}' contains negative values.")

    df = df.sort_values("month").reset_index(drop=True)
    return df


def load_monthly_tariff_template(
    sample_path: Union[str, Path] = "data/monthly_tariff_template.csv",
) -> pd.DataFrame:
    """
    Load built-in monthly tariff template file.
    """
    sample_path = Path(sample_path)
    if not sample_path.exists():
        raise FileNotFoundError(
            f"Monthly tariff template file not found: {sample_path}."
        )

    return load_monthly_tariff_table(sample_path)


# ============================================================
# Storage parameter CSV loading
# ============================================================

def load_storage_parameter_csv(source: DataSource) -> dict:
    """
    Load storage parameter CSV and return the first-row parameter dict.

    Expected columns:
    - storage_capacity_kwh
    - storage_power_kw
    - charge_efficiency
    - discharge_efficiency
    - min_soc_ratio
    - max_soc_ratio
    - capex_total
    - annual_om_cost
    - project_years
    - discount_rate
    - annual_degradation_rate
    """
    df = pd.read_csv(source)
    df.columns = [str(col).strip().lower() for col in df.columns]

    required_columns = [
        "storage_capacity_kwh",
        "storage_power_kw",
        "charge_efficiency",
        "discharge_efficiency",
        "min_soc_ratio",
        "max_soc_ratio",
        "capex_total",
        "annual_om_cost",
        "project_years",
        "discount_rate",
        "annual_degradation_rate",
    ]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(
            f"Storage parameter CSV is missing required columns: {missing_columns}"
        )

    if df.empty:
        raise ValueError("Storage parameter CSV is empty.")

    row = df.iloc[0].copy()

    numeric_columns = [
        "storage_capacity_kwh",
        "storage_power_kw",
        "charge_efficiency",
        "discharge_efficiency",
        "min_soc_ratio",
        "max_soc_ratio",
        "capex_total",
        "annual_om_cost",
        "project_years",
        "discount_rate",
        "annual_degradation_rate",
    ]

    for col in numeric_columns:
        row[col] = pd.to_numeric(row[col], errors="coerce")
        if pd.isna(row[col]):
            raise ValueError(f"Column '{col}' contains invalid numeric value.")

    return {
        "storage_capacity_kwh": float(row["storage_capacity_kwh"]),
        "storage_power_kw": float(row["storage_power_kw"]),
        "charge_efficiency": float(row["charge_efficiency"]),
        "discharge_efficiency": float(row["discharge_efficiency"]),
        "min_soc_ratio": float(row["min_soc_ratio"]),
        "max_soc_ratio": float(row["max_soc_ratio"]),
        "capex_total": float(row["capex_total"]),
        "annual_om_cost": float(row["annual_om_cost"]),
        "project_years": int(row["project_years"]),
        "discount_rate": float(row["discount_rate"]),
        "annual_degradation_rate": float(row["annual_degradation_rate"]),
    }


def load_storage_sample_parameters(
    sample_path: Union[str, Path],
) -> dict:
    """
    Load built-in storage sample parameter CSV.
    """
    sample_path = Path(sample_path)
    if not sample_path.exists():
        raise FileNotFoundError(f"Storage sample file not found: {sample_path}")

    return load_storage_parameter_csv(sample_path)


# ============================================================
# Time helpers
# ============================================================

def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add common time-based helper columns for downstream logic.
    """
    df = df.copy()
    df["date"] = df["time"].dt.date
    df["hour"] = df["time"].dt.hour
    df["month"] = df["time"].dt.month
    df["day_of_week"] = df["time"].dt.dayofweek
    return df


def ensure_hourly_continuity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure the time series is continuous with 1-hour frequency.
    """
    df = df.copy().sort_values("time").reset_index(drop=True)

    expected_time = pd.date_range(
        start=df["time"].min(),
        end=df["time"].max(),
        freq="h",
    )

    actual_time = pd.DatetimeIndex(df["time"])
    missing = expected_time.difference(actual_time)

    if len(missing) > 0:
        raise ValueError(
            f"Time series is not continuous hourly data. "
            f"Missing timestamps example: {list(missing[:5])}"
        )

    if actual_time.duplicated().any():
        dupes = df.loc[actual_time.duplicated(), "time"].tolist()
        raise ValueError(
            f"Duplicate timestamps found in 'time' column. Example: {dupes[:5]}"
        )

    return df


# ============================================================
# Summary helpers
# ============================================================

def summarize_input_data(df: pd.DataFrame) -> dict:
    """
    Return quick summary info for UI display or debugging.
    """
    summary = {
        "rows": int(len(df)),
        "start_time": df["time"].min(),
        "end_time": df["time"].max(),
        "has_tariff_period": "tariff_period" in df.columns,
        "has_price": "price" in df.columns,
        "min_load_kwh": float(df["load_kwh"].min()),
        "max_load_kwh": float(df["load_kwh"].max()),
        "avg_load_kwh": float(df["load_kwh"].mean()),
    }
    return summary


# ============================================================
# Internal low-level helpers
# ============================================================

def _check_required_columns(df: pd.DataFrame) -> None:
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required columns: {missing}. "
            f"CSV must contain: {REQUIRED_COLUMNS}"
        )


def _standardize_time_column(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"], errors="coerce")

    if df["time"].isna().any():
        bad_rows = df[df["time"].isna()].index.tolist()
        raise ValueError(
            f"Failed to parse 'time' column as datetime. Bad row indexes: {bad_rows[:10]}"
        )

    return df


def _standardize_load_column(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["load_kwh"] = pd.to_numeric(df["load_kwh"], errors="coerce")

    if df["load_kwh"].isna().any():
        bad_rows = df[df["load_kwh"].isna()].index.tolist()
        raise ValueError(
            f"Column 'load_kwh' contains invalid numeric values. "
            f"Bad row indexes: {bad_rows[:10]}"
        )

    if (df["load_kwh"] < 0).any():
        bad_rows = df[df["load_kwh"] < 0].index.tolist()
        raise ValueError(
            f"Column 'load_kwh' contains negative values, which are not allowed. "
            f"Bad row indexes: {bad_rows[:10]}"
        )

    return df


def _keep_supported_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only columns currently supported by the app.
    """
    supported = ["time", "load_kwh", "tariff_period", "price"]
    existing = [col for col in supported if col in df.columns]
    return df[existing].copy()