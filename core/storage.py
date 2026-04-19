from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd
from scipy.optimize import linprog

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
# 2026-04-19: Added full-horizon planning helpers.
# This replaces the previous day-by-day planning logic.
# The new version reads the full uploaded load table first and
# then performs one global offline optimization across the
# entire horizon.
# ============================================================

def _normalize_period_list(periods: Optional[List[str]]) -> List[str]:
    if periods is None:
        return []
    return [str(period).lower() for period in periods]


def _build_period_preference_series(
    df: pd.DataFrame,
    tariff_period_column: str,
    preferred_periods: List[str],
) -> pd.Series:
    period_series = df[tariff_period_column].astype(str).str.lower()
    return period_series.isin(preferred_periods).astype(int)


def _build_full_horizon_dispatch_plan(
    df: pd.DataFrame,
    storage_capacity_kwh: float,
    storage_power_kw: float,
    charge_efficiency: float,
    discharge_efficiency: float,
    initial_soc_ratio: float,
    min_soc_ratio: float,
    max_soc_ratio: float,
    charge_periods: List[str],
    discharge_periods: List[str],
    load_column: str,
    tariff_period_column: str,
    price_column: str,
    timestep_hours: float,
    demand_limit_kw: Optional[float] = None,
) -> pd.DataFrame:
    """
    Build one global offline storage dispatch plan across the full horizon.

    Optimization target
    -------------------
    Minimize total energy cost over the uploaded horizon.

    Notes
    -----
    - the whole uploaded table is optimized at once
    - charging and discharging can happen on multiple cycles across the horizon
    - charging headroom can be limited by demand_limit_kw
    """
    if price_column not in df.columns:
        raise ValueError(f"Column '{price_column}' is required for full-horizon optimization.")

    result = df.copy().reset_index(drop=True)
    n = len(result)

    if n == 0:
        raise ValueError('Input dataframe is empty.')

    soc_bounds = calculate_usable_soc_bounds(
        storage_capacity_kwh=storage_capacity_kwh,
        min_soc_ratio=min_soc_ratio,
        max_soc_ratio=max_soc_ratio,
    )
    min_soc_kwh = soc_bounds['min_soc_kwh']
    max_soc_kwh = soc_bounds['max_soc_kwh']
    initial_soc_kwh = storage_capacity_kwh * initial_soc_ratio

    max_charge_per_step = storage_power_kw * timestep_hours
    max_discharge_per_step = storage_power_kw * timestep_hours

    charge_headroom = pd.Series(max_charge_per_step, index=result.index, dtype=float)
    if demand_limit_kw is not None:
        charge_headroom = (float(demand_limit_kw) - result[load_column].astype(float)).clip(lower=0.0)
        charge_headroom = charge_headroom.clip(upper=max_charge_per_step)

    discharge_headroom = result[load_column].astype(float).clip(lower=0.0, upper=max_discharge_per_step)

    period_series = result[tariff_period_column].astype(str).str.lower()
    allowed_charge_mask = period_series.isin(charge_periods)
    allowed_discharge_mask = period_series.isin(discharge_periods)

    # ============================================================
    # 2026-04-19: Full-horizon LP objective.
    # Price is the main driver. Small preference bonuses gently push
    # charging toward super_valley/valley and discharging toward
    # critical_peak/peak when prices are close.
    # ============================================================
    charge_priority_bonus = pd.Series(0.0, index=result.index, dtype=float)
    charge_priority_bonus.loc[period_series == 'super_valley'] = 0.003
    charge_priority_bonus.loc[period_series == 'valley'] = 0.001

    discharge_priority_bonus = pd.Series(0.0, index=result.index, dtype=float)
    discharge_priority_bonus.loc[period_series == 'critical_peak'] = 0.003
    discharge_priority_bonus.loc[period_series == 'peak'] = 0.001

    effective_charge_price = result[price_column].astype(float) - charge_priority_bonus
    effective_discharge_price = result[price_column].astype(float) + discharge_priority_bonus

    var_count = 2 * n
    c = [0.0] * var_count
    bounds = []

    for i in range(n):
        charge_upper = float(charge_headroom.iloc[i]) if bool(allowed_charge_mask.iloc[i]) else 0.0
        discharge_upper = float(discharge_headroom.iloc[i]) if bool(allowed_discharge_mask.iloc[i]) else 0.0

        c[i] = float(effective_charge_price.iloc[i])
        c[n + i] = -float(effective_discharge_price.iloc[i])
        bounds.append((0.0, max(0.0, charge_upper)))

    for i in range(n):
        discharge_upper = float(discharge_headroom.iloc[i]) if bool(allowed_discharge_mask.iloc[i]) else 0.0
        bounds.append((0.0, max(0.0, discharge_upper)))

    a_ub = []
    b_ub = []

    for t in range(n):
        # cumulative SOC upper bound
        row_upper = [0.0] * var_count
        for i in range(t + 1):
            row_upper[i] = charge_efficiency
            row_upper[n + i] = -1.0 / discharge_efficiency
        a_ub.append(row_upper)
        b_ub.append(max_soc_kwh - initial_soc_kwh)

        # cumulative SOC lower bound
        row_lower = [0.0] * var_count
        for i in range(t + 1):
            row_lower[i] = -charge_efficiency
            row_lower[n + i] = 1.0 / discharge_efficiency
        a_ub.append(row_lower)
        b_ub.append(initial_soc_kwh - min_soc_kwh)

    lp_result = linprog(c=c, A_ub=a_ub, b_ub=b_ub, bounds=bounds, method='highs')

    if not lp_result.success:
        raise ValueError(f"Full-horizon storage optimization failed: {lp_result.message}")

    solution = lp_result.x
    charge_from_grid = solution[:n]
    discharge_to_load = solution[n:]

    # ============================================================
    # 2026-04-19: Convert LP result back to sequential SOC columns.
    # ============================================================
    soc_kwh = initial_soc_kwh
    charge_into_soc_list = []
    discharge_from_soc_list = []
    soc_kwh_list = []
    net_load_kwh_list = []
    storage_action_list = []
    # 2026-04-19: Added explicit list initialization for demand-limit tracing.
    demand_limited_flag_list = []

    for i in range(n):
        charge_i = float(charge_from_grid[i])
        discharge_i = float(discharge_to_load[i])

        if demand_limit_kw is not None:
            limit_i = float(charge_headroom.iloc[i])
            demand_limited_flag_list.append(int(limit_i + 1e-9 < max_charge_per_step))
        else:
            demand_limited_flag_list.append(0)

        charge_into_soc = charge_i * charge_efficiency
        discharge_from_soc = discharge_i / discharge_efficiency if discharge_efficiency > 0 else 0.0
        soc_kwh = soc_kwh + charge_into_soc - discharge_from_soc
        soc_kwh = min(max(soc_kwh, min_soc_kwh), max_soc_kwh)

        net_load_kwh = float(result.loc[i, load_column]) + charge_i - discharge_i

        if charge_i > 1e-9 and discharge_i > 1e-9:
            action = 'charge_discharge'
        elif charge_i > 1e-9:
            action = 'charge'
        elif discharge_i > 1e-9:
            action = 'discharge'
        else:
            action = 'idle'

        charge_into_soc_list.append(float(charge_into_soc))
        discharge_from_soc_list.append(float(discharge_from_soc))
        soc_kwh_list.append(float(soc_kwh))
        net_load_kwh_list.append(float(net_load_kwh))
        storage_action_list.append(action)

    result['storage_charge_kwh_grid'] = charge_from_grid.astype(float)
    result['storage_charge_kwh_soc'] = charge_into_soc_list
    result['storage_discharge_kwh_load'] = discharge_to_load.astype(float)
    result['storage_discharge_kwh_soc'] = discharge_from_soc_list
    result['soc_kwh'] = soc_kwh_list
    result['net_load_kwh'] = net_load_kwh_list
    result['storage_action'] = storage_action_list

    # ============================================================
    # 2026-04-19: Added full-horizon tracing columns for report use.
    # ============================================================
    result['planned_charge_allowed'] = allowed_charge_mask.astype(int)
    result['planned_discharge_level'] = allowed_discharge_mask.astype(int)
    result['charge_demand_limited_flag'] = demand_limited_flag_list
    result['global_planning_used_flag'] = 1
    result['in_priority_charge_period'] = _build_period_preference_series(
        result, tariff_period_column=tariff_period_column, preferred_periods=charge_periods
    )
    result['in_priority_discharge_period'] = _build_period_preference_series(
        result, tariff_period_column=tariff_period_column, preferred_periods=discharge_periods
    )

    if price_column in result.columns:
        result['original_energy_cost'] = result[load_column] * result[price_column]
        result['optimized_energy_cost'] = result['net_load_kwh'] * result[price_column]
        result['storage_cost_saving'] = result['original_energy_cost'] - result['optimized_energy_cost']

    return result


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
    demand_limit_kw: Optional[float] = None,
) -> pd.DataFrame:
    """
    Simulate storage operation.

    Updated strategy on 2026-04-19:
    - read the full uploaded horizon first
    - optimize the full horizon in one pass
    - allow multiple charge/discharge cycles across the horizon
    - still keep optional charge headroom control via demand_limit_kw
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

    required_columns = [time_column, load_column, tariff_period_column, price_column]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns for storage simulation: {missing_columns}")

    # ============================================================
    # 2026-04-19: Changed default charge/discharge periods again.
    # The full-horizon optimizer now prefers charging in deep low-price
    # periods first and discharging in the highest-price periods first.
    # ============================================================
    if charge_periods is None:
        charge_periods = ["super_valley", "valley", "flat"]

    if discharge_periods is None:
        discharge_periods = ["critical_peak", "peak", "flat"]

    charge_periods = _normalize_period_list(charge_periods)
    discharge_periods = _normalize_period_list(discharge_periods)

    result = df.copy().sort_values(time_column).reset_index(drop=True)
    result[time_column] = pd.to_datetime(result[time_column], errors="coerce")
    if result[time_column].isna().any():
        raise ValueError(f"Column '{time_column}' contains invalid datetime values.")

    # ============================================================
    # 2026-04-19: Full-horizon offline optimization.
    # ============================================================
    result = _build_full_horizon_dispatch_plan(
        df=result,
        storage_capacity_kwh=storage_capacity_kwh,
        storage_power_kw=storage_power_kw,
        charge_efficiency=charge_efficiency,
        discharge_efficiency=discharge_efficiency,
        initial_soc_ratio=initial_soc_ratio,
        min_soc_ratio=min_soc_ratio,
        max_soc_ratio=max_soc_ratio,
        charge_periods=charge_periods,
        discharge_periods=discharge_periods,
        load_column=load_column,
        tariff_period_column=tariff_period_column,
        price_column=price_column,
        timestep_hours=timestep_hours,
        demand_limit_kw=demand_limit_kw,
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

    # ============================================================
    # 2026-04-19: Added dispatch quality metrics for the new
    # daily planning strategy and report output.
    # ============================================================
    charge_event_count = int((df[charge_column] > 0).sum())
    discharge_event_count = int((df[discharge_column] > 0).sum())

    priority_charge_kwh = 0.0
    if "in_priority_charge_period" in df.columns:
        priority_charge_kwh = float(
            df.loc[df["in_priority_charge_period"] == 1, charge_column].sum()
        )

    priority_discharge_kwh = 0.0
    if "in_priority_discharge_period" in df.columns:
        priority_discharge_kwh = float(
            df.loc[df["in_priority_discharge_period"] == 1, discharge_column].sum()
        )

    priority_charge_ratio = (
        priority_charge_kwh / total_charge_kwh if total_charge_kwh > 0 else 0.0
    )
    priority_discharge_ratio = (
        priority_discharge_kwh / total_discharge_kwh if total_discharge_kwh > 0 else 0.0
    )

    charge_demand_limited_hours = 0
    if "charge_demand_limited_flag" in df.columns:
        charge_demand_limited_hours = int(df["charge_demand_limited_flag"].sum())

    global_planning_rows = 0
    if 'global_planning_used_flag' in df.columns:
        global_planning_rows = int(df['global_planning_used_flag'].sum())

    return {
        "total_charge_kwh": total_charge_kwh,
        "total_discharge_kwh": total_discharge_kwh,
        "estimated_cycles": float(estimated_cycles),
        "utilization_ratio": float(utilization_ratio),
        "charge_event_count": int(charge_event_count),
        "discharge_event_count": int(discharge_event_count),
        "priority_charge_ratio": float(priority_charge_ratio),
        "priority_discharge_ratio": float(priority_discharge_ratio),
        "charge_demand_limited_hours": int(charge_demand_limited_hours),
        "global_planning_rows": int(global_planning_rows),
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
    demand_limit_kw: Optional[float] = None,
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
        demand_limit_kw=demand_limit_kw,
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
