from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd

from utils.validators import validate_storage_params


# ============================================================
# Storage state helpers
# ============================================================

def calculate_usable_soc_bounds(
    storage_capacity_kwh: float,
    min_soc_ratio: float,
    max_soc_ratio: float,
) -> Dict[str, float]:
    """
    Calculate usable SOC bounds in kWh.
    """
    if min_soc_ratio > max_soc_ratio:
        raise ValueError("min_soc_ratio cannot be greater than max_soc_ratio.")

    min_soc_kwh = storage_capacity_kwh * min_soc_ratio
    max_soc_kwh = storage_capacity_kwh * max_soc_ratio

    return {
        "min_soc_kwh": float(min_soc_kwh),
        "max_soc_kwh": float(max_soc_kwh),
    }


# ============================================================
# Charging and discharging logic for one timestep
# ============================================================

def _calculate_max_charge_from_grid(
    soc_kwh: float,
    max_soc_kwh: float,
    storage_power_kw: float,
    charge_efficiency: float,
    timestep_hours: float,
) -> float:
    """
    Calculate maximum charge energy drawn from grid in current timestep.
    """
    remaining_storage_space = max_soc_kwh - soc_kwh

    if remaining_storage_space <= 0:
        return 0.0

    max_grid_charge_by_capacity = remaining_storage_space / charge_efficiency
    max_grid_charge_by_power = storage_power_kw * timestep_hours

    return float(max(0.0, min(max_grid_charge_by_capacity, max_grid_charge_by_power)))


def _calculate_max_discharge_to_load(
    soc_kwh: float,
    min_soc_kwh: float,
    storage_power_kw: float,
    discharge_efficiency: float,
    timestep_hours: float,
    current_load_kwh: float,
) -> float:
    """
    Calculate maximum discharge energy delivered to load in current timestep.
    """
    available_storage_energy = soc_kwh - min_soc_kwh

    if available_storage_energy <= 0:
        return 0.0

    max_load_supply_by_soc = available_storage_energy * discharge_efficiency
    max_load_supply_by_power = storage_power_kw * timestep_hours

    return float(max(0.0, min(max_load_supply_by_soc, max_load_supply_by_power, current_load_kwh)))


# ============================================================
# Rule-based storage simulation
# ============================================================

