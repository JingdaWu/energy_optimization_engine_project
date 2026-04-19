from __future__ import annotations

from typing import Dict, List, Optional


# ============================================================
# Report text templates
# ============================================================

REPORT_TEXT = {
    "zh": {
        "na": "N/A",
        "payback_not_achievable": "当前假设下无法回本",

        "load_extra_max_power": "估算最大功率为 {max_power:.2f} kW。",
        "load_summary": (
            "该工厂在样本周期内的峰值负荷为 {peak_load:.2f} kWh，"
            "平均负荷为 {avg_load:.2f} kWh，最低负荷为 {min_load:.2f} kWh。"
            "峰谷差为 {peak_valley_diff:.2f} kWh，负载率为 {load_factor:.2%}。"
            "样本周期总用电量为 {total_load:.2f} kWh。"
            "{extra}"
        ),

        "tariff_sample_energy_cost": "样本周期电量电费为 {sample_energy_cost}。",
        "tariff_annual_energy_cost": "折算全年电量电费约为 {annual_energy_cost}。",
        "tariff_weighted_price": "加权平均电价为 {weighted_average_price}。",
        "tariff_capacity_charge": (
            "按容量计费方式估算，最大功率约为 {max_power:.2f} kW，"
            "契约容量约为 {contract_capacity:.2f} kW，功率电费为 {power_charge}。"
        ),
        "tariff_demand_charge": (
            "按需量计费方式估算，最大功率约为 {max_power:.2f} kW，"
            "功率电费为 {power_charge}。"
        ),

        "storage_summary": (
            "在当前规则策略下，储能系统在样本周期内累计充电 {total_charge}，"
            "累计放电 {total_discharge}，估算循环次数为 {estimated_cycles:.2f} 次，"
            "利用率为 {utilization_ratio}。"
            "其中电量电费节省为 {energy_saving}，"
            "功率电费节省为 {power_charge_saving}，"
            "合计节省为 {total_saving}。"
        ),

        "finance_summary": (
            "从投资角度看，首年年化节省约为 {annual_energy_saving}，"
            "考虑年容量衰减率 {annual_degradation_rate} 后，"
            "项目平均年净收益约为 {average_annual_net_benefit}。"
            "在总投资 {capex_total} 的假设下，"
            "静态回本周期为 {payback_years}，"
            "简单年化 ROI 为 {simple_roi}，"
            "项目 NPV 为 {npv}，"
            "IRR 为 {irr_text}，LCOE 为 {lcoe_text}。"
        ),

        "decision_no_positive_benefit": "在当前参数假设下，项目尚不能形成正的平均年净收益，因此暂不建议直接投资。",
        "decision_no_finite_payback": "虽然项目可以带来一定节省，但当前参数下仍无法形成明确回本周期，建议先优化电价差、储能成本或运行策略。",
        "decision_attractive": (
            "该项目具备较强投资吸引力。当前假设下，回本周期约为 {payback_years:.2f} 年，"
            "简单年化 ROI 为 {simple_roi:.2%}，样本周期总节省为 {total_saving_sample}。{extra}"
        ),
        "decision_payback_ok_roi_mid": (
            "该项目回本周期约为 {payback_years:.2f} 年，但 ROI 表现一般。"
            "建议先进行试点部署，或进一步优化储能规模、电价假设与控制策略。"
        ),
        "decision_positive_but_slow": (
            "该项目可以带来正向收益，但当前回本周期为 {payback_years:.2f} 年，"
            "高于建议阈值 {payback_threshold_years:.2f} 年，建议继续优化配置和参数后再评估。"
        ),
        "decision_extra_irr": " IRR 为 {irr:.2%}。",
        "decision_extra_lcoe": " LCOE 为 {lcoe_text}。",

        "finding_sample_total_cost": "样本周期总电费：{value}",
        "finding_annual_total_cost": "年化总电费：{value}",
        "finding_peak_load": "峰值负荷：{value:.2f} kWh",
        "finding_max_power": "最大功率：{value:.2f} kW",
        "finding_load_factor": "负载率：{value:.2%}",
        "finding_weighted_avg_price": "加权电价：{value}",
        "finding_storage_saving": "样本周期储能节省：{value}",
        "finding_average_annual_net_benefit": "平均年净收益：{value}",
        "finding_payback_years": "静态回本周期：{value}",
        "finding_simple_roi": "简单年化 ROI：{value}",
        "finding_irr": "IRR：{value}",
        "finding_lcoe": "LCOE：{value}",
    },
    "en": {
        "na": "N/A",
        "payback_not_achievable": "Not achievable under current assumptions",

        "load_extra_max_power": "Estimated maximum power is {max_power:.2f} kW.",
        "load_summary": (
            "The factory load profile shows a peak load of {peak_load:.2f} kWh, "
            "an average load of {avg_load:.2f} kWh, and a minimum load of {min_load:.2f} kWh. "
            "The peak-valley difference is {peak_valley_diff:.2f} kWh, "
            "while the load factor is {load_factor:.2%}. "
            "Total electricity consumption in the analyzed sample period is {total_load:.2f} kWh. "
            "{extra}"
        ),

        "tariff_sample_energy_cost": "Sample-period energy charge is {sample_energy_cost}. ",
        "tariff_annual_energy_cost": "Estimated annual energy charge is {annual_energy_cost}. ",
        "tariff_weighted_price": "Weighted average electricity price is {weighted_average_price}. ",
        "tariff_capacity_charge": (
            "Under capacity-based charging, estimated maximum power is {max_power:.2f} kW, "
            "contracted capacity is {contract_capacity:.2f} kW, "
            "and power charge is {power_charge}. "
        ),
        "tariff_demand_charge": (
            "Under demand-based charging, estimated maximum power is {max_power:.2f} kW, "
            "and power charge is {power_charge}. "
        ),

        "storage_summary": (
            "With the current rule-based strategy, the storage system charges {total_charge} "
            "and discharges {total_discharge} during the sample period. "
            "Estimated cycle count is {estimated_cycles:.2f}, "
            "and utilization ratio is {utilization_ratio}. "
            "Energy-charge saving is {energy_saving}, "
            "power-charge saving is {power_charge_saving}, "
            "and total saving is {total_saving}."
        ),

        "finance_summary": (
            "From an investment perspective, first-year annualized saving is approximately {annual_energy_saving}. "
            "With an annual degradation rate of {annual_degradation_rate}, "
            "average annual net benefit is {average_annual_net_benefit}. "
            "Given a total CAPEX of {capex_total}, "
            "simple payback is {payback_years}, "
            "simple annual ROI is {simple_roi}, "
            "NPV is {npv}, "
            "IRR is {irr_text}, and LCOE is {lcoe_text}."
        ),

        "decision_no_positive_benefit": (
            "Under the current assumptions, the project does not generate positive average annual net benefit, "
            "so investment is not recommended at this stage."
        ),
        "decision_no_finite_payback": (
            "Although the project creates some savings, the current assumptions do not support a finite payback period. "
            "It is recommended to optimize tariff spread, storage cost, or operation strategy first."
        ),
        "decision_attractive": (
            "The project appears financially attractive. Current assumptions suggest "
            "a payback period of {payback_years:.2f} years, "
            "a simple annual ROI of {simple_roi:.2%}, "
            "and sample-period total saving of {total_saving_sample}.{extra}"
        ),
        "decision_payback_ok_roi_mid": (
            "The project has a reasonable payback period of {payback_years:.2f} years, "
            "but ROI is moderate. A pilot implementation or further parameter optimization is recommended."
        ),
        "decision_positive_but_slow": (
            "The project creates positive value, but current payback is {payback_years:.2f} years, "
            "which is longer than the recommendation threshold of {payback_threshold_years:.2f} years. "
            "It is recommended to refine sizing and assumptions before investment."
        ),
        "decision_extra_irr": " IRR is {irr:.2%}.",
        "decision_extra_lcoe": " LCOE is {lcoe_text}.",

        "finding_sample_total_cost": "Sample-period total electricity cost: {value}",
        "finding_annual_total_cost": "Annual total electricity cost: {value}",
        "finding_peak_load": "Peak load: {value:.2f} kWh",
        "finding_max_power": "Maximum power: {value:.2f} kW",
        "finding_load_factor": "Load factor: {value:.2%}",
        "finding_weighted_avg_price": "Weighted average price: {value}",
        "finding_storage_saving": "Sample-period storage saving: {value}",
        "finding_average_annual_net_benefit": "Average annual net benefit: {value}",
        "finding_payback_years": "Simple payback: {value}",
        "finding_simple_roi": "Simple annual ROI: {value}",
        "finding_irr": "IRR: {value}",
        "finding_lcoe": "LCOE: {value}",
    },
}


