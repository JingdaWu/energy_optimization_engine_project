from __future__ import annotations

import streamlit as st

from core.finance import summarize_finance_from_storage_result
from core.load_analysis import summarize_load_analysis
from core.power_charge import (
    calculate_load_factor_from_max_power,
    calculate_max_power_kw,
    calculate_power_charge,
    compare_power_charge_before_after_storage,
)
from core.report import generate_full_report
from core.storage import summarize_storage_simulation
from core.tariff import (
    apply_manual_five_level_tariff,
    apply_monthly_hour_price_table,
    calculate_five_level_tariff_breakdown,
    calculate_total_energy_cost,
    calculate_weighted_average_price,
    estimate_annual_energy_cost_from_sample,
)
from utils.data_loader import (
    add_time_features,
    ensure_hourly_continuity,
    load_energy_data,
    load_monthly_tariff_table,
    load_storage_parameter_csv,
    load_storage_sample_parameters,
)
from utils.i18n import get_text
from utils.validators import validate_input_dataframe
from visualization.plots import (
    plot_cost_reduction_horizontal_bar,
    plot_hourly_average_load,
    plot_load_curve,
    plot_original_vs_optimized_load,
    plot_storage_operation,
    plot_tariff_cost_share_pie,
    plot_tariff_load_curve,
)


if "language" not in st.session_state:
    st.session_state.language = "en"

language = st.session_state.language
T = get_text(language)

st.set_page_config(
    page_title=T["page_title"],
    page_icon="⚡",
    layout="wide",
)


# ============================================================
# Language state
# ============================================================
def toggle_language() -> None:
    st.session_state.language = "en" if st.session_state.language == "zh" else "zh"


language = st.session_state.language
T = get_text(language)
is_zh = language == "zh"


