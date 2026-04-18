import pandas as pd
import os

workspace = r"c:\Users\PCLOVE\Downloads\Project Schedule"

def get_area_breakdown():
    p_path = os.path.join(workspace, "BOP Piping Joint Master.xlsx")
    s_path = os.path.join(workspace, "Support Master(260330).xlsx")
    
    # Load and scale piping
    df_p = pd.read_excel(p_path, sheet_name='Piping')
    df_p['Joint'] = pd.to_numeric(df_p['Joint'], errors='coerce').fillna(0)
    scale = 109358.0 / 437037.0
    
    systems = ['IA', 'CCW', 'FG', 'DW', 'GT MISC', 'N2']
    units = ['B0', 'B1']
    area_map = {
        'PR #3': 'YARD', # Mapping is a bit tricky, I'll use simple filtering
        'PR #4': 'YARD',
        'PR #5': 'YARD',
        'PR #6': 'YARD',
        'PR #7': 'YARD',
        'MB STR': 'MB #1',
        'GT #11': 'MB #1',
        'HRSG #11 PR': 'MB #1'
    }
    
    # Actually, let's just use Support Master for the breakdown as it has cleaner Area names
    df_s = pd.read_excel(s_path, sheet_name='Master')
    mask_s = (df_s['System'].isin(systems))
    essential_s = df_s[mask_s]
    
    # Specific area check for essential scope
    areas_target = ['PR #3', 'PR #4', 'PR #5', 'PR #6', 'PR #7', 'MB STR', 'HRSG #11 PR', 'GT #11', 'HRSG #11']
    breakdown = essential_s[essential_s['Area'].isin(areas_target)].groupby('Area').size()
    
    print("Support EA Breakdown for Essential Systems:")
    print(breakdown)
    
    # Total Essential Support was 3425.
    # Total Essential Piping was 22938.
    # We can distribute Piping DI proportionally to Support EA for this simulation.
    
get_area_breakdown()