def _rt(language: str) -> Dict[str, str]:
    return REPORT_TEXT.get(language, REPORT_TEXT["zh"])


# ============================================================
# Generic number formatting helpers
# ============================================================

def format_currency(value: Optional[float], currency_symbol: str = "¥", language: str = "zh") -> str:
    """
    Format number as currency string.
    """
    text = _rt(language)
    if value is None:
        return text["na"]
    return f"{currency_symbol}{value:,.2f}"


def format_percentage(value: Optional[float], digits: int = 2, language: str = "zh") -> str:
    """
    Format decimal number as percentage string.
    """
    text = _rt(language)
    if value is None:
        return text["na"]
    return f"{value * 100:.{digits}f}%"


def format_years(
    value: Optional[float],
    digits: int = 2,
    language: str = "zh",
) -> str:
    """
    Format payback years.
    """
    text = _rt(language)
    if value is None:
        return text["payback_not_achievable"]

    if language == "zh":
        return f"{value:.{digits}f} 年"
    return f"{value:.{digits}f} years"


def format_energy(value: Optional[float], digits: int = 2, unit: str = "kWh", language: str = "zh") -> str:
    """
    Format energy value.
    """
    text = _rt(language)
    if value is None:
        return text["na"]
    return f"{value:,.{digits}f} {unit}"


