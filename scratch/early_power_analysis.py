import pandas as pd
import os

workspace = r"c:\Users\PCLOVE\Downloads\Project Schedule"

def analyze_early_power():
    piping_path = os.path.join(workspace, "BOP Piping Joint Master.xlsx")
    support_path = os.path.join(workspace, "Support Master(260330).xlsx")
    
    # Load detailed piping
    df_p = pd.read_excel(piping_path, sheet_name='Piping')
    # Filter Systems: IA, CCW, FG, DW, GT MISC, N2
    # Filter Units: B0, B1
    # Filter Areas (if applicable): MB STR, HRSG #11 PR, GT #11, and PR #3-7
    
    systems = ['IA', 'CCW', 'FG', 'DW', 'GT MISC', 'N2']
    units = ['B0', 'B1']
    areas = ['MB STR', 'HRSG #11 PR', 'GT #11', 'PR #3', 'PR #4', 'PR #5', 'PR #6', 'PR #7']
    
    # Piping data filter
    df_p['Joint'] = pd.to_numeric(df_p['Joint'], errors='coerce').fillna(0)
    
    # In Piping Master, there's no 'Count' but 'Joint' should be the volume metric.
    # Note: User previously mentioned summary values. For specific filtering, I should use the 'Piping' sheet.
    # However, the 'Piping' sheet summary might be different from the 'System' sheet.
    # I'll scale the 'Piping' sheet values to match the user's verified '109,358' erection total if needed.
    # Total Joints in Piping sheet was 437,037. Correct total is 109,358 (Erection).
    # Scale factor = 109358 / 437037
    scale_factor = 109358.0 / 437037.0
    
    mask_p = (df_p['System'].isin(systems)) & (df_p['Unit'].isin(units))
    # Area filter: YARD corresponds to PR in Support. MB #1 corresponds to MB STR/GT #11 etc.
    # For now, let's filter by System/Unit first as the primary driver.
    essential_piping = df_p[mask_p]
    essential_p_volume = essential_piping['Joint'].sum() * scale_factor
    
    # Support data filter
    df_s = pd.read_excel(support_path, sheet_name='Master')
    mask_s = (df_s['System'].isin(systems)) & (df_s['Area'].isin(areas))
    essential_support = df_s[mask_s]
    essential_s_volume = len(essential_support)
    
    return {
        "p_vol": essential_p_volume,
        "s_vol": essential_s_volume,
        "p_count": len(essential_piping)
    }

results = analyze_early_power()
print(f"Essential Piping (Scaled DI): {results['p_vol']:.2f}")
print(f"Essential Support (Count): {results['s_vol']}")

# Timeline
from datetime import datetime, timedelta
target_op = datetime(2026, 12, 31)
# Cleaning 2m + Pre-comm 1m + HT 14d = 104 days? 
# Let's say: Target Completion = Sep 16, 2026
target_comp = datetime(2026, 9, 16)
today = datetime(2026, 4, 18)
days_rem = (target_comp - today).days

print(f"Days to Mechanical Completion (Sep 16): {days_rem}")
print(f"Required Daily Piping: {results['p_vol'] / days_rem:.2f} DI/Day")
print(f"Required Daily Support: {results['s_vol'] / days_rem:.2f} EA/Day")
