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
    [data-testid="stMetric"] { margin-bottom: -1rem !important; text-align: center; }
    
    .solution-card {
        background: #f0f7ff !important; /* Light blue background for emphasis */
        border-left: 5px solid #0056b3 !important;
        padding: 15px !important;
        border-radius: 4px !important;
        color: #004085 !important; /* Strong blue text */
        line-height: 1.4 !important;
    }
    .solution-title {
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        margin-bottom: 8px !important;
        display: block;
        color: #003366 !important;
    }
    .solution-content {
        font-size: 1.15rem !important;
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
    "GT #11 Installation": {"EA": 377, "DI": 2466, "Lag": 0, "Status": "Alignment (50%)"},
    "HRSG #11 PR": {"EA": 173, "DI": 1131, "Lag": 2, "Status": "In Progress"},
    "Main Building Structure": {"EA": 1290, "DI": 8438, "Lag": 2, "Status": "Wait for MB Steel"},
    "Pipe Rack #3": {"EA": 407, "DI": 2662, "Lag": 2, "Status": "Wait for Civil"},
    "Pipe Rack #4": {"EA": 600, "DI": 3925, "Lag": 2, "Status": "Wait for Civil"},
    "Pipe Rack #5": {"EA": 266, "DI": 1740, "Lag": 2, "Status": "Wait for Civil"},
    "Pipe Rack #6": {"EA": 173, "DI": 1131, "Lag": 2, "Status": "Wait for Civil"},
    "Pipe Rack #7": {"EA": 221, "DI": 1445, "Lag": 2, "Status": "Wait for Civil"}
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
st.sidebar.markdown('<h2 style="font-size: 1.35rem; margin-top: 0; margin-bottom: 5px;">📌 Strategy Panel</h2>', unsafe_allow_html=True)

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
    {"System": "Closed Cooling Water (CCW)", "Area": "Main Building / PR", "Description": "Provides cooling water to GT/ST bearings and accessory equipment.", "Criticality": "Highest", "Remark": "CCW Heat Exchangers, CCW Pumps"},
    {"System": "Fuel Gas System (FG)", "Area": "Main Building / GT Area", "Description": "Distributes filtered and regulated fuel gas to GT combustion system.", "Criticality": "Mandatory", "Remark": "FG Filter Separator, FG Heater, Gas Turbines"},
    {"System": "Demineralized Water (DW)", "Area": "Water Treatment / PR", "Description": "Supply of high-purity water for process requirements and cleaning.", "Criticality": "Mandatory", "Remark": "DW Tank, DW Supply Pumps"},
    {"System": "Nitrogen System (N2)", "Area": "GT Area / PR", "Description": "Used for purging fuel gas lines and inerting systems before maintenance.", "Criticality": "Mandatory", "Remark": "N2 Bottle Rack, Purge Panels"},
    {"System": "GT MISC (Vents)", "Area": "Main Building", "Description": "Safe venting of process gases and drainage of lube oil leakages.", "Criticality": "Mandatory", "Remark": "GT Enclosure, Vent Fans, Lube Oil Mist Eliminator"},
    {"System": "Instrument Air (IA)", "Area": "All Areas", "Description": "Provides compressed air for pneumatic control valves and instruments.", "Criticality": "Operation", "Remark": "Air Compressors, IA Dryers"},
]

# --- Presentation Layer ---
tab_dash, tab_rep = st.tabs(["📊 Dashboard View", "📋 Technical Report"])

