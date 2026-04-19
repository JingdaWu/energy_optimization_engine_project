from __future__ import annotations

from typing import Dict, List, Optional

from utils.validators import validate_financial_params


# ============================================================
# Core financial metric calculation
# ============================================================

def calculate_annual_net_benefit(
    annual_energy_saving: float,
    annual_om_cost: float,
    annual_other_benefit: float = 0.0,
) -> float:
    """
    Calculate annual net benefit.

    Formula:
    annual_net_benefit = annual_energy_saving + annual_other_benefit - annual_om_cost
    """
    validate_financial_params(
        capex_total=0.0,
        annual_om_cost=annual_om_cost,
    )

    if annual_energy_saving < 0:
        raise ValueError("annual_energy_saving cannot be negative.")

    if annual_other_benefit < 0:
        raise ValueError("annual_other_benefit cannot be negative.")

    annual_net_benefit = annual_energy_saving + annual_other_benefit - annual_om_cost
    return float(annual_net_benefit)


def calculate_simple_payback_years(
    capex_total: float,
    annual_net_benefit: float,
) -> Optional[float]:
    """
    Calculate simple payback period.
    """
    validate_financial_params(
        capex_total=capex_total,
        annual_om_cost=0.0,
    )

    if annual_net_benefit <= 0:
        return None

    return float(capex_total / annual_net_benefit)


def calculate_simple_roi(
    annual_net_benefit: float,
    capex_total: float,
) -> Optional[float]:
    """
    Calculate simple annual ROI.
    """
    validate_financial_params(
        capex_total=capex_total,
        annual_om_cost=0.0,
    )

    if capex_total <= 0:
        return None

    return float(annual_net_benefit / capex_total)


# ============================================================
# Degradation helpers
# ============================================================

def calculate_degradation_multiplier(
    year_index: int,
    annual_degradation_rate: float,
) -> float:
    """
    Calculate remaining usable capacity / revenue multiplier for a given year.

    year_index:
    - 1 means first operating year
    - 2 means second operating year
    """
    if year_index <= 0:
        raise ValueError("year_index must be greater than 0.")

    validate_financial_params(
        capex_total=0.0,
        annual_om_cost=0.0,
        annual_degradation_rate=annual_degradation_rate,
    )

    multiplier = (1 - annual_degradation_rate) ** (year_index - 1)
    return float(multiplier)


def build_degraded_annual_benefit_series(
    base_annual_energy_saving: float,
    annual_om_cost: float,
    project_years: int,
    annual_other_benefit: float = 0.0,
    annual_degradation_rate: float = 0.0,
) -> List[float]:
    """
    Build annual net benefit series with degradation applied to energy-saving benefit.

    Assumption:
    - energy-saving-related benefit degrades with storage usable capacity
    - O&M cost does not degrade
    """
    validate_financial_params(
        capex_total=0.0,
        annual_om_cost=annual_om_cost,
        project_years=project_years,
        annual_degradation_rate=annual_degradation_rate,
    )

    if base_annual_energy_saving < 0:
        raise ValueError("base_annual_energy_saving cannot be negative.")

    if annual_other_benefit < 0:
        raise ValueError("annual_other_benefit cannot be negative.")

    annual_benefits: List[float] = []

    for year in range(1, project_years + 1):
        degradation_multiplier = calculate_degradation_multiplier(
            year_index=year,
            annual_degradation_rate=annual_degradation_rate,
        )

        degraded_energy_saving = base_annual_energy_saving * degradation_multiplier
        annual_net_benefit = (
            degraded_energy_saving
            + annual_other_benefit
            - annual_om_cost
        )

        annual_benefits.append(float(annual_net_benefit))

    return annual_benefits


# ============================================================
# Project-level cash flow calculation
# ============================================================

def build_project_cash_flows(
    capex_total: float,
    annual_net_benefit: float,
    project_years: int,
    residual_value: float = 0.0,
) -> List[float]:
    """
    Build simplified annual project cash flows without degradation.

    Convention:
    - Year 0: negative CAPEX
    - Year 1..N: annual net benefit
    - Final year includes residual value
    """
    validate_financial_params(
        capex_total=capex_total,
        annual_om_cost=0.0,
        project_years=project_years,
    )

    if residual_value < 0:
        raise ValueError("residual_value cannot be negative.")

    cash_flows = [-float(capex_total)]

    for year in range(1, project_years + 1):
        yearly_cash = float(annual_net_benefit)
        if year == project_years:
            yearly_cash += float(residual_value)
        cash_flows.append(yearly_cash)

    return cash_flows


