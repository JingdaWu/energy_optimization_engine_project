from __future__ import annotations


# ============================================================
# Translation dictionary
# ============================================================

TRANSLATIONS = {
    "zh": {
        "page_title": "能源调优引擎",
        "sidebar_title": "能源调优引擎",
        "sidebar_desc": "面向数据中心与数字基础设施的经济性分析决策助手",
        "language_toggle": "English",
        "data_source": "能耗负荷",
        "upload_csv": "上传数据",
        "download_template": "下载模板",
        "upload_hourly_csv": "点击下方按钮上传数据",
        "tariff_mode": "电价",
        "manual_tariff": "手动输入",
        "table_tariff": "上传电价表",
        "upload_tariff_table": "上传全年各时段电价表",
        "tariff_template_download": "下载模板",
        "tariff_settings": "输入分时电价",
        "critical_peak_price": "尖峰电价 (¥/kWh)",
        "peak_price": "峰电价 (¥/kWh)",
        "flat_price": "平电价 (¥/kWh)",
        "valley_price": "谷电价 (¥/kWh)",
        "super_valley_price": "深谷电价 (¥/kWh)",
        "critical_peak_hours": "尖峰时段",
        "peak_hours": "峰时段",
        "flat_hours": "平时段",
        "valley_hours": "谷时段",
        "super_valley_hours": "深谷时段",
        "power_charge_mode": "功率电费计费方式",
        "capacity_charge": "容量计费",
        "demand_charge": "需量计费",
        "capacity_price_per_kw": "容量电费 (¥/kW)",
        "contract_buffer_ratio": "预估最高功率-契约功率缓冲区 (%)",
        "demand_price_per_kw": "需量电费 (¥/kW)",
        "use_storage": "储能系统",
        "without_storage": "不应用",
        "with_storage": "应用",
        "storage_input_mode": "设备参数",
        "storage_manual": "手动输入",
        "storage_upload": "上传参数表",
        "storage_sample": "使用样品参数",
        "upload_storage_csv": "上传储能设备参数表格",
        "storage_template_download": "下载模板",
        "storage_sample_select": "选择样品型号",
        "storage_settings": "输入设备参数",
        "storage_capacity": "储能设备容量 (kWh)",
        "storage_power": "储能设备功率 (kW)",
        "charge_efficiency": "充电效率 (%)",
        "discharge_efficiency": "放电效率 (%)",
        "min_soc_ratio": "截止放电SOC (%)",
        "max_soc_ratio": "截止充电SOC (%)",
        "capex_total": "CAPEX (¥)",
        "annual_om_cost": "年运维成本 (¥)",
        "project_years": "设备使用年限 (年)",
        "discount_rate": "折现率 (%)",
        "annual_degradation_rate": "设备年容量衰减率 (%)",
        "run_simulation": "开始分析",
        "title": "能源调优引擎",
        "caption": "面向数据中心与数字基础设施的经济性分析决策助手",
        "need_upload_first": "请上传数据中心或数字基础设施各时段的能耗负荷数据",
        "need_tariff_upload_first": "请上传数据中心或数字基础设施所在地区全年各时段电价表",
        "need_storage_upload_first": "请上传拟引入储能系统的参数数据表格",
        "simulation_success": "分析完成",
        "simulation_failed": "分析失败 (有数据未被输入)",
        "click_to_start": "请先在左侧数据输入栏输入各项参数，然后点击“开始分析”输出经济性分析与决策报告",
        "key_metrics": "分析指标",
        "sample_total_cost": "电费支出 (输入样品负荷周期内)",
        "annual_total_cost": "电费支出 (全年)",
        "peak_load": "峰值负荷",
        "max_power": "最大功率",
        "load_factor": "电网负荷率",
        "weighted_avg_price": "加权平均电价",
        "storage_saving": "引入储能系统收益 (输入样品负荷周期内)",
        "average_annual_net_benefit": "引入储能系统收益 (全年)",
        "payback_years": "回本周期",
        "simple_roi": "投资回报率 (ROI)",
        "irr": "内部到期收益率 (IRR)",
        "lcoe": "平准化能源成本 (LCOE)",
        "load_analysis": "负荷分析",
        "tariff_analysis": "电价分析",
        "storage_operation": "储能系统运行状态分析",
        "auto_conclusion": "分析结论",
        "load_summary": "负荷相关",
        "tariff_summary": "电价相关",
        "storage_summary": "储能系统运行状态相关",
        "finance_summary": "经济性相关",
        "recommendation": "决策建议",
        "result_preview": "分析数据一览",
        "not_available": "N/A",
        "factory_load_curve": "数据中心或数字基础设施的负荷时间序列矩阵",
        "avg_load_by_hour": "分时平均负荷",
        "load_with_price": "负荷/电价时间序列矩阵",
        "tariff_share_pie": "电价支出占比",
        "storage_soc_chart": "储能系统运行状态与SOC的时间序列矩阵",
        "optimized_load_chart": "引入储能系统前后电网负荷状态对比",
        "cost_reduction_chart": "引入储能系统前后电费支出对比",
        "time": "日期与时段",
        "hour_of_day": "时段",
        "load_kwh_axis": "负荷 (kWh)",
        "avg_load_kwh_axis": "平均负荷 (kWh)",
        "price_axis": "电价 (¥/kWh)",
        "tariff_period_axis": "电价时段",
        "cost_axis": "支出 (¥)",
        "charge_discharge_axis": "充放电量 (kWh)",
        "soc_axis": "储能系统SOC (kWh)",
        "relative_cost_axis": "电费支出占比 (%)",
        "before_storage": "引入储能系统前",
        "after_storage": "引入储能系统后",

        "app_name": "能源调优引擎",  #新
        "app_subtitle": "面向高能耗工厂与储能场景的电费分析、削峰套利与经济性决策支持平台",  #新
        "app_caption": "用于能源成本优化、储能评估与管理层决策支持的科技风演示工具。",  #新

        "chip_tou_tariff_analysis": "分时电价分析",  #新
        "chip_power_charge_evaluation": "功率电费评估",  #新
        "chip_storage_arbitrage": "储能套利仿真",  #新
        "chip_financial_metrics": "经济性指标",  #新

        "section_data_input": "负荷数据上传", 
        "section_data_input_desc": "上传数据中心或数字基础设施各时段能耗负荷",  
        "section_tariff": "电价配置",  #新
        "section_tariff_desc": "选择分时电价模式并配置价格参数。",  #新
        "section_power": "功率电费配置",  #新
        "section_power_desc": "设置容量或需量计费方式。",  #新
        "section_storage": "储能配置",  #新
        "section_storage_desc": "选择是否启用储能，并定义系统参数。",  #新

        "scenario_summary": "当前场景摘要",  #新
        "executive_summary": "执行摘要",  #新
        "detailed_insights": "详细解读",  #新
        "before_after_overview": "优化前后对比",  #新
        "detailed_result_table": "详细结果表",  #新
        "detailed_result_table_hint": "以下表格用于工程复核与明细查看。",  #新

        "label_tariff_mode": "电价模式",  #新
        "label_power_mode": "功率计费",  #新
        "label_storage_mode": "储能状态",  #新
        "label_data_status": "数据状态",  #新

        "value_uploaded": "已上传",  #新
        "value_not_uploaded": "未上传",  #新
        "value_enabled": "启用",  #新
        "value_disabled": "关闭",  #新
        "value_manual": "手动分时",  #新
        "value_table": "月度价格表",  #新
        "value_capacity": "容量电费",  #新
        "value_demand": "需量电费",  #新

        "run_hint": "准备完成后运行场景分析",  #新
        "run_button_new": "开始生成决策结果",  #新

        "empty_title": "准备开始一次新的能源场景评估",  #新
        "empty_body": "请先在左侧依次完成：1）上传负荷 CSV；2）配置电价模式；3）选择功率电费方式；4）按需启用储能系统；最后点击“开始生成决策结果”。如果暂时没有自己的数据，可以先下载模板文件进行试用。",  #新

        "analysis_done": "本次场景分析已完成，以下结果可用于技术判断与管理决策。",  #新
        "kpi_desc": "优先展示可直接支持投资与部署决策的关键指标。",  #新
        "oper_desc": "运行特征指标用于解释成本变化与峰值行为。",  #新

        "saving_ratio": "节省比例",  #新
        "energy_saving": "电量电费节省",  #新
        "power_charge_saving": "功率电费节省",  #新
        "peak_reduction": "峰值功率降低",  #新
        "optimized_max_power": "优化后最大功率",  #新
        "tariff_breakdown": "电价明细",  #新
        "storage_result_preview": "储能结果预览",  #新
        "tariff_result_preview": "电价结果预览",  #新
    },
    "en": {
        "page_title": "Energy Optimization Engine",
        "sidebar_title": "Energy Optimization Engine",
        "sidebar_desc": "Economic Analysis & Decision Agent for Data Center & Digital Infrastructure",
        "language_toggle": "中文",
        "data_source": "Load Data",
        "upload_csv": "Upload CSV",
        "download_template": "⤓ Template",
        "upload_hourly_csv": "Upload hourly load CSV",
        "tariff_mode": "Tariff Input Mode",
        "manual_tariff": "Manual Input",
        "table_tariff": "Upload Annual Tariff Table",
        "upload_tariff_table": "Upload annual tariff table CSV",
        "tariff_template_download": "⤓ Template",
        "tariff_settings": "TOU Tariff Settings",
        "critical_peak_price": "Critical Peak Price",
        "peak_price": "Peak Price",
        "flat_price": "Flat Price",
        "valley_price": "Valley Price",
        "super_valley_price": "Super Valley Price",
        "critical_peak_hours": "Critical Peak Hours",
        "peak_hours": "Peak Hours",
        "flat_hours": "Flat Hours",
        "valley_hours": "Valley Hours",
        "super_valley_hours": "Super Valley Hours",
        "power_charge_mode": "Power Charge Mode",
        "capacity_charge": "Capacity Charge",
        "demand_charge": "Demand Charge",
        "capacity_price_per_kw": "Capacity Charge Price",
        "contract_buffer_ratio": "Contract Buffer Ratio",
        "demand_price_per_kw": "Demand Charge Price",
        "use_storage": "Storage System",
        "without_storage": "Do Not Apply",
        "with_storage": "Apply",
        "storage_input_mode": "Storage Parameter Source",
        "storage_manual": "Manual Input",
        "storage_upload": "Upload CSV",
        "storage_sample": "Use Sample Data",
        "upload_storage_csv": "Upload storage parameter CSV",
        "storage_template_download": "⤓ Template",
        "storage_sample_select": "Select Sample Data",
        "storage_settings": "Storage Parameters",
        "storage_capacity": "Storage Capacity (kWh)",
        "storage_power": "Storage Power (kW)",
        "charge_efficiency": "Charge Efficiency",
        "discharge_efficiency": "Discharge Efficiency",
        "min_soc_ratio": "Minimum SOC Ratio",
        "max_soc_ratio": "Maximum SOC Ratio",
        "capex_total": "Total CAPEX",
        "annual_om_cost": "Annual O&M Cost",
        "project_years": "Project Years",
        "discount_rate": "Discount Rate",
        "annual_degradation_rate": "Annual Capacity Degradation Rate",
        "run_simulation": "Run Simulation",
        "title": "Energy Optimization Engine",
        "caption": "Evaluate factory electricity cost structure and storage project value",
        "need_upload_first": "Please upload a CSV file first.",
        "need_tariff_upload_first": "Please upload the annual tariff table CSV first.",
        "need_storage_upload_first": "Please upload the storage parameter CSV first.",
        "simulation_success": "Simulation completed successfully.",
        "simulation_failed": "Simulation failed",
        "click_to_start": "Set parameters in the sidebar, then click 'Run Simulation' to start.",
        "key_metrics": "Key Metrics",
        "sample_total_cost": "Total Cost (Sample Period)",
        "annual_total_cost": "Total Cost (Annual)",
        "peak_load": "Peak Load",
        "max_power": "Maximum Power",
        "load_factor": "Load Factor",
        "weighted_avg_price": "Weighted Average Price",
        "storage_saving": "Storage Saving (Sample Period)",
        "average_annual_net_benefit": "Average Annual Net Benefit",
        "payback_years": "Payback",
        "simple_roi": "ROI",
        "irr": "IRR",
        "lcoe": "LCOE",
        "load_analysis": "Load Analysis",
        "tariff_analysis": "Tariff Analysis",
        "storage_operation": "Storage Operation",
        "auto_conclusion": "Auto-generated Conclusion",
        "load_summary": "Load Summary",
        "tariff_summary": "Tariff Summary",
        "storage_summary": "Storage Summary",
        "finance_summary": "Finance Summary",
        "recommendation": "Recommendation",
        "result_preview": "Result Data Preview",
        "not_available": "N/A",
        "factory_load_curve": "Factory Load Curve",
        "avg_load_by_hour": "Average Load by Hour",
        "load_with_price": "Load Curve with Tariff Price",
        "tariff_share_pie": "Electricity Cost Share by Tariff Period",
        "storage_soc_chart": "Storage Charge, Discharge, and SOC",
        "optimized_load_chart": "Original vs Optimized Grid Load",
        "cost_reduction_chart": "Electricity Cost Reduction",
        "time": "Time",
        "hour_of_day": "Hour of Day",
        "load_kwh_axis": "Load (kWh)",
        "avg_load_kwh_axis": "Average Load (kWh)",
        "price_axis": "Price",
        "tariff_period_axis": "Tariff Period",
        "cost_axis": "Cost",
        "charge_discharge_axis": "Charge / Discharge (kWh)",
        "soc_axis": "SOC (kWh)",
        "relative_cost_axis": "Relative Cost (%)",
        "before_storage": "Before Storage",
        "after_storage": "After Storage",

        "app_name": "Energy Optimization Engine",
        "app_subtitle": "A decision-oriented platform for electricity cost analysis, peak shaving, storage arbitrage, and project economics.",
        "app_caption": "A tech-style demo for energy cost optimization, storage evaluation, and executive decision support.",

        "chip_tou_tariff_analysis": "TOU Tariff Analysis",
        "chip_power_charge_evaluation": "Power Charge Evaluation",
        "chip_storage_arbitrage": "Storage Arbitrage",
        "chip_financial_metrics": "Financial Metrics",

        "section_data_input": "Data Input",
        "section_data_input_desc": "Upload the load profile and prepare simulation inputs.",
        "section_tariff": "Tariff Configuration",
        "section_tariff_desc": "Select the tariff mode and define electricity pricing.",
        "section_power": "Power Charge Configuration",
        "section_power_desc": "Configure capacity-based or demand-based power charges.",
        "section_storage": "Storage Configuration",
        "section_storage_desc": "Enable storage if needed and configure the system parameters.",

        "scenario_summary": "Scenario Summary",
        "executive_summary": "Executive Summary",
        "detailed_insights": "Detailed Insights",
        "before_after_overview": "Before vs After Overview",
        "detailed_result_table": "Detailed Result Table",
        "detailed_result_table_hint": "Use the table below for engineering review and detailed inspection.",

        "label_tariff_mode": "Tariff Mode",
        "label_power_mode": "Power Charge",
        "label_storage_mode": "Storage",
        "label_data_status": "Load Data",

        "value_uploaded": "Uploaded",
        "value_not_uploaded": "Not uploaded",
        "value_enabled": "Enabled",
        "value_disabled": "Disabled",
        "value_manual": "Manual",
        "value_table": "Monthly Table",
        "value_capacity": "Capacity",
        "value_demand": "Demand",

        "run_hint": "Run the scenario analysis when configuration is ready",
        "run_button_new": "Generate Decision Results",

        "empty_title": "Ready to Evaluate a New Energy Scenario",
        "empty_body": "Use the left sidebar to: 1) upload a load CSV, 2) configure the tariff mode, 3) select the power charge method, and 4) optionally enable storage. Then click 'Generate Decision Results'. If you do not have your own data yet, download the templates and try the demo first.",

        "analysis_done": "Scenario analysis completed. The results below can support both engineering review and executive decision-making.",
        "kpi_desc": "Decision-first metrics for investment and deployment evaluation.",
        "oper_desc": "Operational indicators explain the cost structure and peak behavior.",

        "saving_ratio": "Saving Ratio",
        "energy_saving": "Energy Saving",
        "power_charge_saving": "Power Charge Saving",
        "peak_reduction": "Peak Reduction",
        "optimized_max_power": "Optimized Max Power",
        "tariff_breakdown": "Tariff Breakdown",
        "storage_result_preview": "Storage Result Preview",
        "tariff_result_preview": "Tariff Result Preview",
    },
}


# ============================================================
# Translation helper
# ============================================================

def get_text(language: str) -> dict:
    """
    Return translation dictionary for current language.
    Defaults to Chinese.
    """
    return TRANSLATIONS.get(language, TRANSLATIONS["zh"])