def format_power(value: Optional[float], digits: int = 2, unit: str = "kW", language: str = "zh") -> str:
    """
    Format power value.
    """
    text = _rt(language)
    if value is None:
        return text["na"]
    return f"{value:,.{digits}f} {unit}"


def format_price_per_energy(
    value: Optional[float],
    digits: int = 4,
    currency_symbol: str = "¥",
    language: str = "zh",
) -> str:
    """
    Format price per kWh.
    """
    text = _rt(language)
    if value is None:
        return text["na"]
    return f"{currency_symbol}{value:,.{digits}f}/kWh"


# ============================================================
# Load analysis report
# ============================================================

def generate_load_summary_text(
    load_metrics: Dict[str, float],
    max_power_kw: Optional[float] = None,
    language: str = "zh",
) -> str:
    """
    Generate narrative summary for load profile.
    """
    text = _rt(language)

    peak_load = load_metrics.get("peak_load_kwh")
    avg_load = load_metrics.get("avg_load_kwh")
    min_load = load_metrics.get("min_load_kwh")
    peak_valley_diff = load_metrics.get("peak_valley_diff_kwh")
    load_factor = load_metrics.get("load_factor")
    total_load = load_metrics.get("total_load_kwh")

    extra = ""
    if max_power_kw is not None:
        extra = text["load_extra_max_power"].format(max_power=max_power_kw)

    return text["load_summary"].format(
        peak_load=peak_load,
        avg_load=avg_load,
        min_load=min_load,
        peak_valley_diff=peak_valley_diff,
        load_factor=load_factor,
        total_load=total_load,
        extra=extra,
    )


# ============================================================
# Tariff analysis report
# ============================================================

def generate_tariff_summary_text(
    sample_energy_cost: float,
    annual_energy_cost: Optional[float],
    weighted_average_price: Optional[float],
    power_charge_summary: Optional[Dict[str, float]] = None,
    currency_symbol: str = "¥",
    language: str = "zh",
) -> str:
    """
    Generate tariff / electricity cost summary.
    """
    text = _rt(language)

    parts: List[str] = [
        text["tariff_sample_energy_cost"].format(
            sample_energy_cost=format_currency(sample_energy_cost, currency_symbol, language)
        )
    ]

    if annual_energy_cost is not None:
        parts.append(
            text["tariff_annual_energy_cost"].format(
                annual_energy_cost=format_currency(annual_energy_cost, currency_symbol, language)
            )
        )

    if weighted_average_price is not None:
        parts.append(
            text["tariff_weighted_price"].format(
                weighted_average_price=format_price_per_energy(
                    weighted_average_price,
                    currency_symbol=currency_symbol,
                    language=language,
                )
            )
        )

    if power_charge_summary is not None:
        mode = power_charge_summary.get("mode")
        power_charge = power_charge_summary.get("power_charge")
        max_power = power_charge_summary.get("max_power_kw")

        if mode == "capacity":
            contract_capacity = power_charge_summary.get("contract_capacity_kw")
            parts.append(
                text["tariff_capacity_charge"].format(
                    max_power=max_power,
                    contract_capacity=contract_capacity,
                    power_charge=format_currency(power_charge, currency_symbol, language),
                )
            )
        elif mode == "demand":
            parts.append(
                text["tariff_demand_charge"].format(
                    max_power=max_power,
                    power_charge=format_currency(power_charge, currency_symbol, language),
                )
            )

    return "".join(parts) if language == "zh" else "".join(parts).strip()


# ============================================================
# Storage simulation report
# ============================================================

def generate_storage_summary_text(
    throughput_metrics: Dict[str, float],
    energy_saving_sample: float,
    power_charge_saving_sample: float = 0.0,
    total_saving_sample: Optional[float] = None,
    currency_symbol: str = "¥",
    language: str = "zh",
) -> str:
    """
    Generate storage summary text.
    """
    text = _rt(language)

    total_charge = throughput_metrics.get("total_charge_kwh")
    total_discharge = throughput_metrics.get("total_discharge_kwh")
    estimated_cycles = throughput_metrics.get("estimated_cycles")
    utilization_ratio = throughput_metrics.get("utilization_ratio")

    if total_saving_sample is None:
        total_saving_sample = float(energy_saving_sample + power_charge_saving_sample)

    return text["storage_summary"].format(
        total_charge=format_energy(total_charge, language=language),
        total_discharge=format_energy(total_discharge, language=language),
        estimated_cycles=estimated_cycles,
        utilization_ratio=format_percentage(utilization_ratio, language=language),
        energy_saving=format_currency(energy_saving_sample, currency_symbol, language),
        power_charge_saving=format_currency(power_charge_saving_sample, currency_symbol, language),
        total_saving=format_currency(total_saving_sample, currency_symbol, language),
    )


# ============================================================
# Finance analysis report
# ============================================================

def generate_finance_summary_text(
    finance_summary: Dict[str, object],
    currency_symbol: str = "¥",
    language: str = "zh",
) -> str:
    """
    Generate narrative summary for finance metrics.
    """
    annual_energy_saving = finance_summary.get("annual_energy_saving")
    average_annual_net_benefit = finance_summary.get("average_annual_net_benefit")
    capex_total = finance_summary.get("capex_total")
    payback_years = finance_summary.get("simple_payback_years")
    simple_roi = finance_summary.get("simple_roi")
    npv = finance_summary.get("npv")
    irr = finance_summary.get("irr")
    lcoe = finance_summary.get("lcoe")
    annual_degradation_rate = finance_summary.get("annual_degradation_rate")

    irr_text = format_percentage(irr, language=language)
    lcoe_text = format_price_per_energy(lcoe, currency_symbol=currency_symbol, language=language)

    return _rt(language)["finance_summary"].format(
        annual_energy_saving=format_currency(annual_energy_saving, currency_symbol, language),
        annual_degradation_rate=format_percentage(annual_degradation_rate, language=language),
        average_annual_net_benefit=format_currency(average_annual_net_benefit, currency_symbol, language),
        capex_total=format_currency(capex_total, currency_symbol, language),
        payback_years=format_years(payback_years, language=language),
        simple_roi=format_percentage(simple_roi, language=language),
        npv=format_currency(npv, currency_symbol, language),
        irr_text=irr_text,
        lcoe_text=lcoe_text,
    )


# ============================================================
# Decision suggestion logic
# ============================================================

def generate_decision_recommendation(
    finance_summary: Dict[str, object],
    total_saving_sample: float,
    payback_threshold_years: float = 5.0,
    roi_threshold: float = 0.15,
    currency_symbol: str = "¥",
    language: str = "zh",
) -> str:
    """
    Generate simple investment recommendation.
    """
    text = _rt(language)

    payback_years = finance_summary.get("simple_payback_years")
    simple_roi = finance_summary.get("simple_roi")
    average_annual_net_benefit = finance_summary.get("average_annual_net_benefit")
    irr = finance_summary.get("irr")
    lcoe = finance_summary.get("lcoe")

    if average_annual_net_benefit is None or average_annual_net_benefit <= 0:
        return text["decision_no_positive_benefit"]

    if payback_years is None:
        return text["decision_no_finite_payback"]

    if payback_years <= payback_threshold_years and simple_roi is not None and simple_roi >= roi_threshold:
        extra = ""
        if irr is not None:
            extra += text["decision_extra_irr"].format(irr=irr)
        if lcoe is not None:
            extra += text["decision_extra_lcoe"].format(
                lcoe_text=format_price_per_energy(lcoe, currency_symbol=currency_symbol, language=language)
            )

        return text["decision_attractive"].format(
            payback_years=payback_years,
            simple_roi=simple_roi,
            total_saving_sample=format_currency(total_saving_sample, currency_symbol, language),
            extra=extra,
        )

    if payback_years <= payback_threshold_years:
        return text["decision_payback_ok_roi_mid"].format(payback_years=payback_years)

    return text["decision_positive_but_slow"].format(
        payback_years=payback_years,
        payback_threshold_years=payback_threshold_years,
    )


# ============================================================
# Full integrated report
# ============================================================