def simulate_storage_operation(
    df: pd.DataFrame,
    storage_capacity_kwh: float,
    storage_power_kw: float,
    charge_efficiency: float,
    discharge_efficiency: float,
    initial_soc_ratio: float = 0.0,
    min_soc_ratio: float = 0.0,
    max_soc_ratio: float = 1.0,
    charge_periods: Optional[List[str]] = None,
    discharge_periods: Optional[List[str]] = None,
    time_column: str = "time",
    load_column: str = "load_kwh",
    tariff_period_column: str = "tariff_period",
    price_column: str = "price",
    timestep_hours: float = 1.0,
) -> pd.DataFrame:
    """
    Simulate rule-based storage operation for MVP.

    Default strategy:
    - charge during valley periods
    - discharge during peak periods

    Output columns:
    - storage_charge_kwh_grid
    - storage_charge_kwh_soc
    - storage_discharge_kwh_load
    - storage_discharge_kwh_soc
    - soc_kwh
    - net_load_kwh
    - storage_action
    """
    validate_storage_params(
        storage_capacity_kwh=storage_capacity_kwh,
        storage_power_kw=storage_power_kw,
        charge_efficiency=charge_efficiency,
        discharge_efficiency=discharge_efficiency,
        initial_soc_ratio=initial_soc_ratio,
        min_soc_ratio=min_soc_ratio,
        max_soc_ratio=max_soc_ratio,
    )

    required_columns = [time_column, load_column, tariff_period_column]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns for storage simulation: {missing_columns}")

    if charge_periods is None:
        charge_periods = ["valley"]

    if discharge_periods is None:
        discharge_periods = ["peak"]

    result = df.copy().sort_values(time_column).reset_index(drop=True)

    soc_bounds = calculate_usable_soc_bounds(
        storage_capacity_kwh=storage_capacity_kwh,
        min_soc_ratio=min_soc_ratio,
        max_soc_ratio=max_soc_ratio,
    )

    min_soc_kwh = soc_bounds["min_soc_kwh"]
    max_soc_kwh = soc_bounds["max_soc_kwh"]
    soc_kwh = storage_capacity_kwh * initial_soc_ratio

    storage_charge_kwh_grid_list = []
    storage_charge_kwh_soc_list = []
    storage_discharge_kwh_load_list = []
    storage_discharge_kwh_soc_list = []
    soc_kwh_list = []
    net_load_kwh_list = []
    storage_action_list = []

    for _, row in result.iterrows():
        current_load = float(row[load_column])
        current_period = str(row[tariff_period_column]).lower()

        charge_from_grid = 0.0
        charge_into_soc = 0.0
        discharge_to_load = 0.0
        discharge_from_soc = 0.0
        action = "idle"

        # Charge during low-price periods
        if current_period in charge_periods:
            charge_from_grid = _calculate_max_charge_from_grid(
                soc_kwh=soc_kwh,
                max_soc_kwh=max_soc_kwh,
                storage_power_kw=storage_power_kw,
                charge_efficiency=charge_efficiency,
                timestep_hours=timestep_hours,
            )
            charge_into_soc = charge_from_grid * charge_efficiency
            soc_kwh += charge_into_soc
            action = "charge" if charge_from_grid > 0 else "idle"

        # Discharge during high-price periods
        elif current_period in discharge_periods:
            discharge_to_load = _calculate_max_discharge_to_load(
                soc_kwh=soc_kwh,
                min_soc_kwh=min_soc_kwh,
                storage_power_kw=storage_power_kw,
                discharge_efficiency=discharge_efficiency,
                timestep_hours=timestep_hours,
                current_load_kwh=current_load,
            )
            discharge_from_soc = discharge_to_load / discharge_efficiency if discharge_efficiency > 0 else 0.0
            soc_kwh -= discharge_from_soc
            action = "discharge" if discharge_to_load > 0 else "idle"

        # Keep SOC within bounds
        soc_kwh = min(max(soc_kwh, min_soc_kwh), max_soc_kwh)

        # Net load seen by the grid
        net_load_kwh = current_load + charge_from_grid - discharge_to_load

        storage_charge_kwh_grid_list.append(float(charge_from_grid))
        storage_charge_kwh_soc_list.append(float(charge_into_soc))
        storage_discharge_kwh_load_list.append(float(discharge_to_load))
        storage_discharge_kwh_soc_list.append(float(discharge_from_soc))
        soc_kwh_list.append(float(soc_kwh))
        net_load_kwh_list.append(float(net_load_kwh))
        storage_action_list.append(action)

    result["storage_charge_kwh_grid"] = storage_charge_kwh_grid_list
    result["storage_charge_kwh_soc"] = storage_charge_kwh_soc_list
    result["storage_discharge_kwh_load"] = storage_discharge_kwh_load_list
    result["storage_discharge_kwh_soc"] = storage_discharge_kwh_soc_list
    result["soc_kwh"] = soc_kwh_list
    result["net_load_kwh"] = net_load_kwh_list
    result["storage_action"] = storage_action_list

    if price_column in result.columns:
        result["original_energy_cost"] = result[load_column] * result[price_column]
        result["optimized_energy_cost"] = result["net_load_kwh"] * result[price_column]
        result["storage_cost_saving"] = (
            result["original_energy_cost"] - result["optimized_energy_cost"]
        )

    return result


# ============================================================
# Storage performance metrics
# ============================================================