with tab_dash:
    t_col, p_col = st.columns([8.2, 1.8])
    with t_col:
        st.markdown('<h1 style="font-size: 1.8rem; margin: 0; padding: 0;">🏗️ Project Acceleration Dashboard: GT #11 Early Power</h1>', unsafe_allow_html=True)
    with p_col:
        add_print_button()
    
    st.markdown(f"""
        <div style="background-color:#e0f2f1; padding:18px; border-radius:10px; border-left:8px solid #00897b; margin-bottom:20px;">
            <span style="font-size:1.35rem; font-weight:bold; color:#004d40;">
                🚨 Ultimate Bottleneck in timeline : {strat_bottleneck} (Structure Access for header piping installation Constraint) | Target Float: {net_float} Days
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
            "Schedule Status": "-",
            "Work Teams": f"{df['Work Teams'].sum():.1f}", 
            "Handover": "-",
            "Piping(DI)": int(df["Piping(DI)"].sum()),
            "Support(EA)": int(df["Support(EA)"].sum()),
            "Pressure Test Finish": "-",
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
        fig.update_yaxes(autorange="reversed") 
        fig.add_vline(x=pd.to_datetime(MC_TARGET).timestamp() * 1000, line_dash="dash", line_color="red")
        
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
            fig.add_annotation(
                x=row["Pressure Test Finish"], y=row["Area"],
                text=f"<b>{row['Pressure Test Finish'].strftime('%m/%d')}</b>",
                showarrow=False, xanchor='left', xshift=10,
                font=dict(size=11, color="#334155")
            )

        fig.update_layout(
            margin=dict(l=0, r=40, t=0, b=0), # Revert to compact margins
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
    f1, f2, f3, f4, f5 = st.columns(5)
    f1.markdown('<div class="flow-box"><b>1. Structure</b><br>Handover</div>', unsafe_allow_html=True)
    f2.markdown('<div class="flow-box"><b>2. Access</b><br>Scaffolding (2 Weeks)</div>', unsafe_allow_html=True)
    f3.markdown('<div class="flow-box"><b>3. Erection</b><br>Header & Branches Piping</div>', unsafe_allow_html=True)
    f4.markdown('<div class="flow-box"><b>4. Punch & Test</b><br>Pressure Test & Punch (2 Weeks)</div>', unsafe_allow_html=True)
    f5.markdown('<div class="flow-box"><b>5. Pre-Commissioning</b><br>CCW Flushing & FG Pig Cleaning<br>(2 Months)</div>', unsafe_allow_html=True)

    st.subheader("✅ Essential Systems for GT #11 Start-up")
    st.table(pd.DataFrame(ESSENTIAL_SYSTEMS))

    st.subheader("💡 Solution to Meet Target MC (Sep 16, 2026)")
    st.markdown(f"""
        <div class="solution-card">
            <div class="solution-content">
                <div style="margin-bottom: 5pt;">1. <b>Parallel Resource Injection</b>: Increase total teams to 40+ upon MB Steel release to compress branch erection.</div>
                <div style="margin-bottom: 5pt;">2. <b>Double Shift (Night Work)</b>: Implement 24/7 welding for Header-to-Branch transitions in Main Building Structural area.</div>
                <div>3. <b>Pre-spool Staging</b>: Complete all item-punching at ground level *before* crane lifting to minimize high-elevation work time.</div>
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
    
    # GT #11 EARLY POWER PIPING STRATEGY REPORT
    **Date**: {datetime.date.today()} | **Objective**: MC by Sep 16, 2026
    
    ---
    
    ## 1. Project Sequence & Site Status
    The successful achievement of the GT #11 Early Power milestone relies on a strictly linear construction logic governed by structural prerequisites. 
    ### A. Current Erection Status
    - **GT #11 Installation**: Currently at **50% progress**. Base Equipment Alignment and Accessory Device Installation are ongoing.
    - **HRSG #11 Installation**: Currently in active progress. 
    ### B. Strategic Prerequisite: Main Building Steel
    The most critical technical lag at this stage is the **Main Building Steel Structure**. According to site logic:
    
    1. **GT & HRSG equipment installation** must be finalized first.
    2. **Main Building steel** is then erected, providing the path for **Header Piping**.
    3. **Branch piping** then distributes from MB Structure -> HRSG #11 -> GT #11.
    4. Consequently, **{strat_bottleneck}** release is the definitive bottleneck.
    
    ## 2. Technical Constraints: Header & Branch Access
    The simulation models identified the strategic importance of the **Header-to-Branch** transition:
    - **Interface Access**: Header piping originating from external racks cannot enter the MB area until the structure is certified.
    - **Lag Impact**: Any delay in MB Steel release exponentially compresses the window for branch erection.
    
    ## 3. Commissioning Strategy: CCW & Fuel Gas
    The 2-month window post-MC is driven by high-velocity flushing of the CCW and clean-pigging of the FG lines.
    
    ## 4. Work Period & Resource Allocation Logic (Deep Dive)
    The simulation models the deployment of **{total_manpower_teams} Dedicated Work Teams** through a "Volume-Weight Resource Distribution" engine.
    - **Workspace Constraint (Bottleneck)**: 
        - **Main Building Structure** is restricted to a **MAX of 6 Work Teams** due to space limitations. 
        - Even with high volume, the maximum output is capped at [6 Work Teams x {prod_di} DI/Day] = **{6 * prod_di} DI/Day**.
    - **Resource Distribution Formula**: 
        - `Assigned Work Teams per Area = min( (Area Volume / Total Volume) * {total_manpower_teams}, Space Cap )`
        - This ensures that while {total_manpower_teams} work teams are active globally, they are not overcrowded in a single area.
    - **Duration Calculation**:
        - `Duration = [Total Area DI] / ( [Assigned Work Teams] x {prod_di} DI/Day )`
    
    ## 5. Essential Systems for GT #11 Start-up
    To achieve Early Power, the following core systems must reach Mechanical Completion (MC) and undergo pre-commissioning.
    
    | Essential System | Area | Description | Criticality | Remark (Equipment) |
    | :--- | :--- | :--- | :--- | :--- |
    | **CCW** | Main Building / PR | Cooling for GT/ST bearings/accessory equipment. | **Highest** | CCW Heat Exchangers, Pumps |
    | **Fuel Gas (FG)** | MB / GT Area | Regulated fuel gas supply to GT combustion. | **Mandatory** | FG Filter Separators, Heaters |
    | **Demineralized Water** | WT / PR | High-purity water for cleaning/process. | **Mandatory** | DW Tanks, Supply Pumps |
    | **Nitrogen (N2)** | GT Area / PR | Purging/inerting systems before maintenance. | **Mandatory** | N2 Bottle Racks, Purge Panels |
    | **GT MISC (Vents)** | Main Building | Safe venting of gases / Oil drainage. | **Mandatory** | GT Enclosure, Vent Fans |
    | **Instrument Air** | All Areas | Compressed air for pneumatic control logic. | **Operation** | Air Compressors, Dryers |
    
    > **⚠️ Note on Volumetric Reconciliation**:
    > There is a distinction between the **Total Area Construction Volume (22,938 DI)** on the dashboard and the **Start-up Essential Scope** above. 
    > 1. **Field Erection Basis**: All DI values represent **Site Field Erection (Final Jointing)** only. Shop Fabrication is excluded.
    > 2. **Priority**: Resource allocation is prioritized for these systems to compress the schedule.
    
    - **Integrated Approach**: Welding and NDT for these systems are prioritized for the Main Building and Pipe Rack #3/#4 paths.
    
    ## 6. Summary of Strategic Actions
    1. **MB Steel Prioritization**: Pressure Civil/Steel subcontractors for the earliest possible handover.
    2. **Branch Pre-positioning**: Accelerate pre-fabrication of branch spools to ensure 100% material readiness.
    3. **Bypass Pre-fab**: Finalize temporary CCW bypass pipes during the August erection phase.
    
    ---
    *Disclaimer: Report updated to reflect current site status (GT 50% Alignment) and Resource-Constrained Simulation (Max 5 Work Teams in Main Building).*
    
    </div>
    """, unsafe_allow_html=True)