def generate_full_report(
    load_metrics: Dict[str, float],
    sample_energy_cost: float,
    annual_energy_cost: Optional[float],
    weighted_average_price: Optional[float],
    throughput_metrics: Optional[Dict[str, float]] = None,
    finance_summary: Optional[Dict[str, object]] = None,
    power_charge_summary: Optional[Dict[str, float]] = None,
    energy_saving_sample: Optional[float] = None,
    power_charge_saving_sample: float = 0.0,
    total_saving_sample: Optional[float] = None,
    max_power_kw: Optional[float] = None,
    currency_symbol: str = "¥",
    language: str = "zh",
) -> Dict[str, str]:
    """
    Generate full report dictionary for UI display.
    """
    load_text = generate_load_summary_text(
        load_metrics=load_metrics,
        max_power_kw=max_power_kw,
        language=language,
    )

    tariff_text = generate_tariff_summary_text(
        sample_energy_cost=sample_energy_cost,
        annual_energy_cost=annual_energy_cost,
        weighted_average_price=weighted_average_price,
        power_charge_summary=power_charge_summary,
        currency_symbol=currency_symbol,
        language=language,
    )

    storage_text = ""
    finance_text = ""
    recommendation_text = ""

    if throughput_metrics is not None and finance_summary is not None and energy_saving_sample is not None:
        storage_text = generate_storage_summary_text(
            throughput_metrics=throughput_metrics,
            energy_saving_sample=energy_saving_sample,
            power_charge_saving_sample=power_charge_saving_sample,
            total_saving_sample=total_saving_sample,
            currency_symbol=currency_symbol,
            language=language,
        )

        finance_text = generate_finance_summary_text(
            finance_summary=finance_summary,
            currency_symbol=currency_symbol,
            language=language,
        )

        recommendation_text = generate_decision_recommendation(
            finance_summary=finance_summary,
            total_saving_sample=0.0 if total_saving_sample is None else total_saving_sample,
            currency_symbol=currency_symbol,
            language=language,
        )

    executive_parts = [load_text, tariff_text]
    if storage_text:
        executive_parts.append(storage_text)
    if finance_text:
        executive_parts.append(finance_text)
    if recommendation_text:
        executive_parts.append(recommendation_text)

    executive_summary = " ".join(part for part in executive_parts if part)

    return {
        "load_summary": load_text,
        "tariff_summary": tariff_text,
        "storage_summary": storage_text,
        "finance_summary": finance_text,
        "recommendation": recommendation_text,
        "executive_summary": executive_summary,
    }


# ============================================================
# Bullet-style key findings
# ============================================================

def generate_key_findings(
    sample_total_cost: float,
    annual_total_cost: Optional[float],
    peak_load_kwh: float,
    max_power_kw: float,
    load_factor: float,
    weighted_average_price: float,
    finance_summary: Optional[Dict[str, object]] = None,
    total_saving_sample: Optional[float] = None,
    currency_symbol: str = "¥",
    language: str = "zh",
) -> List[str]:
    """
    Generate short key findings for dashboard display.
    """
    text = _rt(language)
    findings: List[str] = []

    findings.extend(
        [
            text["finding_sample_total_cost"].format(
                value=format_currency(sample_total_cost, currency_symbol, language)
            ),
            text["finding_annual_total_cost"].format(
                value=format_currency(annual_total_cost, currency_symbol, language)
                if annual_total_cost is not None
                else text["na"]
            ),
            text["finding_peak_load"].format(value=peak_load_kwh),
            text["finding_max_power"].format(value=max_power_kw),
            text["finding_load_factor"].format(value=load_factor),
            text["finding_weighted_avg_price"].format(
                value=format_price_per_energy(weighted_average_price, currency_symbol=currency_symbol, language=language)
            ),
        ]
    )

    if finance_summary is not None and total_saving_sample is not None:
        findings.extend(
            [
                text["finding_storage_saving"].format(
                    value=format_currency(total_saving_sample, currency_symbol, language)
                ),
                text["finding_average_annual_net_benefit"].format(
                    value=format_currency(finance_summary.get("average_annual_net_benefit"), currency_symbol, language)
                ),
                text["finding_payback_years"].format(
                    value=format_years(finance_summary.get("simple_payback_years"), language=language)
                ),
                text["finding_simple_roi"].format(
                    value=format_percentage(finance_summary.get("simple_roi"), language=language)
                ),
                text["finding_irr"].format(
                    value=format_percentage(finance_summary.get("irr"), language=language)
                ),
                text["finding_lcoe"].format(
                    value=format_price_per_energy(finance_summary.get("lcoe"), currency_symbol=currency_symbol, language=language)
                ),
            ]
        )

    return findings