def calculate_storage_throughput_metrics(
    df: pd.DataFrame,
    storage_capacity_kwh: float,
    charge_column: str = "storage_charge_kwh_grid",
    discharge_column: str = "storage_discharge_kwh_load",
) -> Dict[str, float]:
    """
    Calculate throughput and utilization metrics.
    """
    required_columns = [charge_column, discharge_column]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    total_charge_kwh = float(df[charge_column].sum())
    total_discharge_kwh = float(df[discharge_column].sum())

    if storage_capacity_kwh > 0:
        estimated_cycles = total_discharge_kwh / storage_capacity_kwh
        utilization_ratio = total_discharge_kwh / storage_capacity_kwh
    else:
        estimated_cycles = 0.0
        utilization_ratio = 0.0

    return {
        "total_charge_kwh": total_charge_kwh,
        "total_discharge_kwh": total_discharge_kwh,
        "estimated_cycles": float(estimated_cycles),
        "utilization_ratio": float(utilization_ratio),
    }


def calculate_storage_revenue_metrics(
    df: pd.DataFrame,
    original_cost_column: str = "original_energy_cost",
    optimized_cost_column: str = "optimized_energy_cost",
    saving_column: str = "storage_cost_saving",
) -> Dict[str, float]:
    """
    Calculate storage revenue-related metrics.
    """
    required_columns = [original_cost_column, optimized_cost_column, saving_column]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    original_total_cost = float(df[original_cost_column].sum())
    optimized_total_cost = float(df[optimized_cost_column].sum())
    total_saving = float(df[saving_column].sum())

    saving_ratio = total_saving / original_total_cost if original_total_cost > 0 else 0.0

    return {
        "original_total_cost": original_total_cost,
        "optimized_total_cost": optimized_total_cost,
        "total_saving": total_saving,
        "saving_ratio": float(saving_ratio),
    }


def calculate_daily_storage_summary(
    df: pd.DataFrame,
    time_column: str = "time",
) -> pd.DataFrame:
    """
    Aggregate daily storage operation summary.
    """
    required_columns = [
        time_column,
        "storage_charge_kwh_grid",
        "storage_discharge_kwh_load",
        "storage_cost_saving",
    ]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    result = df.copy()
    result[time_column] = pd.to_datetime(result[time_column], errors="coerce")

    if result[time_column].isna().any():
        raise ValueError(f"Column '{time_column}' contains invalid datetime values.")

    result["date"] = result[time_column].dt.date

    summary = (
        result.groupby("date", as_index=False)
        .agg(
            daily_charge_kwh=("storage_charge_kwh_grid", "sum"),
            daily_discharge_kwh=("storage_discharge_kwh_load", "sum"),
            daily_saving=("storage_cost_saving", "sum"),
        )
        .reset_index(drop=True)
    )

    return summary


# ============================================================
# End-to-end helper for MVP
# ============================================================

def summarize_storage_simulation(
    df: pd.DataFrame,
    storage_capacity_kwh: float,
    storage_power_kw: float,
    charge_efficiency: float,
    discharge_efficiency: float,
    initial_soc_ratio: float = 0.0,
    min_soc_ratio: float = 0.0,
    max_soc_ratio: float = 1.0,
    charge_periods: Optional[List[str]] = None,
    discharge_periods: Optional[List[str]] = None,
) -> Dict[str, object]:
    """
    Full MVP pipeline for storage simulation.
    """
    result_df = simulate_storage_operation(
        df=df,
        storage_capacity_kwh=storage_capacity_kwh,
        storage_power_kw=storage_power_kw,
        charge_efficiency=charge_efficiency,
        discharge_efficiency=discharge_efficiency,
        initial_soc_ratio=initial_soc_ratio,
        min_soc_ratio=min_soc_ratio,
        max_soc_ratio=max_soc_ratio,
        charge_periods=charge_periods,
        discharge_periods=discharge_periods,
    )

    throughput_metrics = calculate_storage_throughput_metrics(
        result_df,
        storage_capacity_kwh=storage_capacity_kwh,
    )

    revenue_metrics = calculate_storage_revenue_metrics(result_df)

    daily_summary = calculate_daily_storage_summary(result_df)

    return {
        "result_df": result_df,
        "throughput_metrics": throughput_metrics,
        "revenue_metrics": revenue_metrics,
        "daily_summary": daily_summary,
    }