def build_project_cash_flows_with_degradation(
    capex_total: float,
    base_annual_energy_saving: float,
    annual_om_cost: float,
    project_years: int,
    annual_other_benefit: float = 0.0,
    annual_degradation_rate: float = 0.0,
    residual_value: float = 0.0,
) -> List[float]:
    """
    Build annual cash flow series with degradation applied.
    """
    validate_financial_params(
        capex_total=capex_total,
        annual_om_cost=annual_om_cost,
        project_years=project_years,
        annual_degradation_rate=annual_degradation_rate,
    )

    if residual_value < 0:
        raise ValueError("residual_value cannot be negative.")

    annual_benefits = build_degraded_annual_benefit_series(
        base_annual_energy_saving=base_annual_energy_saving,
        annual_om_cost=annual_om_cost,
        project_years=project_years,
        annual_other_benefit=annual_other_benefit,
        annual_degradation_rate=annual_degradation_rate,
    )

    cash_flows = [-float(capex_total)]

    for idx, annual_benefit in enumerate(annual_benefits, start=1):
        yearly_cash = float(annual_benefit)
        if idx == project_years:
            yearly_cash += float(residual_value)
        cash_flows.append(yearly_cash)

    return cash_flows


def calculate_npv(
    cash_flows: List[float],
    discount_rate: float,
) -> float:
    """
    Calculate net present value (NPV).

    Note:
    discount_rate must be greater than -1.0, otherwise
    (1 + discount_rate) becomes zero or negative.
    """
    if discount_rate <= -1:
        raise ValueError("discount_rate must be greater than -1.")

    npv = 0.0
    for year, cash_flow in enumerate(cash_flows):
        npv += cash_flow / ((1 + discount_rate) ** year)

    return float(npv)


# ============================================================
# IRR calculation
# ============================================================

def calculate_irr(
    cash_flows: List[float],
    guess_low: float = -0.99,
    guess_high: float = 5.0,
    tolerance: float = 1e-6,
    max_iterations: int = 200,
) -> Optional[float]:
    """
    Calculate IRR using binary search.
    """
    if len(cash_flows) < 2:
        return None

    low = guess_low
    high = guess_high

    npv_low = calculate_npv(cash_flows, low)
    npv_high = calculate_npv(cash_flows, high)

    if npv_low == 0:
        return float(low)

    if npv_high == 0:
        return float(high)

    if npv_low * npv_high > 0:
        return None

    for _ in range(max_iterations):
        mid = (low + high) / 2
        npv_mid = calculate_npv(cash_flows, mid)

        if abs(npv_mid) < tolerance:
            return float(mid)

        if npv_low * npv_mid < 0:
            high = mid
            npv_high = npv_mid
        else:
            low = mid
            npv_low = npv_mid

    return float((low + high) / 2)


# ============================================================
# LCOE calculation
# ============================================================

def calculate_discounted_lcoe(
    capex_total: float,
    annual_om_cost: float,
    base_annual_discharge_kwh: float,
    project_years: int,
    discount_rate: float,
    annual_degradation_rate: float = 0.0,
) -> Optional[float]:
    """
    Calculate simplified discounted LCOE for storage.

    Formula:
    LCOE = discounted total lifecycle cost / discounted total discharge energy
    """
    validate_financial_params(
        capex_total=capex_total,
        annual_om_cost=annual_om_cost,
        project_years=project_years,
        discount_rate=discount_rate,
        annual_degradation_rate=annual_degradation_rate,
    )

    if base_annual_discharge_kwh <= 0:
        return None

    discounted_cost = float(capex_total)
    discounted_energy = 0.0

    for year in range(1, project_years + 1):
        degradation_multiplier = calculate_degradation_multiplier(
            year_index=year,
            annual_degradation_rate=annual_degradation_rate,
        )

        annual_discharge = base_annual_discharge_kwh * degradation_multiplier
        discount_factor = (1 + discount_rate) ** year

        discounted_cost += annual_om_cost / discount_factor
        discounted_energy += annual_discharge / discount_factor

    if discounted_energy <= 0:
        return None

    return float(discounted_cost / discounted_energy)


# ============================================================
# Annualization helpers
# ============================================================

def annualize_saving_from_sample(
    sample_total_saving: float,
    sample_days: float,
) -> float:
    """
    Convert saving from sample period to annualized saving.
    """
    if sample_total_saving < 0:
        raise ValueError("sample_total_saving cannot be negative.")

    if sample_days <= 0:
        raise ValueError("sample_days must be greater than 0.")

    annual_saving = sample_total_saving / sample_days * 365
    return float(annual_saving)


def annualize_discharge_from_sample(
    sample_total_discharge_kwh: float,
    sample_days: float,
) -> float:
    """
    Convert discharge throughput from sample period to annualized discharge.
    """
    if sample_total_discharge_kwh < 0:
        raise ValueError("sample_total_discharge_kwh cannot be negative.")

    if sample_days <= 0:
        raise ValueError("sample_days must be greater than 0.")

    annual_discharge = sample_total_discharge_kwh / sample_days * 365
    return float(annual_discharge)


def estimate_sample_days_from_hours(total_rows: int) -> float:
    """
    Estimate sample duration in days based on hourly rows.
    """
    if total_rows <= 0:
        raise ValueError("total_rows must be greater than 0.")

    return float(total_rows / 24.0)