# ============================================================
# UI style
# ============================================================
UI_COLOR_BORDER_SIDEBAR = "rgba(255,255,255,0.10)"
UI_COLOR_HERO_BG = "linear-gradient(135deg, rgba(0,174,239,0.18), rgba(14,17,23,0.96))"
UI_COLOR_HERO_BORDER = "rgba(0,194,255,0.28)"
UI_COLOR_SECTION_BG = "rgba(255,255,255,0.045)"
UI_COLOR_SECTION_BORDER = "rgba(255,255,255,0.12)"
UI_COLOR_SUMMARY_BG = "linear-gradient(135deg, rgba(0,174,239,0.12), rgba(255,255,255,0.02))"
UI_COLOR_SUMMARY_BORDER = "rgba(0,174,239,0.20)"
UI_COLOR_CHIP_BG = "rgba(0,174,239,0.16)"
UI_COLOR_CHIP_BORDER = "rgba(0,174,239,0.30)"
UI_COLOR_SCENARIO_BG = "rgba(255,255,255,0.03)"
UI_COLOR_SCENARIO_BORDER = "rgba(255,255,255,0.08)"

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2.4rem;
        padding-bottom: 2rem;
        max-width: 1600px;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(255,255,255,0.10);
        overflow-y: auto;
    }

    [data-testid="stSidebarContent"] {
        overflow-y: auto;
        max-height: 100vh;
        padding-bottom: 2rem;
    }

    .hero-card {
        background: linear-gradient(135deg, rgba(0,174,239,0.18), rgba(14,17,23,0.96));
        border: 1px solid rgba(0,194,255,0.28);
        border-radius: 20px;
        padding: 24px 24px 18px 24px;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.18);
    }

    .hero-title {
        font-size: 34px;
        font-weight: 800;
        line-height: 1.15;
        margin-bottom: 6px;
        letter-spacing: 0.2px;
    }

    .hero-subtitle {
        font-size: 15px;
        opacity: 0.86;
        line-height: 1.5;
        margin-bottom: 14px;
    }

    .chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 6px;
    }

    .chip {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
        color: #EAF8FF;
        background: rgba(0,174,239,0.16);
        border: 1px solid rgba(0,174,239,0.30);
    }

    .section-card {
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 16px;
        padding: 14px 14px 10px 14px;
        margin-top: 10px;
        margin-bottom: 10px;
        box-shadow: 0 6px 14px rgba(0,0,0,0.08);
    }

    .section-title {
        font-size: 17px;
        font-weight: 750;
        margin-bottom: 2px;
        color: #F5FBFF;
    }

    .section-desc {
        font-size: 12px;
        opacity: 0.76;
        margin-bottom: 0px;
    }

    .sidebar-title {
        font-size: 22px;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 2px;
        color: #F7FBFF;
    }

    .sidebar-subtitle {
        font-size: 12px;
        opacity: 0.74;
        margin-bottom: 10px;
    }

    .panel-title {
        font-size: 22px;
        font-weight: 800;
        margin: 4px 0 12px 0;
    }

    .panel-subtitle {
        font-size: 13px;
        opacity: 0.74;
        margin-top: -6px;
        margin-bottom: 12px;
    }

    .scenario-bar {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 12px 14px;
        margin-bottom: 14px;
    }

    .scenario-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 10px;
    }

    .scenario-item {
        background: rgba(255,255,255,0.025);
        border-radius: 12px;
        padding: 10px 12px;
        border: 1px solid rgba(255,255,255,0.05);
    }

    .scenario-label {
        font-size: 11px;
        opacity: 0.65;
        text-transform: uppercase;
        letter-spacing: 0.4px;
        margin-bottom: 4px;
    }

    .scenario-value {
        font-size: 14px;
        font-weight: 700;
    }

    .summary-card {
        background: linear-gradient(135deg, rgba(0,174,239,0.12), rgba(255,255,255,0.02));
        border: 1px solid rgba(0,174,239,0.20);
        border-radius: 18px;
        padding: 16px 16px 4px 16px;
        margin-bottom: 14px;
    }

    .summary-title {
        font-size: 18px;
        font-weight: 800;
        margin-bottom: 10px;
    }

    .small-note {
        font-size: 12px;
        opacity: 0.72;
        margin-top: 4px;
        margin-bottom: 0px;
    }

    .empty-state {
        background: rgba(255,255,255,0.02);
        border: 1px dashed rgba(0,194,255,0.25);
        border-radius: 18px;
        padding: 24px 20px;
        margin-top: 10px;
    }

    .empty-title {
        font-size: 22px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .empty-body {
        font-size: 14px;
        opacity: 0.80;
        line-height: 1.7;
    }

    @media (max-width: 1100px) {
        .scenario-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Sidebar helper
# ============================================================

def render_sidebar_section(title: str, desc: str) -> None:
    st.sidebar.markdown(
        f"""
        <div class="section-card">
            <div class="section-title">{title}</div>
            <div class="section-desc">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# Sidebar header
# ============================================================

top_left, top_right = st.sidebar.columns([4, 1])
with top_left:
    st.markdown(
        f"""
        <div class="sidebar-title">{T['sidebar_title']}</div>
        <div class="sidebar-subtitle">{T['sidebar_desc']}</div>
        """,
        unsafe_allow_html=True,
    )
with top_right:
    st.button(T["language_toggle"], on_click=toggle_language, use_container_width=True)


# ============================================================
# Sidebar - data input
# ============================================================

render_sidebar_section(T["section_data_input"], T["section_data_input_desc"])

load_col1, load_col2 = st.sidebar.columns([3, 2])
with load_col1:
    uploaded_load_file = st.file_uploader(
        T["upload_hourly_csv"],
        type=["csv"],
        key="uploaded_load_file",
    )
with load_col2:
    with open("data/sample_load.csv", "rb") as f:
        st.download_button(
            label=T["download_template"],
            data=f,
            file_name="sample_load.csv",
            mime="text/csv",
            use_container_width=True,
        )


# ============================================================
# Sidebar - tariff config
# ============================================================

render_sidebar_section(T["section_tariff"], T["section_tariff_desc"])

if "tariff_mode_radio" not in st.session_state:
    st.session_state.tariff_mode_radio = T["value_manual"]

tariff_mode_label = st.sidebar.radio(
    T["label_tariff_mode"],
    options=[T["value_manual"], T["value_table"]],
    key="tariff_mode_radio",
    horizontal=True,
)

tariff_mode = "manual" if tariff_mode_label == T["value_manual"] else "table"

monthly_tariff_table_df = None
uploaded_tariff_table = None

if tariff_mode == "manual":
    critical_peak_price = st.sidebar.number_input(
        T["critical_peak_price"],
        min_value=0.0,
        value=2.00,
        step=0.01,
    )
    peak_price = st.sidebar.number_input(
        T["peak_price"],
        min_value=0.0,
        value=1.70,
        step=0.01,
    )
    flat_price = st.sidebar.number_input(
        T["flat_price"],
        min_value=0.0,
        value=1.00,
        step=0.01,
    )
    valley_price = st.sidebar.number_input(
        T["valley_price"],
        min_value=0.0,
        value=0.30,
        step=0.01,
    )
    super_valley_price = st.sidebar.number_input(
        T["super_valley_price"],
        min_value=0.0,
        value=0.10,
        step=0.01,
    )

    hour_options = [(i, f"{i}~{i+1}") for i in range(24)]
    hour_ids = [h[0] for h in hour_options]
    hour_labels = {h[0]: h[1] for h in hour_options}

    critical_peak_hours = st.sidebar.multiselect(
        T["critical_peak_hours"],
        options=hour_ids,
        default=[18, 19],
        format_func=lambda x: hour_labels[x],
    )
    peak_hours = st.sidebar.multiselect(
        T["peak_hours"],
        options=hour_ids,
        default=[16, 17, 20, 21],
        format_func=lambda x: hour_labels[x],
    )
    flat_hours = st.sidebar.multiselect(
        T["flat_hours"],
        options=hour_ids,
        default=[7, 8, 9, 10, 11, 12, 13, 14, 15, 22],
        format_func=lambda x: hour_labels[x],
    )
    valley_hours = st.sidebar.multiselect(
        T["valley_hours"],
        options=hour_ids,
        default=[5, 6, 23],
        format_func=lambda x: hour_labels[x],
    )
    super_valley_hours = st.sidebar.multiselect(
        T["super_valley_hours"],
        options=hour_ids,
        default=[0, 1, 2, 3, 4],
        format_func=lambda x: hour_labels[x],
    )
else:
    tariff_col1, tariff_col2 = st.sidebar.columns([3, 2])
    with tariff_col1:
        uploaded_tariff_table = st.file_uploader(
            T["upload_tariff_table"],
            type=["csv"],
            key="uploaded_tariff_table",
        )
    with tariff_col2:
        with open("data/monthly_tariff_template.csv", "rb") as f:
            st.download_button(
                label=T["tariff_template_download"],
                data=f,
                file_name="monthly_tariff_template.csv",
                mime="text/csv",
                use_container_width=True,
            )


# ============================================================
# Sidebar - power charge config
# ============================================================

render_sidebar_section(T["section_power"], T["section_power_desc"])

if "power_charge_mode_radio" not in st.session_state:
    st.session_state.power_charge_mode_radio = T["value_capacity"]

power_charge_mode_label = st.sidebar.radio(
    T["label_power_mode"],
    options=[T["value_capacity"], T["value_demand"]],
    key="power_charge_mode_radio",
    horizontal=True,
)

power_charge_mode = "capacity" if power_charge_mode_label == T["value_capacity"] else "demand"

capacity_price_per_kw = 0.0
contract_buffer_ratio = 0.0
demand_price_per_kw = 0.0

if power_charge_mode == "capacity":
    capacity_price_per_kw = st.sidebar.number_input(
        T["capacity_price_per_kw"],
        min_value=0.0,
        value=25.0,
        step=1.0,
    )
    contract_buffer_ratio_percent = st.sidebar.slider(
        T["contract_buffer_ratio"],
        min_value=0,
        max_value=100,
        value=10,
        step=1,
        format="%d%%",
    )
    contract_buffer_ratio = contract_buffer_ratio_percent / 100
else:
    demand_price_per_kw = st.sidebar.number_input(
        T["demand_price_per_kw"],
        min_value=0.0,
        value=35.0,
        step=1.0,
    )


# ============================================================
# Sidebar - storage config
# ============================================================

render_sidebar_section(T["section_storage"], T["section_storage_desc"])

if "use_storage_mode_radio" not in st.session_state:
    st.session_state.use_storage_mode_radio = T["value_disabled"]

use_storage_label = st.sidebar.radio(
    T["label_storage_mode"],
    options=[T["value_disabled"], T["value_enabled"]],
    key="use_storage_mode_radio",
    horizontal=True,
)

use_storage = use_storage_label == T["value_enabled"]

storage_params = None
uploaded_storage_file = None

if use_storage:
    storage_input_mode = st.sidebar.radio(
        T["storage_input_mode"],
        options=[
            T["storage_manual"],
            T["storage_upload"],
            T["storage_sample"],
        ],
        index=0,
    )

    if storage_input_mode == T["storage_manual"]:
        storage_capacity_kwh = st.sidebar.number_input(
            T["storage_capacity"],
            min_value=1.0,
            value=2000.0,
            step=100.0,
        )
        storage_power_kw = st.sidebar.number_input(
            T["storage_power"],
            min_value=1.0,
            value=1000.0,
            step=50.0,
        )

        charge_efficiency_percent = st.sidebar.slider(
            T["charge_efficiency"],
            min_value=50,
            max_value=100,
            value=95,
            step=1,
            format="%d%%",
        )
        discharge_efficiency_percent = st.sidebar.slider(
            T["discharge_efficiency"],
            min_value=50,
            max_value=100,
            value=95,
            step=1,
            format="%d%%",
        )
        min_soc_ratio_percent = st.sidebar.slider(
            T["min_soc_ratio"],
            min_value=0,
            max_value=100,
            value=10,
            step=1,
            format="%d%%",
        )
        max_soc_ratio_percent = st.sidebar.slider(
            T["max_soc_ratio"],
            min_value=0,
            max_value=100,
            value=100,
            step=1,
            format="%d%%",
        )

        charge_efficiency = charge_efficiency_percent / 100
        discharge_efficiency = discharge_efficiency_percent / 100
        min_soc_ratio = min_soc_ratio_percent / 100
        max_soc_ratio = max_soc_ratio_percent / 100

        capex_total = st.sidebar.number_input(
            T["capex_total"],
            min_value=0.0,
            value=1500000.0,
            step=10000.0,
        )
        annual_om_cost = st.sidebar.number_input(
            T["annual_om_cost"],
            min_value=0.0,
            value=80000.0,
            step=1000.0,
        )
        project_years = st.sidebar.number_input(
            T["project_years"],
            min_value=1,
            value=10,
            step=1,
        )

        discount_rate_percent = st.sidebar.slider(
            T["discount_rate"],
            min_value=0,
            max_value=30,
            value=5,
            step=1,
            format="%d%%",
        )
        discount_rate = discount_rate_percent / 100

        annual_degradation_rate_percent = st.sidebar.slider(
            T["annual_degradation_rate"],
            min_value=0.0,
            max_value=10.0,
            value=2.0,
            step=0.1,
            format="%.1f%%",
        )
        annual_degradation_rate = annual_degradation_rate_percent / 100

        storage_params = {
            "storage_capacity_kwh": storage_capacity_kwh,
            "storage_power_kw": storage_power_kw,
            "charge_efficiency": charge_efficiency,
            "discharge_efficiency": discharge_efficiency,
            "min_soc_ratio": min_soc_ratio,
            "max_soc_ratio": max_soc_ratio,
            "capex_total": capex_total,
            "annual_om_cost": annual_om_cost,
            "project_years": int(project_years),
            "discount_rate": discount_rate,
            "annual_degradation_rate": annual_degradation_rate,
        }

    elif storage_input_mode == T["storage_upload"]:
        storage_col1, storage_col2 = st.sidebar.columns([3, 2])
        with storage_col1:
            uploaded_storage_file = st.file_uploader(
                T["upload_storage_csv"],
                type=["csv"],
                key="uploaded_storage_file",
            )
        with storage_col2:
            with open("data/storage_params_template.csv", "rb") as f:
                st.download_button(
                    label=T["storage_template_download"],
                    data=f,
                    file_name="storage_params_template.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

        if uploaded_storage_file is not None:
            storage_params = load_storage_parameter_csv(uploaded_storage_file)

    else:
        storage_sample_choice = st.sidebar.selectbox(
            T["storage_sample_select"],
            options=["storage_sample_1", "storage_sample_2", "storage_sample_3"],
            index=1,
        )

        sample_path_map = {
            "storage_sample_1": "data/storage_sample_1.csv",
            "storage_sample_2": "data/storage_sample_2.csv",
            "storage_sample_3": "data/storage_sample_3.csv",
        }
        storage_params = load_storage_sample_parameters(sample_path_map[storage_sample_choice])


# ============================================================
# Sidebar - run button
# ============================================================

st.sidebar.markdown("")
st.sidebar.markdown(
    f"""
    <div class="small-note">{T['run_hint']}</div>
    """,
    unsafe_allow_html=True,
)
run_button = st.sidebar.button(T["run_button_new"], type="primary", use_container_width=True)


# ============================================================
# Hero area
# ============================================================

st.markdown(
    f"""
    <div class="hero-card">
        <div class="hero-title">{T['app_name']}</div>
        <div class="hero-subtitle">{T['app_subtitle']}</div>
        <div class="chip-row">
            {''.join([
                f"<span class='chip'>{chip}</span>"
                for chip in [
                    T["chip_tou_tariff_analysis"],
                    T["chip_power_charge_evaluation"],
                    T["chip_storage_arbitrage"],
                    T["chip_financial_metrics"],
                ]
            ])}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(T["app_caption"])


# ============================================================
# Scenario summary
# ============================================================

scenario_tariff = T["value_manual"] if tariff_mode == "manual" else T["value_table"]
scenario_power = T["value_capacity"] if power_charge_mode == "capacity" else T["value_demand"]
scenario_storage = T["value_enabled"] if use_storage else T["value_disabled"]
scenario_data = T["value_uploaded"] if uploaded_load_file is not None else T["value_not_uploaded"]

st.markdown(
    f"""
    <div class="scenario-bar">
        <div class="section-title" style="margin-bottom:10px;">{T['scenario_summary']}</div>
        <div class="scenario-grid">
            <div class="scenario-item">
                <div class="scenario-label">{T['label_tariff_mode']}</div>
                <div class="scenario-value">{scenario_tariff}</div>
            </div>
            <div class="scenario-item">
                <div class="scenario-label">{T['label_power_mode']}</div>
                <div class="scenario-value">{scenario_power}</div>
            </div>
            <div class="scenario-item">
                <div class="scenario-label">{T['label_storage_mode']}</div>
                <div class="scenario-value">{scenario_storage}</div>
            </div>
            <div class="scenario-item">
                <div class="scenario-label">{T['label_data_status']}</div>
                <div class="scenario-value">{scenario_data}</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Main pipeline execution
# ============================================================

if run_button:
    try:
        # ------------------------------------------------------------
        # Step 1: Load load-profile data
        # ------------------------------------------------------------
        if uploaded_load_file is None:
            st.warning(T["need_upload_first"])
            st.stop()

        raw_df = load_energy_data(uploaded_load_file)
        validate_input_dataframe(raw_df)
        raw_df = add_time_features(raw_df)
        ensure_hourly_continuity(raw_df)

        # ------------------------------------------------------------
        # Step 2: Load analysis
        # ------------------------------------------------------------
        load_analysis = summarize_load_analysis(raw_df)
        base_max_power_kw = calculate_max_power_kw(raw_df, load_column="load_kwh")
        base_load_factor = calculate_load_factor_from_max_power(raw_df, load_column="load_kwh")

        # ------------------------------------------------------------
        # Step 3: Tariff assignment
        # ------------------------------------------------------------
        annual_energy_cost = None
        tariff_breakdown_df = None

        if tariff_mode == "manual":
            tariff_df = apply_manual_five_level_tariff(
                df=raw_df,
                critical_peak_hours=critical_peak_hours,
                peak_hours=peak_hours,
                flat_hours=flat_hours,
                valley_hours=valley_hours,
                super_valley_hours=super_valley_hours,
                critical_peak_price=critical_peak_price,
                peak_price=peak_price,
                flat_price=flat_price,
                valley_price=valley_price,
                super_valley_price=super_valley_price,
            )

            sample_energy_cost = calculate_total_energy_cost(tariff_df, cost_column="energy_cost")
            weighted_average_price = calculate_weighted_average_price(
                tariff_df,
                load_column="load_kwh",
                price_column="price",
            )
            tariff_breakdown_df = calculate_five_level_tariff_breakdown(
                tariff_df,
                tariff_period_column="tariff_period",
                load_column="load_kwh",
                price_column="price",
                cost_column="energy_cost",
            )

            sample_days = len(tariff_df) / 24.0
            annual_energy_cost = sample_energy_cost / sample_days * 365 if sample_days > 0 else None

        else:
            if uploaded_tariff_table is None:
                st.warning(T["need_tariff_upload_first"])
                st.stop()

            monthly_tariff_table_df = load_monthly_tariff_table(uploaded_tariff_table)

            tariff_df = apply_monthly_hour_price_table(
                df=raw_df,
                price_table_df=monthly_tariff_table_df,
                time_column="time",
                output_price_column="price",
                output_label_column="tariff_period",
            )

            sample_energy_cost = calculate_total_energy_cost(tariff_df, cost_column="energy_cost")
            weighted_average_price = calculate_weighted_average_price(
                tariff_df,
                load_column="load_kwh",
                price_column="price",
            )

            annual_tariff_estimation = estimate_annual_energy_cost_from_sample(
                load_df=raw_df,
                monthly_price_table_df=monthly_tariff_table_df,
                time_column="time",
                load_column="load_kwh",
            )
            annual_energy_cost = annual_tariff_estimation["annual_total_energy_cost"]

            tariff_breakdown_df = (
                tariff_df.groupby("hour", as_index=False)
                .agg(
                    total_load_kwh=("load_kwh", "sum"),
                    avg_price=("price", "mean"),
                    total_cost=("energy_cost", "sum"),
                )
                .rename(columns={"hour": "tariff_period"})
            )

        # ------------------------------------------------------------
        # Step 4: Power charge before storage
        # ------------------------------------------------------------
        power_charge_summary = calculate_power_charge(
            df=raw_df,
            mode=power_charge_mode,
            load_column="load_kwh",
            capacity_price_per_kw=capacity_price_per_kw,
            contract_buffer_ratio=contract_buffer_ratio,
            demand_price_per_kw=demand_price_per_kw,
        )

        sample_total_cost = float(sample_energy_cost + power_charge_summary["power_charge"])

        annual_total_cost = None
        if annual_energy_cost is not None:
            annual_total_cost = float(annual_energy_cost + power_charge_summary["power_charge"] * 12)

        # ------------------------------------------------------------
        # Step 5: Optional storage simulation
        # ------------------------------------------------------------
        storage_result_df = None
        storage_throughput_metrics = None
        finance_summary = None
        storage_report_dict = None
        total_saving_sample = None
        optimized_total_cost_sample = None
        optimized_power_charge_summary = None
        power_charge_compare = None
        energy_saving_sample = None
        power_charge_saving_sample = None
        saving_ratio = None
        peak_reduction_kw = None

        if use_storage:
            if storage_params is None:
                st.warning(T["need_storage_upload_first"])
                st.stop()

            # ============================================================
            # 2026-04-19: Updated storage dispatch call.
            # This version uses daily planning first, then executes:
            # - charge priority: super_valley -> valley
            # - discharge priority: critical_peak -> peak
            # - charge power is capped by the original max grid power
            #   to reduce the risk of raising demand/capacity charges
            # - initial SOC changed from full SOC to min SOC
            # ============================================================
            # ============================================================
            # 2026-04-19: Updated storage call for full-horizon offline planning.
            # The storage optimizer now reads the full uploaded horizon and
            # performs one global planning pass before dispatch.
            # ============================================================
            storage_summary = summarize_storage_simulation(
                df=tariff_df,
                storage_capacity_kwh=storage_params["storage_capacity_kwh"],
                storage_power_kw=storage_params["storage_power_kw"],
                charge_efficiency=storage_params["charge_efficiency"],
                discharge_efficiency=storage_params["discharge_efficiency"],
                initial_soc_ratio=storage_params["min_soc_ratio"],
                min_soc_ratio=storage_params["min_soc_ratio"],
                max_soc_ratio=storage_params["max_soc_ratio"],
                charge_periods=["super_valley", "valley"],
                discharge_periods=["critical_peak", "peak"],
                demand_limit_kw=base_max_power_kw,
            )

            storage_result_df = storage_summary["result_df"]
            storage_throughput_metrics = storage_summary["throughput_metrics"]

            energy_saving_sample = float(storage_summary["revenue_metrics"]["total_saving"])

            power_charge_compare = compare_power_charge_before_after_storage(
                original_df=tariff_df,
                optimized_df=storage_result_df,
                mode=power_charge_mode,
                original_load_column="load_kwh",
                optimized_load_column="net_load_kwh",
                capacity_price_per_kw=capacity_price_per_kw,
                contract_buffer_ratio=contract_buffer_ratio,
                demand_price_per_kw=demand_price_per_kw,
            )

            optimized_power_charge_summary = {
                "mode": power_charge_mode,
                "max_power_kw": power_charge_compare["optimized_max_power_kw"],
                "power_charge": power_charge_compare["optimized_power_charge"],
            }
            if power_charge_mode == "capacity":
                optimized_power_charge_summary["contract_capacity_kw"] = power_charge_compare["optimized_contract_capacity_kw"]

            power_charge_saving_sample = float(power_charge_compare["power_charge_saving"])
            total_saving_sample = float(energy_saving_sample + power_charge_saving_sample)
            optimized_total_cost_sample = float(sample_total_cost - total_saving_sample)

            if sample_total_cost > 0:
                saving_ratio = total_saving_sample / sample_total_cost

            peak_reduction_kw = float(
                power_charge_compare["original_max_power_kw"] - power_charge_compare["optimized_max_power_kw"]
            )

            finance_summary = summarize_finance_from_storage_result(
                total_sample_saving=total_saving_sample,
                sample_row_count=len(storage_result_df),
                capex_total=storage_params["capex_total"],
                annual_om_cost=storage_params["annual_om_cost"],
                project_years=storage_params["project_years"],
                discount_rate=storage_params["discount_rate"],
                annual_degradation_rate=storage_params["annual_degradation_rate"],
                total_sample_discharge_kwh=storage_throughput_metrics["total_discharge_kwh"],
                include_irr=True,
            )

            storage_report_dict = generate_full_report(
                load_metrics=load_analysis["basic_metrics"],
                sample_energy_cost=sample_energy_cost,
                annual_energy_cost=annual_energy_cost,
                weighted_average_price=weighted_average_price,
                throughput_metrics=storage_throughput_metrics,
                finance_summary=finance_summary,
                power_charge_summary=power_charge_summary,
                energy_saving_sample=energy_saving_sample,
                power_charge_saving_sample=power_charge_saving_sample,
                total_saving_sample=total_saving_sample,
                max_power_kw=base_max_power_kw,
                language=language,
            )
        else:
            storage_report_dict = generate_full_report(
                load_metrics=load_analysis["basic_metrics"],
                sample_energy_cost=sample_energy_cost,
                annual_energy_cost=annual_energy_cost,
                weighted_average_price=weighted_average_price,
                power_charge_summary=power_charge_summary,
                max_power_kw=base_max_power_kw,
                language=language,
            )

        # ============================================================
        # Output header
        # ============================================================

        st.success(T["analysis_done"])

        # ------------------------------------------------------------
        # Section A: Decision KPIs
        # ------------------------------------------------------------
        st.markdown(f"<div class='panel-title'>{T['key_metrics']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='panel-subtitle'>{T['kpi_desc']}</div>", unsafe_allow_html=True)

        if use_storage and finance_summary is not None and total_saving_sample is not None:
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            kpi1.metric(
                T["annual_total_cost"],
                T["not_available"] if annual_total_cost is None else f"¥{annual_total_cost:,.2f}",
            )
            kpi2.metric(
                T["average_annual_net_benefit"],
                f"¥{finance_summary['average_annual_net_benefit']:,.2f}",
            )
            payback_value = finance_summary["simple_payback_years"]
            kpi3.metric(
                T["payback_years"],
                T["not_available"] if payback_value is None else f"{payback_value:.2f} ",
            )
            irr_value = finance_summary["irr"]
            kpi4.metric(
                T["irr"],
                T["not_available"] if irr_value is None else f"{irr_value:.2%}",
            )

            kpi5, kpi6, kpi7, kpi8 = st.columns(4)
            roi_value = finance_summary["simple_roi"]
            lcoe_value = finance_summary["lcoe"]
            kpi5.metric(
                T["storage_saving"],
                f"¥{total_saving_sample:,.2f}",
            )
            kpi6.metric(
                T["simple_roi"],
                T["not_available"] if roi_value is None else f"{roi_value:.2%}",
            )
            kpi7.metric(
                T["lcoe"],
                T["not_available"] if lcoe_value is None else f"¥{lcoe_value:,.4f}/kWh",
            )
            kpi8.metric(
                T["weighted_avg_price"],
                f"¥{weighted_average_price:,.4f}/kWh",
            )
        else:
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            kpi1.metric(T["sample_total_cost"], f"¥{sample_total_cost:,.2f}")
            kpi2.metric(
                T["annual_total_cost"],
                T["not_available"] if annual_total_cost is None else f"¥{annual_total_cost:,.2f}",
            )
            kpi3.metric(T["peak_load"], f"{load_analysis['basic_metrics']['peak_load_kwh']:,.2f} kWh")
            kpi4.metric(T["weighted_avg_price"], f"¥{weighted_average_price:,.4f}/kWh")

        st.markdown(f"<div class='panel-subtitle'>{T['oper_desc']}</div>", unsafe_allow_html=True)
        op1, op2, op3, op4 = st.columns(4)
        op1.metric(T["max_power"], f"{base_max_power_kw:,.2f} kW")
        op2.metric(T["load_factor"], f"{base_load_factor:.2%}")
        op3.metric(T["sample_total_cost"], f"¥{sample_total_cost:,.2f}")
        op4.metric(T["peak_load"], f"{load_analysis['basic_metrics']['peak_load_kwh']:,.2f} kWh")

        # ------------------------------------------------------------
        # Section B: Before vs After summary
        # ------------------------------------------------------------
        if use_storage and total_saving_sample is not None and optimized_total_cost_sample is not None:
            st.markdown(
                f"""
                <div class="summary-card">
                    <div class="summary-title">{T['before_after_overview']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            bf1, bf2, bf3, bf4 = st.columns(4)
            bf1.metric(T["before_storage"], f"¥{sample_total_cost:,.2f}")
            bf2.metric(T["after_storage"], f"¥{optimized_total_cost_sample:,.2f}")
            bf3.metric(T["storage_saving"], f"¥{total_saving_sample:,.2f}")
            bf4.metric(
                T["saving_ratio"],
                T["not_available"] if saving_ratio is None else f"{saving_ratio:.2%}",
            )

            bf5, bf6, bf7, bf8 = st.columns(4)
            bf5.metric(
                T["energy_saving"],
                f"¥{energy_saving_sample:,.2f}" if energy_saving_sample is not None else T["not_available"],
            )
            bf6.metric(
                T["power_charge_saving"],
                f"¥{power_charge_saving_sample:,.2f}" if power_charge_saving_sample is not None else T["not_available"],
            )
            bf7.metric(
                T["peak_reduction"],
                T["not_available"] if peak_reduction_kw is None else f"{peak_reduction_kw:,.2f} kW",
            )
            bf8.metric(
                T["optimized_max_power"],
                T["not_available"]
                if optimized_power_charge_summary is None
                else f"{optimized_power_charge_summary['max_power_kw']:,.2f} kW",
            )

        # ------------------------------------------------------------
        # Section C: Charts
        # ------------------------------------------------------------
        st.subheader(T["load_analysis"])
        load_left, load_right = st.columns(2)

        fig_load_curve = plot_load_curve(
            raw_df,
            title=T["factory_load_curve"],
            xaxis_title=T["time"],
            yaxis_title=T["load_kwh_axis"],
        )
        with load_left:
            st.plotly_chart(fig_load_curve, use_container_width=True)

        fig_hourly_avg = plot_hourly_average_load(
            load_analysis["hourly_profile"],
            title=T["avg_load_by_hour"],
            xaxis_title=T["hour_of_day"],
            yaxis_title=T["avg_load_kwh_axis"],
        )
        with load_right:
            st.plotly_chart(fig_hourly_avg, use_container_width=True)

        st.subheader(T["tariff_analysis"])
        tariff_left, tariff_right = st.columns([1.35, 1])

        fig_tariff_load = plot_tariff_load_curve(
            tariff_df,
            title=T["load_with_price"],
            xaxis_title=T["time"],
            yaxis_title_left=T["load_kwh_axis"],
            yaxis_title_right=T["price_axis"],
        )
        with tariff_left:
            st.plotly_chart(fig_tariff_load, use_container_width=True)

        with tariff_right:
            if tariff_mode == "manual":
                tariff_breakdown_df_plot = tariff_breakdown_df.copy()

                tariff_period_label_map = {
                    "critical_peak": "尖峰" if language == "zh" else "Critical Peak",
                    "peak": "峰" if language == "zh" else "Peak",
                    "flat": "平" if language == "zh" else "Flat",
                    "valley": "谷" if language == "zh" else "Valley",
                    "super_valley": "深谷" if language == "zh" else "Super Valley",
                }

                tariff_breakdown_df_plot["tariff_period"] = (
                    tariff_breakdown_df_plot["tariff_period"]
                    .astype(str)
                    .str.lower()
                    .map(tariff_period_label_map)
                    .fillna(tariff_breakdown_df_plot["tariff_period"])
                )

                fig_tariff_breakdown = plot_tariff_cost_share_pie(
                    tariff_breakdown_df_plot,
                    label_column="tariff_period",
                    value_column="total_cost",
                    title=T["tariff_share_pie"],
                )
                st.plotly_chart(fig_tariff_breakdown, use_container_width=True)
            else:
                st.dataframe(tariff_breakdown_df.head(24), use_container_width=True)

        if use_storage and storage_result_df is not None:
            st.subheader(T["storage_operation"])

            storage_row1_left, storage_row1_right = st.columns(2)

            fig_optimized_load = plot_original_vs_optimized_load(
                storage_result_df,
                title=T["optimized_load_chart"],
                xaxis_title=T["time"],
                yaxis_title=T["load_kwh_axis"],
            )
            with storage_row1_left:
                st.plotly_chart(fig_optimized_load, use_container_width=True)

            fig_storage_op = plot_storage_operation(
                storage_result_df,
                title=T["storage_soc_chart"],
                xaxis_title=T["time"],
                yaxis_title_left=T["charge_discharge_axis"],
                yaxis_title_right=T["soc_axis"],
            )
            with storage_row1_right:
                st.plotly_chart(fig_storage_op, use_container_width=True)

            fig_cost_reduce = plot_cost_reduction_horizontal_bar(
                original_cost=sample_total_cost,
                optimized_cost=optimized_total_cost_sample,
                title=T["cost_reduction_chart"],
                xaxis_title=T["relative_cost_axis"],
                original_label=T["before_storage"],
                optimized_label=T["after_storage"],
            )
            st.plotly_chart(fig_cost_reduce, use_container_width=True)

        # ------------------------------------------------------------
        # Section D: Conclusion
        # ------------------------------------------------------------
        st.subheader(T["auto_conclusion"])

        st.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-title">{T['executive_summary']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if use_storage:
            executive_summary_text = (
                f"{storage_report_dict['recommendation']}\n\n"
                f"{storage_report_dict['finance_summary']}"
            )
        else:
            executive_summary_text = (
                f"{storage_report_dict['tariff_summary']}\n\n"
                f"{storage_report_dict['load_summary']}"
            )

        st.info(executive_summary_text)

        st.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-title">{T['detailed_insights']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

                # ============================================================
        # MODIFIED 2026-04-21: 2x2 aligned insight layout
        # Top-left: load summary
        # Top-right: tariff summary
        # Bottom-left: storage summary
        # Bottom-right: finance summary
        # ============================================================
        insight_row1_col1, insight_row1_col2 = st.columns(2)
        insight_row2_col1, insight_row2_col2 = st.columns(2)

        with insight_row1_col1:
            st.markdown(f"**{T['load_summary']}**")
            st.write(storage_report_dict["load_summary"])

        with insight_row1_col2:
            st.markdown(f"**{T['tariff_summary']}**")
            st.write(storage_report_dict["tariff_summary"])

        if use_storage:
            with insight_row2_col1:
                st.markdown(f"**{T['storage_summary']}**")
                st.write(storage_report_dict["storage_summary"])

            with insight_row2_col2:
                st.markdown(f"**{T['finance_summary']}**")
                st.write(storage_report_dict["finance_summary"])

        # ------------------------------------------------------------
        # Section E: Detailed table
        # ------------------------------------------------------------
        with st.expander(T["detailed_result_table"], expanded=False):
            st.caption(T["detailed_result_table_hint"])
            if tariff_breakdown_df is not None:
                st.markdown(f"**{T['tariff_breakdown']}**")
                st.dataframe(tariff_breakdown_df, use_container_width=True)

            if use_storage and storage_result_df is not None:
                st.markdown(f"**{T['storage_result_preview']}**")
                st.dataframe(storage_result_df.head(50), use_container_width=True)
            else:
                st.markdown(f"**{T['tariff_result_preview']}**")
                st.dataframe(tariff_df.head(50), use_container_width=True)

    except Exception as e:
        st.error(f"{T['simulation_failed']}: {e}")

else:
    st.markdown(
        f"""
        <div class="empty-state">
            <div class="empty-title">{T['empty_title']}</div>
            <div class="empty-body">{T['empty_body']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )