import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

# --- Global Layout Config ---
st.set_page_config(page_title="Strategic Piping Management", layout="wide", page_icon="🏗️")

# --- UI Aesthetics ---
st.markdown("""
    <style>
    /* Global Compactness */
    [data-testid="stVerticalBlock"] > div { padding-top: 0px !important; padding-bottom: 0px !important; gap: 0.1rem !important; }
    .stApp { background-color: white !important; }
    
    /* Remove Backgrounds & Borders */
    .report-card, .flow-box, .solution-card { 
        background: transparent !important; 
        border: none !important; 
        padding: 5px !important;
        color: black !important;
    }
    
    /* Report Font Adjustments: Titles 1.1x larger than baseline */
    .report-card h2 { font-size: 1.45rem !important; margin-top: 15px !important; color: #1e293b !important; }
    .report-card h3 { font-size: 1.25rem !important; margin-top: 10px !important; color: #475569 !important; }
    .report-card p, .report-card li { font-size: 1.2rem !important; line-height: 1.5 !important; }
    
    /* Enhanced Table Styling */
    .report-card table { width: 50% !important; border-collapse: collapse !important; margin-top: 15px !important; }
    .report-card th { background-color: #f8fafc !important; border-bottom: 2px solid #cbd5e1 !important; padding: 12px !important; }
    .report-card td { padding: 12px !important; border-bottom: 1px solid #e2e8f0 !important; }
    
    /* Lower Section Tables: Shrink only the Essential Systems table to 80% */
    .compact-section table { 
        width: 80% !important; 
        margin-left: 0 !important; 
        margin-right: auto !important;
    }
    
    /* Center align table headers and cells via CSS hack */
    .stDataFrame [data-testid="stTable"] th { text-align: center !important; vertical-align: middle !important; font-size: 1.15rem !important; }
    .stDataFrame [data-testid="stTable"] td { text-align: center !important; vertical-align: middle !important; font-size: 1.1rem !important; }
    .stDataFrame [data-testid="stMetric"] { text-align: center; } /* Also center metrics */
    
    /* Metric compression - Scale up by 1.3x */
    [data-testid="stMetricValue"] { font-size: 1.6rem !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { font-size: 1.2rem !important; }
    /* Essential Systems Table Optimization */
    [data-testid="stTable"] td {
        font-size: 0.95rem !important;
        vertical-align: middle !important;
    }
    /* Index, System, Area: Keep narrow and no-wrap */
    [data-testid="stTable"] td:nth-child(1),
    [data-testid="stTable"] td:nth-child(2),
    [data-testid="stTable"] td:nth-child(3) {
        white-space: nowrap !important;
    }
    /* Description(4), Criticality(5), Related Equipment(6): Increase width */
    [data-testid="stTable"] td:nth-child(4) { min-width: 300px !important; white-space: nowrap !important; }
    [data-testid="stTable"] td:nth-child(5) { min-width: 100px !important; white-space: nowrap !important; }
    [data-testid="stTable"] td:nth-child(6) { min-width: 250px !important; white-space: nowrap !important; }
    
    /* Remark(7th): Reduce width and allow wrap */
    [data-testid="stTable"] td:nth-child(7) {
        white-space: normal !important;
        width: 200px !important;
    }

    [data-testid="stMetric"] { margin-bottom: -1rem !important; text-align: center; }
    
    .solution-card {
        background: #eef2ff !important; /* Indigo-tinted background */
        border-left: 6px solid #4338ca !important; /* Indigo border */
        padding: 20px !important;
        border-radius: 8px !important;
        color: #1e1b4b !important; /* Deep indigo text */
        line-height: 1.6 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .solution-title {
        font-size: 1.6rem !important;
        font-weight: 800 !important;
        margin-bottom: 12px !important;
        display: block;
        color: #312e81 !important;
    }
    .solution-content {
        font-size: 1.25rem !important;
        font-weight: 700 !important;
    }

    [data-testid="stHeader"] { display: none; }
    .block-container { padding-top: 0.5rem !important; padding-bottom: 0.5rem !important; padding-left: 2rem !important; padding-right: 2rem !important; }
    
    /* Sidebar Spacing */
    [data-testid="stSidebar"] { background-color: #f8fafc !important; }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] { padding-top: 25px !important; gap: 0.6rem !important; }
    [data-testid="stSidebar"] .stMarkdown { margin-bottom: 5px !important; }
    [data-testid="stSidebar"] .stDateInput, [data-testid="stSidebar"] .stSlider, [data-testid="stSidebar"] .stNumberInput { margin-bottom: 8px !important; }
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { font-weight: 700 !important; font-size: 0.95rem !important; color: #334155 !important; }
</style>
""", unsafe_allow_html=True)

# --- Master Data ---
AREA_DATA = {
    "GT #11 Installation": {"EA": 895, "DI": 4115, "Lag": 0, "Status": "Alignment (50%)"}, # Added AS/HW (+1649 DI, +518 EA)
    "HRSG #11 PR": {"EA": 173, "DI": 1131, "Lag": 2, "Status": "In Progress"},
    "Main Building Structure": {"EA": 1808, "DI": 10087, "Lag": 2, "Status": "Wait for MB Steel"}, # Added AS/HW (+1649 DI, +518 EA)
    "Pipe Rack #3": {"EA": 925, "DI": 4311, "Lag": 2, "Status": "Wait for Architectural"}, # Added AS/HW (+1649 DI, +518 EA)
    "Pipe Rack #4": {"EA": 1118, "DI": 5574, "Lag": 2, "Status": "Wait for Architectural"}, # Added AS/HW (+1649 DI, +518 EA)
    "Pipe Rack #5": {"EA": 266, "DI": 1740, "Lag": 2, "Status": "Wait for Architectural"},
    "Pipe Rack #6": {"EA": 173, "DI": 1131, "Lag": 2, "Status": "Wait for Architectural"},
    "Pipe Rack #7": {"EA": 221, "DI": 1445, "Lag": 2, "Status": "Wait for Architectural"}
}
TOTAL_DI = sum(d["DI"] for d in AREA_DATA.values())
TOTAL_EA = sum(d["EA"] for d in AREA_DATA.values())
MC_TARGET = datetime.date(2026, 9, 16)

# --- Print Support ---
def add_print_button():
    components.html(
        """
        <script>
            function printReport() {
                window.parent.print();
            }
        </script>
        <div style="display: flex; justify-content: flex-end; align-items: center; height: 100%;">
            <button onclick="printReport()" style="
                background-color: #f8fafc;
                color: #475569;
                padding: 6px 14px;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
                font-size: 13px;
                display: flex;
                align-items: center;
                gap: 6px;
                box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            ">
                <span>🖨️</span> Print
            </button>
        </div>
        """,
        height=60
    )

# --- Sidebar Controls ---
st.sidebar.markdown('<h2 style="font-size: 1.35rem; margin-top: 0; margin-bottom: 5px;">📌 Simulation Panel</h2>', unsafe_allow_html=True)

st.sidebar.markdown('<hr style="margin: 10px 0;">', unsafe_allow_html=True)
st.sidebar.markdown('<p style="font-weight: 600; font-size: 1.05rem; margin-bottom: 8px;">Handover Dates</p>', unsafe_allow_html=True)
rel_dates = {}
for area in AREA_DATA.keys():
    d_rel = datetime.date(2026, 6, 1)
    if "#3" in area: d_rel = datetime.date(2026, 5, 20)
    if "GT #11" in area: d_rel = datetime.date(2026, 7, 5)
    rel_dates[area] = st.sidebar.date_input(area, d_rel)

st.sidebar.markdown('<hr style="margin: 5px 0;">', unsafe_allow_html=True)
with st.sidebar.expander("Manpower Setup", expanded=True):
    total_manpower_teams = st.number_input("Piping Work Teams", 1, 100, 40)
    prod_di = st.slider("DI/Team-Day", 3.0, 30.0, 12.0)
    prod_ea_ratio = st.slider("EA/DI Ratio", 0.1, 1.0, 0.3)
    priority = st.slider("EP Priority (%)", 0, 100, 70)

# --- Simulation Logic ---
AREA_CAPS = {
    "Main Building Structure": 6, # Space constraint: Max 6 Work Teams
    "GT #11 Installation": 8,
    "HRSG #11 PR": 6,
    "Pipe Rack #3": 4,
    "Pipe Rack #4": 4,
    "Pipe Rack #5": 3,
    "Pipe Rack #6": 3,
    "Pipe Rack #7": 3,
}

ep_work_teams = total_manpower_teams * (priority / 100)
prod_ea = prod_di * prod_ea_ratio
sim_results = []

# --- Resource Allocation Logic (Redistribution Algorithm) ---
def allocate_teams(total_teams, area_data, area_caps):
    assigned = {area: 0.0 for area in area_data}
    remaining_teams = total_teams
    
    # Iteratively distribute teams to areas not yet at capacity
    for _ in range(10): # Max 10 iterations to prevent infinite loops
        eligible_areas = [a for a in area_data if assigned[a] < area_caps.get(a, 4)]
        if not eligible_areas or remaining_teams < 0.1:
            break
            
        total_eligible_weight = sum(area_data[a]["DI"] for a in eligible_areas)
        if total_eligible_weight == 0: break
        
        starting_remaining = remaining_teams
        for area in eligible_areas:
            share = area_data[area]["DI"] / total_eligible_weight
            potential_assign = starting_remaining * share
            
            # How much more can this area take?
            space_left = area_caps.get(area, 4) - assigned[area]
            actual_assign = min(potential_assign, space_left)
            
            assigned[area] += actual_assign
            remaining_teams -= actual_assign
            
        if starting_remaining - remaining_teams < 0.05: break
    
    # Ensure minimum 1 team per active area if possible
    for area in assigned:
        if assigned[area] < 1.0 and remaining_teams > 0:
            assigned[area] = 1.0
            
    return assigned

assigned_teams_map = allocate_teams(ep_work_teams, AREA_DATA, AREA_CAPS)
prod_ea = prod_di * prod_ea_ratio
sim_results = []

# --- Calculate simulation with assigned teams ---
for area, data in AREA_DATA.items():
    piping_start = rel_dates[area] + datetime.timedelta(weeks=data["Lag"])
    assigned_teams = assigned_teams_map[area]
    
    # Calculate daily output for the area
    capacity_di = assigned_teams * prod_di
    piping_days = data["DI"] / capacity_di if capacity_di > 0 else 999
    
    piping_finish = piping_start + datetime.timedelta(days=int(piping_days))
    pt_finish = piping_finish + datetime.timedelta(weeks=2)
    flt = (MC_TARGET - pt_finish).days
    
    sim_results.append({
        "Area": area, 
        "Handover": rel_dates[area],
        "Schedule Status": data["Status"],
        "Work Teams": round(assigned_teams, 1),
        "Piping Finish": piping_finish,
        "Pressure Test Finish": pt_finish,
        "Piping(DI)": data["DI"], 
        "Support(EA)": data["EA"], 
        "Float": flt
    })

df = pd.DataFrame(sim_results)
max_finish = df["Pressure Test Finish"].max()
net_float = (MC_TARGET - max_finish).days
# Mathematical bottleneck
math_bottleneck = df.loc[df['Pressure Test Finish'].idxmax(), 'Area']
# User defined strategic bottleneck: Main Building Structure
strat_bottleneck = "Main Building Structure"

# --- Essential Systems Data ---
ESSENTIAL_SYSTEMS = [
    {"System": "Fuel Gas System (FG)", "Area": "Main Building / GT Area", "Description": "Distributes filtered and regulated fuel gas to GT combustion system.", "Criticality": "Mandatory", "Related Equipment": "FG Filter Separator, FG Heater", "Remark": ""},
    {"System": "Closed Cooling Water (CCW)", "Area": "Main Building / PR", "Description": "Cooling for GT/ST bearings and accessory equipment. Requires Power Receiving.", "Criticality": "Mandatory", "Related Equipment": "CCW Heat Exchangers, CCW Pumps", "Remark": ""},
    {"System": "Instrument Air (IA)", "Area": "All Areas", "Description": "Compressed air for pneumatic control valves and instruments.", "Criticality": "Operation", "Related Equipment": "Air Compressors, IA Dryers", "Remark": ""},
    {"System": "Aux. Steam & Hot Water (AS/HW)", "Area": "AB Bld / PR#3/4 / MB", "Description": "Anti-Icing for GT Intake to prevent freezing (Dec 31 Startup Basis).", "Criticality": "Mandatory", "Related Equipment": "Aux. Boiler, HW Pumps, HX", "Remark": ""},
    {"System": "Nitrogen System (N2)", "Area": "GT Area / PR", "Description": "Purging fuel gas lines and inerting systems before maintenance.", "Criticality": "Mandatory", "Related Equipment": "N2 Bottle Rack, Purge Panels", "Remark": ""},
    {"System": "GT MISC (Vents)", "Area": "Main Building", "Description": "Safe venting of process gases and drainage of lube oil leakages.", "Criticality": "Mandatory", "Related Equipment": "GT Enclosure, Vent Fans", "Remark": ""},
    {"System": "Demineralized Water (DW)", "Area": "Water Treatment / PR", "Description": "Supply of high-purity water for process requirements and cleaning.", "Criticality": "Highest", "Related Equipment": "DW Tank, DW Supply Pumps", "Remark": "Reviewing temporary demi. water supply via other power plant (by INTEGRA)"},
]

# --- Presentation Layer ---
tab_dash, tab_rep = st.tabs(["📊 Dashboard View", "📋 Technical Report"])