# ============================================================
# Finance summary
# ============================================================

def summarize_financial_analysis(
    capex_total: float,
    annual_energy_saving: float,
    annual_om_cost: float,
    annual_other_benefit: float = 0.0,
    project_years: int = 10,
    discount_rate: float = 0.08,
    residual_value: float = 0.0,
    annual_degradation_rate: float = 0.0,
    annual_discharge_kwh: Optional[float] = None,
    include_irr: bool = True,
) -> Dict[str, object]:
    """
    Full financial summary with degradation support.
    """
    validate_financial_params(
        capex_total=capex_total,
        annual_om_cost=annual_om_cost,
        project_years=project_years,
        discount_rate=discount_rate,
        annual_degradation_rate=annual_degradation_rate,
    )

    annual_net_benefit_year1 = calculate_annual_net_benefit(
        annual_energy_saving=annual_energy_saving,
        annual_om_cost=annual_om_cost,
        annual_other_benefit=annual_other_benefit,
    )

    cash_flows = build_project_cash_flows_with_degradation(
        capex_total=capex_total,
        base_annual_energy_saving=annual_energy_saving,
        annual_om_cost=annual_om_cost,
        project_years=project_years,
        annual_other_benefit=annual_other_benefit,
        annual_degradation_rate=annual_degradation_rate,
        residual_value=residual_value,
    )

    npv = calculate_npv(
        cash_flows=cash_flows,
        discount_rate=discount_rate,
    )

    irr = calculate_irr(cash_flows) if include_irr else None

    annual_benefit_series = cash_flows[1:]
    avg_annual_net_benefit = (
        float(sum(annual_benefit_series) / len(annual_benefit_series))
        if len(annual_benefit_series) > 0
        else 0.0
    )

    payback_years = calculate_simple_payback_years(
        capex_total=capex_total,
        annual_net_benefit=avg_annual_net_benefit,
    )

    simple_roi = calculate_simple_roi(
        annual_net_benefit=avg_annual_net_benefit,
        capex_total=capex_total,
    )

    lcoe = None
    if annual_discharge_kwh is not None:
        lcoe = calculate_discounted_lcoe(
            capex_total=capex_total,
            annual_om_cost=annual_om_cost,
            base_annual_discharge_kwh=annual_discharge_kwh,
            project_years=project_years,
            discount_rate=discount_rate,
            annual_degradation_rate=annual_degradation_rate,
        )

    return {
        "annual_energy_saving": float(annual_energy_saving),
        "annual_other_benefit": float(annual_other_benefit),
        "annual_om_cost": float(annual_om_cost),
        "annual_net_benefit_year1": float(annual_net_benefit_year1),
        "average_annual_net_benefit": float(avg_annual_net_benefit),
        "capex_total": float(capex_total),
        "simple_payback_years": payback_years,
        "simple_roi": simple_roi,
        "project_years": int(project_years),
        "discount_rate": float(discount_rate),
        "annual_degradation_rate": float(annual_degradation_rate),
        "residual_value": float(residual_value),
        "cash_flows": cash_flows,
        "npv": float(npv),
        "irr": irr,
        "lcoe": lcoe,
    }


def summarize_finance_from_storage_result(
    total_sample_saving: float,
    sample_row_count: int,
    capex_total: float,
    annual_om_cost: float,
    annual_other_benefit: float = 0.0,
    project_years: int = 10,
    discount_rate: float = 0.08,
    residual_value: float = 0.0,
    annual_degradation_rate: float = 0.0,
    total_sample_discharge_kwh: Optional[float] = None,
    include_irr: bool = True,
) -> Dict[str, object]:
    """
    Convert storage simulation sample saving into annualized finance summary.
    """
    sample_days = estimate_sample_days_from_hours(sample_row_count)

    annual_energy_saving = annualize_saving_from_sample(
        sample_total_saving=total_sample_saving,
        sample_days=sample_days,
    )

    annual_discharge_kwh = None
    if total_sample_discharge_kwh is not None:
        annual_discharge_kwh = annualize_discharge_from_sample(
            sample_total_discharge_kwh=total_sample_discharge_kwh,
            sample_days=sample_days,
        )

    finance_summary = summarize_financial_analysis(
        capex_total=capex_total,
        annual_energy_saving=annual_energy_saving,
        annual_om_cost=annual_om_cost,
        annual_other_benefit=annual_other_benefit,
        project_years=project_years,
        discount_rate=discount_rate,
        residual_value=residual_value,
        annual_degradation_rate=annual_degradation_rate,
        annual_discharge_kwh=annual_discharge_kwh,
        include_irr=include_irr,
    )

    finance_summary["sample_days"] = float(sample_days)
    finance_summary["sample_row_count"] = int(sample_row_count)
    finance_summary["annual_discharge_kwh"] = annual_discharge_kwh

    return finance_summary