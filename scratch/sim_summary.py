import pandas as pd
import os

workspace = r"c:\Users\PCLOVE\Downloads\Project Schedule"

def categorize_area(area_name):
    if pd.isna(area_name): return "Other"
    area_name = str(area_name).upper()
    if "PR" in area_name or "PIPE RACK" in area_name:
        return "Pipe Rack"
    if "MB" in area_name or "MAIN BUILDING" in area_name or "HRSG" in area_name or "STG" in area_name:
        return "Main Building"
    return "Others"

def run_simulation():
    piping_path = os.path.join(workspace, "BOP Piping Joint Master.xlsx")
    support_path = os.path.join(workspace, "Support Master(260330).xlsx")
    
    df_p = pd.read_excel(piping_path, sheet_name='Piping')
    df_s = pd.read_excel(support_path, sheet_name='Master')
    
    df_p['Joint'] = pd.to_numeric(df_p['Joint'], errors='coerce').fillna(0)
    df_p['Category'] = df_p['Area'].apply(categorize_area)
    
    df_s['Category'] = df_s['Area'].apply(categorize_area)
    
    piping_summary = df_p.groupby(['Category', 'Area', 'System'])['Joint'].sum().reset_index()
    support_summary = df_s.groupby(['Category', 'Area', 'System']).size().reset_index(name='Count')
    
    total_piping = df_p['Joint'].sum()
    total_support = len(df_s)
    
    print(f"Total Piping DI: {total_piping}")
    print(f"Total Support Count: {total_support}")
    
    # Preceding logic: Pipe Rack first, then Main Building?
    # Or simultaneous? The user said PR and MB are preceding processes.
    # This means piping construction starts after Structure.
    
    return piping_summary, support_summary, total_piping, total_support

p_sum, s_sum, t_p, t_s = run_simulation()

# Detailed reporting...
p_cat = p_sum.groupby('Category')['Joint'].sum()
s_cat = s_sum.groupby('Category')['Count'].sum()

print("\n--- Summary by Category ---")
print("Piping:\n", p_cat)
print("Support:\n", s_cat)
