from __future__ import annotations

from typing import Dict, Iterable, List, Optional

import pandas as pd


# ============================================================
# DataFrame validation
# ============================================================

def validate_input_dataframe(df: pd.DataFrame) -> None:
    """
    Validate the input load dataframe for MVP / demo usage.

    Required columns:
    - time
    - load_kwh
    """
    required_columns = ["time", "load_kwh"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(
            f"Input dataframe is missing required columns: {missing_columns}"
        )

    if df.empty:
        raise ValueError("Input dataframe is empty.")

    if df["time"].isna().any():
        raise ValueError("Column 'time' contains missing values.")

    if df["load_kwh"].isna().any():
        raise ValueError("Column 'load_kwh' contains missing values.")

    if (df["load_kwh"] < 0).any():
        raise ValueError("Column 'load_kwh' contains negative values.")

    if df["time"].duplicated().any():
        raise ValueError("Column 'time' contains duplicate timestamps.")


def validate_hourly_dataframe(df: pd.DataFrame) -> None:
    """
    Validate whether the dataframe is a continuous hourly time series.
    """
    if df.empty:
        raise ValueError("Cannot validate hourly continuity on an empty dataframe.")

    sorted_df = df.sort_values("time").reset_index(drop=True)
    expected_time = pd.date_range(
        start=sorted_df["time"].min(),
        end=sorted_df["time"].max(),
        freq="h",
    )

    actual_time = pd.DatetimeIndex(sorted_df["time"])
    missing_time = expected_time.difference(actual_time)

    if len(missing_time) > 0:
        raise ValueError(
            f"Hourly continuity check failed. Missing timestamps example: {list(missing_time[:5])}"
        )


# ============================================================
# Flexible tariff validation
# ============================================================

def validate_tariff_price_dict(
    price_dict: Dict[str, Optional[float]],
    allow_empty: bool = True,
) -> None:
    """
    Validate tariff price dictionary.

    Supported tariff labels:
    - critical_peak
    - peak
    - flat
    - valley
    - super_valley

    Notes
    -----
    When allow_empty=True, price can be None for unused periods.
    """
    supported_labels = {
        "critical_peak",
        "peak",
        "flat",
        "valley",
        "super_valley",
    }

    unknown_labels = set(price_dict.keys()) - supported_labels
    if unknown_labels:
        raise ValueError(f"Unknown tariff labels found: {sorted(unknown_labels)}")

    for label, value in price_dict.items():
        if value is None:
            if not allow_empty:
                raise ValueError(f"Tariff price for '{label}' cannot be empty.")
            continue

        _validate_non_negative_number(value, f"{label}_price")


def validate_hour_label_map(
    hour_label_map: Dict[int, str],
) -> None:
    """
    Validate hour -> tariff label mapping.

    Requirements:
    - exactly 24 hours
    - every hour 0~23 must exist
    - each hour must map to a supported tariff label
    """
    supported_labels = {
        "critical_peak",
        "peak",
        "flat",
        "valley",
        "super_valley",
    }

    if len(hour_label_map) != 24:
        raise ValueError("Tariff hour mapping must contain exactly 24 entries.")

    expected_hours = set(range(24))
    actual_hours = set(hour_label_map.keys())

    if expected_hours != actual_hours:
        missing_hours = sorted(list(expected_hours - actual_hours))
        extra_hours = sorted(list(actual_hours - expected_hours))
        raise ValueError(
            f"Tariff hour mapping must cover 0~23 exactly. "
            f"Missing hours: {missing_hours}, extra hours: {extra_hours}"
        )

    invalid_labels = sorted(
        {label for label in hour_label_map.values() if label not in supported_labels}
    )
    if invalid_labels:
        raise ValueError(f"Invalid tariff labels found: {invalid_labels}")


def validate_hour_label_groups(
    critical_peak_hours: Iterable[int],
    peak_hours: Iterable[int],
    flat_hours: Iterable[int],
    valley_hours: Iterable[int],
    super_valley_hours: Iterable[int],
    allow_empty_groups: bool = True,
) -> None:
    """
    Validate grouped tariff-hour definitions.

    Notes
    -----
    Empty groups are allowed when allow_empty_groups=True.
    """
    grouped = {
        "critical_peak_hours": list(critical_peak_hours),
        "peak_hours": list(peak_hours),
        "flat_hours": list(flat_hours),
        "valley_hours": list(valley_hours),
        "super_valley_hours": list(super_valley_hours),
    }

    all_hours: List[int] = []

    for name, hours in grouped.items():
        if len(hours) == 0 and not allow_empty_groups:
            raise ValueError(f"{name} cannot be empty.")

        _validate_hour_list(hours, name, allow_empty=allow_empty_groups)
        all_hours.extend(hours)

    if len(all_hours) != 24:
        raise ValueError(
            "Tariff period definitions must cover exactly 24 hourly entries in total."
        )

    if len(set(all_hours)) != 24:
        raise ValueError(
            "Tariff period definitions contain duplicate hours or missing hours."
        )


def validate_hour_label_map_has_prices(
    hour_label_map: Dict[int, str],
    price_dict: Dict[str, Optional[float]],
) -> None:
    """
    Ensure every used tariff label has a valid price.
    """
    validate_hour_label_map(hour_label_map)
    validate_tariff_price_dict(price_dict, allow_empty=True)

    used_labels = set(hour_label_map.values())

    missing_price_labels = [
        label for label in sorted(used_labels) if price_dict.get(label) is None
    ]
    if missing_price_labels:
        raise ValueError(
            f"Used tariff labels are missing prices: {missing_price_labels}"
        )


# ============================================================
# Legacy TOU tariff validation
# ============================================================

def validate_tariff_prices(
    peak_price: float,
    flat_price: float,
    valley_price: float,
) -> None:
    """
    Legacy 3-level TOU tariff validation.
    """
    price_map = {
        "peak_price": peak_price,
        "flat_price": flat_price,
        "valley_price": valley_price,
    }

    for name, value in price_map.items():
        _validate_non_negative_number(value, name)

    if valley_price > flat_price:
        raise ValueError(
            "Valley price should usually be lower than or equal to flat price."
        )

    if flat_price > peak_price:
        raise ValueError(
            "Flat price should usually be lower than or equal to peak price."
        )


def validate_time_periods(
    peak_hours: Iterable[int],
    flat_hours: Iterable[int],
    valley_hours: Iterable[int],
) -> None:
    """
    Legacy 3-level TOU hour validation.
    """
    peak_hours = list(peak_hours)
    flat_hours = list(flat_hours)
    valley_hours = list(valley_hours)

    _validate_hour_list(peak_hours, "peak_hours", allow_empty=False)
    _validate_hour_list(flat_hours, "flat_hours", allow_empty=False)
    _validate_hour_list(valley_hours, "valley_hours", allow_empty=False)

    all_hours = peak_hours + flat_hours + valley_hours

    if len(all_hours) != 24:
        raise ValueError(
            "Tariff periods must cover exactly 24 hourly entries in total."
        )

    if len(set(all_hours)) != 24:
        raise ValueError(
            "Tariff period definitions contain duplicate hours or missing hours."
        )


# ============================================================
# Storage parameter validation
# ============================================================

def validate_storage_params(
    storage_capacity_kwh: float,
    storage_power_kw: float,
    charge_efficiency: float,
    discharge_efficiency: float,
    initial_soc_ratio: float = 1.0,
    min_soc_ratio: float = 0.0,
    max_soc_ratio: float = 1.0,
) -> None:
    """
    Validate energy storage system parameters.
    """
    _validate_positive_number(storage_capacity_kwh, "storage_capacity_kwh")
    _validate_positive_number(storage_power_kw, "storage_power_kw")

    _validate_ratio(charge_efficiency, "charge_efficiency")
    _validate_ratio(discharge_efficiency, "discharge_efficiency")
    _validate_ratio(initial_soc_ratio, "initial_soc_ratio")
    _validate_ratio(min_soc_ratio, "min_soc_ratio")
    _validate_ratio(max_soc_ratio, "max_soc_ratio")

    if min_soc_ratio > max_soc_ratio:
        raise ValueError("min_soc_ratio cannot be greater than max_soc_ratio.")

    if not (min_soc_ratio <= initial_soc_ratio <= max_soc_ratio):
        raise ValueError(
            "initial_soc_ratio must be between min_soc_ratio and max_soc_ratio."
        )


# ============================================================
# Financial parameter validation
# ============================================================

def validate_financial_params(
    capex_total: float,
    annual_om_cost: float,
    project_years: Optional[int] = None,
    discount_rate: Optional[float] = None,
    annual_degradation_rate: Optional[float] = None,
) -> None:
    """
    Validate finance-related input parameters.
    """
    _validate_non_negative_number(capex_total, "capex_total")
    _validate_non_negative_number(annual_om_cost, "annual_om_cost")

    if project_years is not None:
        if not isinstance(project_years, int) or project_years <= 0:
            raise ValueError("project_years must be a positive integer.")

    if discount_rate is not None:
        if discount_rate < 0:
            raise ValueError("discount_rate cannot be negative.")

    if annual_degradation_rate is not None:
        _validate_ratio(annual_degradation_rate, "annual_degradation_rate")


# ============================================================
# Dispatch / flexible load validation
# ============================================================

def validate_dispatch_params(
    adjustable_load_ratio: float,
    labor_cost_per_day: float = 0.0,
) -> None:
    """
    Validate dispatch optimization input parameters.
    """
    _validate_ratio(adjustable_load_ratio, "adjustable_load_ratio")
    _validate_non_negative_number(labor_cost_per_day, "labor_cost_per_day")


# ============================================================
# Power charge validation
# ============================================================

def validate_capacity_charge_params(
    capacity_price_per_kw: float,
    contract_buffer_ratio: float,
) -> None:
    """
    Validate capacity-based power charge parameters.
    """
    _validate_non_negative_number(capacity_price_per_kw, "capacity_price_per_kw")
    _validate_non_negative_number(contract_buffer_ratio, "contract_buffer_ratio")


def validate_demand_charge_params(
    demand_price_per_kw: float,
) -> None:
    """
    Validate demand-based power charge parameters.
    """
    _validate_non_negative_number(demand_price_per_kw, "demand_price_per_kw")


# ============================================================
# Generic config dictionary validation
# ============================================================

def validate_required_keys(
    config: Dict,
    required_keys: List[str],
    config_name: str,
) -> None:
    """
    Validate whether a config dictionary contains all required keys.
    """
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ValueError(
            f"{config_name} is missing required keys: {missing_keys}"
        )


# ============================================================
# Low-level helper validators
# ============================================================

def _validate_positive_number(value: float, name: str) -> None:
    if not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number.")
    if value <= 0:
        raise ValueError(f"{name} must be greater than 0.")


def _validate_non_negative_number(value: float, name: str) -> None:
    if not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number.")
    if value < 0:
        raise ValueError(f"{name} cannot be negative.")


def _validate_ratio(value: float, name: str) -> None:
    if not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number.")
    if value < 0 or value > 1:
        raise ValueError(f"{name} must be between 0 and 1.")


def _validate_hour_list(
    hours: List[int],
    name: str,
    allow_empty: bool = False,
) -> None:
    if len(hours) == 0 and not allow_empty:
        raise ValueError(f"{name} cannot be empty.")

    for hour in hours:
        if not isinstance(hour, int):
            raise ValueError(f"All values in {name} must be integers.")
        if hour < 0 or hour > 23:
            raise ValueError(f"All values in {name} must be between 0 and 23.")