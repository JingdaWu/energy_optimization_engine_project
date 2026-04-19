from __future__ import annotations

from typing import Dict

import pandas as pd

from utils.validators import (
    validate_capacity_charge_params,
    validate_demand_charge_params,
)


# ============================================================
# Maximum power helpers
# ============================================================

def calculate_max_power_kw(
    df: pd.DataFrame,
    load_column: str = "load_kwh",
) -> float:
    """
    Approximate maximum power from hourly load data.

    Assumption
    ----------
    Hourly load_kwh is treated as an hourly average kW-equivalent value.
    """
    if load_column not in df.columns:
        raise ValueError(f"Column '{load_column}' not found in dataframe.")

    if df.empty:
        raise ValueError("Input dataframe is empty.")

    return float(df[load_column].max())


def calculate_load_factor_from_max_power(
    df: pd.DataFrame,
    load_column: str = "load_kwh",
) -> float:
    """
    Calculate load factor using average load / maximum power.
    """
    if load_column not in df.columns:
        raise ValueError(f"Column '{load_column}' not found in dataframe.")

    avg_load = float(df[load_column].mean())
    max_power = calculate_max_power_kw(df, load_column=load_column)

    if max_power <= 0:
        return 0.0

    return float(avg_load / max_power)


# ============================================================
# Capacity charge
# ============================================================

def calculate_capacity_charge(
    max_power_kw: float,
    capacity_price_per_kw: float,
    contract_buffer_ratio: float,
) -> Dict[str, float]:
    """
    Calculate capacity-based power charge.

    Formula
    -------
    contract_capacity_kw = max_power_kw * (1 + contract_buffer_ratio)
    capacity_charge = contract_capacity_kw * capacity_price_per_kw
    """
    validate_capacity_charge_params(
        capacity_price_per_kw=capacity_price_per_kw,
        contract_buffer_ratio=contract_buffer_ratio,
    )

    if max_power_kw < 0:
        raise ValueError("max_power_kw cannot be negative.")

    contract_capacity_kw = max_power_kw * (1 + contract_buffer_ratio)
    power_charge = contract_capacity_kw * capacity_price_per_kw

    return {
        "max_power_kw": float(max_power_kw),
        "contract_capacity_kw": float(contract_capacity_kw),
        "power_charge": float(power_charge),
    }


# ============================================================
# Demand charge
# ============================================================

def calculate_demand_charge(
    max_power_kw: float,
    demand_price_per_kw: float,
) -> Dict[str, float]:
    """
    Calculate demand-based power charge.

    Formula
    -------
    power_charge = max_power_kw * demand_price_per_kw
    """
    validate_demand_charge_params(
        demand_price_per_kw=demand_price_per_kw,
    )

    if max_power_kw < 0:
        raise ValueError("max_power_kw cannot be negative.")

    power_charge = max_power_kw * demand_price_per_kw

    return {
        "max_power_kw": float(max_power_kw),
        "power_charge": float(power_charge),
    }


# ============================================================
# Unified power charge interface
# ============================================================

def calculate_power_charge(
    df: pd.DataFrame,
    mode: str,
    load_column: str = "load_kwh",
    capacity_price_per_kw: float = 0.0,
    contract_buffer_ratio: float = 0.0,
    demand_price_per_kw: float = 0.0,
) -> Dict[str, float]:
    """
    Unified interface for power charge calculation.

    Supported modes
    ---------------
    - "capacity"
    - "demand"
    """
    max_power_kw = calculate_max_power_kw(df, load_column=load_column)

    if mode == "capacity":
        result = calculate_capacity_charge(
            max_power_kw=max_power_kw,
            capacity_price_per_kw=capacity_price_per_kw,
            contract_buffer_ratio=contract_buffer_ratio,
        )
        result["mode"] = "capacity"
        return result

    if mode == "demand":
        result = calculate_demand_charge(
            max_power_kw=max_power_kw,
            demand_price_per_kw=demand_price_per_kw,
        )
        result["mode"] = "demand"
        return result

    raise ValueError("mode must be either 'capacity' or 'demand'")


# ============================================================
# Compare original vs optimized power charge
# ============================================================

def compare_power_charge_before_after_storage(
    original_df: pd.DataFrame,
    optimized_df: pd.DataFrame,
    mode: str,
    original_load_column: str = "load_kwh",
    optimized_load_column: str = "net_load_kwh",
    capacity_price_per_kw: float = 0.0,
    contract_buffer_ratio: float = 0.0,
    demand_price_per_kw: float = 0.0,
) -> Dict[str, float]:
    """
    Compare power charge before and after storage.
    """
    original_charge = calculate_power_charge(
        df=original_df,
        mode=mode,
        load_column=original_load_column,
        capacity_price_per_kw=capacity_price_per_kw,
        contract_buffer_ratio=contract_buffer_ratio,
        demand_price_per_kw=demand_price_per_kw,
    )

    optimized_charge = calculate_power_charge(
        df=optimized_df,
        mode=mode,
        load_column=optimized_load_column,
        capacity_price_per_kw=capacity_price_per_kw,
        contract_buffer_ratio=contract_buffer_ratio,
        demand_price_per_kw=demand_price_per_kw,
    )

    original_power_charge = float(original_charge["power_charge"])
    optimized_power_charge = float(optimized_charge["power_charge"])

    return {
        "mode": mode,
        "original_max_power_kw": float(original_charge["max_power_kw"]),
        "optimized_max_power_kw": float(optimized_charge["max_power_kw"]),
        "original_power_charge": original_power_charge,
        "optimized_power_charge": optimized_power_charge,
        "power_charge_saving": float(original_power_charge - optimized_power_charge),
        "original_contract_capacity_kw": float(original_charge.get("contract_capacity_kw", 0.0)),
        "optimized_contract_capacity_kw": float(optimized_charge.get("contract_capacity_kw", 0.0)),
    }