with tab_dash:
    t_col, p_col = st.columns([8.2, 1.8])
    with t_col:
        st.markdown('<h1 style="font-size: 1.8rem; margin: 0; padding: 0;">🏗️ Project Simulation Dashboard: GT #11 Early Power</h1>', unsafe_allow_html=True)
    with p_col:
        add_print_button()
    
    # Major Constraints Alert
    st.markdown(f"""
        <div style="background-color:#fff3e0; padding:15px; border-radius:10px; border-left:8px solid #ff9800; margin-bottom:10px;">
            <span style="font-size:1.15rem; font-weight:bold; color:#e65100;">
                ⚠️ Major Constraint: Power Receiving must be completed before CCW/HW Pump operation. 
                Energizing requires FF (Fire Fighting) & HVAC installation to prevent overheating/fire.
            </span>
        </div>
        <div style="background-color:#e0f2f1; padding:15px; border-radius:10px; border-left:8px solid #00897b; margin-bottom:20px;">
            <span style="font-size:1.15rem; font-weight:bold; color:#004d40;">
                🚨 Ultimate Bottleneck in timeline : {strat_bottleneck} (Structure Access for header piping installation) | Target Float: {net_float} Days
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    # KPI Grid
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Piping Vol. (Field)", f"{TOTAL_DI:,} DI")
    m2.metric("Support Vol.", f"{TOTAL_EA:,} EA")
    m3.metric("Avg Field DI/DAY", f"{prod_di} DI")
    m4.metric("Avg Support EA/DAY", f"{prod_ea:.1f} EA")
    m5.metric("Target Float", f"{net_float} D", delta_color="normal" if net_float >= 0 else "inverse")
    m6.metric("Total Teams", f"{ep_work_teams:.1f}")
    
    st.divider()
    
    left, right = st.columns([6.8, 3.2])
    with left:
        st.subheader("📊 Detailed Milestone Forecast")
        df_view = df.copy()
        # Format for display
        df_view["Work Teams Temp"] = df_view["Work Teams"].map(lambda x: f"{x:.1f}")
        for c in ["Handover", "Pressure Test Finish"]: 
            df_view[c] = df_view[c].apply(lambda x: x.strftime('%Y-%m-%d'))
        
        # Displaying with Site Status (Center alignment and hide index)
        display_cols = ["Area", "Schedule Status", "Work Teams Temp", "Handover", "Piping(DI)", "Support(EA)", "Pressure Test Finish", "Float"]
        # Rename for clean display
        df_display = df_view[display_cols].rename(columns={"Work Teams Temp": "Work Teams"})
        
        # --- Add Total Row ---
        total_row = pd.DataFrame([{
            "Area": "TOTAL",
            "Schedule Status": "",
            "Work Teams": f"{df['Work Teams'].sum():.1f}", 
            "Handover": "",
            "Piping(DI)": int(df["Piping(DI)"].sum()),
            "Support(EA)": int(df["Support(EA)"].sum()),
            "Pressure Test Finish": "",
            "Float": int(df["Float"].min())
        }])
        df_display = pd.concat([df_display, total_row], ignore_index=True)

        st.table(df_display)
    
    with right:
        st.subheader("📅 Construction Path")
        # Align chart bars with table rows (offset for table header height)
        st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
        # --- Enhanced Chart: Add Start/Finish Labels ---
        fig = px.timeline(df, x_start="Handover", x_end="Pressure Test Finish", y="Area", 
                          color="Float", color_continuous_scale=["#ef4444", "#22c55e"], height=250)
        # Define Key Milestones
        mc_date = pd.to_datetime(MC_TARGET)
        pr_date = mc_date - datetime.timedelta(days=16) # Power Receiving: 16 days before MC for logic
        
        # Add Milestone Vertical Lines (Adjusted to stop just below labels)
        fig.add_shape(type="line", x0=pr_date, x1=pr_date, y0=0, y1=1.10, yref="paper",
                      line=dict(color="blue", width=2, dash="dash"))
        fig.add_shape(type="line", x0=mc_date, x1=mc_date, y0=0, y1=1.01, yref="paper",
                      line=dict(color="red", width=2, dash="dash"))
        
        # Add Milestone Labels on TOP (Center-aligned on lines, staggered heights to prevent overlap)
        fig.add_annotation(x=pr_date, y=1.18, yref="paper", text=f"<b>Power Receiving: {pr_date.strftime('%m/%d')}</b>", 
                           showarrow=False, font=dict(color="blue", size=11), xanchor="center", xshift=0)
        fig.add_annotation(x=mc_date, y=1.08, yref="paper", text=f"<b>MC: {mc_date.strftime('%m/%d')}</b>", 
                           showarrow=False, font=dict(color="red", size=11), xanchor="center", xshift=0)
        
        # Add text labels for Start and Finish next to the bars
        for idx, row in df.iterrows():
            # Start Date (Left)
            fig.add_annotation(
                x=row["Handover"], y=row["Area"],
                text=f"<b>{row['Handover'].strftime('%m/%d')}</b>",
                showarrow=False, xanchor='right', xshift=-10,
                font=dict(size=11, color="#334155")
            )
            # Finish Date (Right)
            f_finish = pd.to_datetime(row["Pressure Test Finish"])
            if f_finish > mc_date: # Highlight delay
                f_color = "#ef4444"
            else:
                f_color = "#334155"
                
            fig.add_annotation(
                x=row["Pressure Test Finish"], y=row["Area"],
                text=f"<b>{row['Pressure Test Finish'].strftime('%m/%d')}</b>",
                showarrow=False, xanchor='left', xshift=10,
                font=dict(size=11, color=f_color)
            )

        fig.update_layout(
            margin=dict(l=0, r=40, t=45, b=0), # Increased top margin for staggered labels
            xaxis_title=None, yaxis_title=None, 
            showlegend=False,
            coloraxis_showscale=False # Remove color bar legend
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- Compact Lower Section ---
    st.markdown("""
        <style>
        .compact-section { margin-top: -70px; }
        .stDivider { margin-top: 0px; margin-bottom: 0px; }
        .flow-box { 
            background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; 
            padding: 10px; font-size: 1.05rem; text-align: center; height: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="compact-section">', unsafe_allow_html=True)
    # Divider removed to save space
    
    st.subheader("🔄 Construction Work Flow")
    f1, f2, f3, f4, f5, f6 = st.columns(6)
    f1.markdown('<div class="flow-box"><b>1. Fabrication</b><br>Spool & Support Fabrication</div>', unsafe_allow_html=True)
    f2.markdown('<div class="flow-box"><b>2. Structure</b><br>Handover</div>', unsafe_allow_html=True)
    f3.markdown('<div class="flow-box"><b>3. Access</b><br>Scaffolding<br>(2 Weeks)</div>', unsafe_allow_html=True)
    f4.markdown('<div class="flow-box"><b>4. Erection</b><br>Header & Branches Piping</div>', unsafe_allow_html=True)
    f5.markdown('<div class="flow-box"><b>5. Punch & Test</b><br>Pressure Test & Punch<br>(2 Weeks)</div>', unsafe_allow_html=True)
    f6.markdown('<div class="flow-box"><b>6. Pre-Commissioning</b><br>CCW Flushing & FG Pig Cleaning<br>(2 Months)</div>', unsafe_allow_html=True)

    st.subheader("✅ Essential Systems for GT #11 Start-up")
    df_e = pd.DataFrame(ESSENTIAL_SYSTEMS)
    df_e.index = np.arange(1, len(df_e) + 1)
    st.table(df_e)

    st.subheader("💡 Infrastructure Dependency & Solution")
    st.markdown(f"""
        <div class="solution-card">
            <div class="solution-content">
                <div style="margin-bottom: 8pt;">1. <b>Safety Priority</b>: Prioritize Fire Fighting & HVAC in electrical rooms to allow Energizing without fire/overheating risk.</div>
                <div style="margin-bottom: 8pt;">2. <b>Power Receiving</b>: Complete AIS/Transformer & Cable installation to enable Power Receiving before CCW Flushing.</div>
                <div style="margin-bottom: 8pt;">3. <b>Structural Early Handover</b>: Accelerate Pipe Rack & MB Structure delivery through additional manpower and crash work by preceding Mechanical/Architectural teams.</div>
                <div>4. <b>Double Shift</b>: Implement 24/7 welding for Main Building Structural Header-to-Branch transitions.</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
# --- Technical Report Tab ---
with tab_rep:
    rt_col, rp_col = st.columns([8.5, 1.5])
    with rt_col:
        st.title("📋 Technical Report: GT #11 Early Power")
    with rp_col:
        add_print_button()
        
    st.markdown(f"""
    <div class="report-card">
    
    # GT #11 EARLY POWER PIPING & INFRASTRUCTURE STRATEGY REPORT
    **Date**: {datetime.date.today()} | **Operation Milestone**: Dec 31, 2026
    
    ---
    
    ## 1. Project Sequence & Major Infrastructure Constraints
    The GT #11 startup is governed not only by piping progress but also by critical infrastructure and safety prerequisites.
    
    ### A. Permanent Power Receiving (The Power Milestone)
    Power Receiving is a **non-negotiable milestone** that must occur before the operation of all auxiliary equipment, including CCW Pumps, Air Compressors, and HW Pumps.
    - **Pre-requisites**: Installation of AIS (Air Insulated Switchgear), Transformers, Electrical Panels, and Main Cabling must be finalized.
    - **Safety Dependency**: Energizing cannot proceed without the completion of **Fire Fighting (FF)** and **HVAC** systems to mitigate the risk of fire and equipment overheating.
    - **Impact**: Power Receiving must be completed *prior* to the CCW Flushing phase to ensure pump functionality.

    ### B. Strategic Prerequisite: Main Building Steel
    The Main Building Steel Structure remains the definitive piping bottleneck, as branch piping distributions depend on MB Structure certification.
    
    ## 2. Anti-Icing System: AS & HW Strategy
    For the target operation date of **Dec 31, 2026**, the Anti-Icing system is mandatory to prevent GT Air Intake freezing.
    - **System Logic**: Utilizes Steam from the **Aux. Boiler** to heat water, which is then circulated via **Hot Water (HW) Supply Pumps** and Heat Exchangers.
    - **Critical Routing**: The AS/HW piping path encompasses: **Aux. Boiler Building & HW Pump House → PR #4 → PR #3 → MB Structure → GT #11**.
    - **Priority Scope**: Installation of Unit B0 and B1 piping volumes is mandatory for this system to be functional for the winter startup.
    
    ## 3. Commissioning Strategy: CCW & Fuel Gas
    The 2-month window post-MC is driven by high-velocity flushing of the CCW and clean-pigging of the FG lines.
    
    ## 4. Resource Allocation Logic (Deep Dive)
    - **Workspace Constraint**: Manpower in Main Building Structure remains capped at **6 teams** due to elevation and space safety constraints.
    - **Dynamic Redistribution**: Teams will be prioritized for AS/HW and FG/CCW essential systems to meet the Dec 31 milestone.
    
    ## 5. Essential Systems & Criticality matrix
    
    | Essential System | Area | Description | Criticality | Related Equipment / Remark |
    | :--- | :--- | :--- | :--- | :--- |
    | **1. Fuel Gas** | MB / GT | High-pressure fuel distribution. | **Mandatory** | FG Filter Separator / Heater |
    | **2. CCW** | MB / PR | Cooling for bearings/accessory equipment. | **Mandatory** | **Power Receiving Requirement** |
    | **3. IA** | All | Instrument air for control valves. | **Operation** | Air Compressors / IA Dryers |
    | **4. AS/HW** | AB / PR | Anti-Icing for winter startup. | **Mandatory** | **Aux. Boiler Integration** |
    | **5. N2** | GT / PR | Purging and inerting for safety. | **Mandatory** | N2 Bottle Rack / Purge Panels |
    | **6. GT MISC** | MB | Process gas venting and drainage. | **Mandatory** | GT Enclosure / Vent Fans |
    | **7. Demi. Water**| WT / PR | Process water and cleaning supply. | **Highest** | **Temporary supply via other power plant (by INTEGRA)** |
    
    > **⚠️ Note on Volumetric Reconciliation**:
    > There is a distinction between the **Total Area Construction Volume (22,938 DI)** on the dashboard and the **Start-up Essential Scope** above. 
    > 1. **Field Erection Basis**: All DI values represent **Site Field Erection (Final Jointing)** only. Shop Fabrication is excluded.
    > 2. **Priority**: Resource allocation is prioritized for these systems to compress the schedule.
    
    - **Integrated Approach**: Welding and NDT for these systems are prioritized for the Main Building and Pipe Rack #3/#4 paths.
    
    ## 6. Summary of Strategic Actions
    1. **Power Receiving Interlock**: Synchronize Electrical (AIS/Cable) and Piping (CCW) schedules.
    2. **Safety Systems Concurrent Work**: Ensure FF and HVAC installation in electrical rooms overlaps with cabling to avoid energizing delays.
    3. **AS/HW Path Acceleration**: Prioritize PR#4 and PR#3 paths to secure Anti-Icing before the onset of winter freezing.
    4. **Winterization Readiness**: Complete all B0/B1 scope spools at shop to minimize field welding during cold conditions.
    
    ---
    *Disclaimer: Report updated to reflect Dec 31 Operation basis, Anti-Icing Mandatory requirement, and Power Receiving/FF/HVAC Interlock constraints.*
    
    </div>
    """, unsafe_allow_html=True)
