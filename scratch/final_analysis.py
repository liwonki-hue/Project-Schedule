import pandas as pd
import os

workspace = r"c:\Users\PCLOVE\Downloads\Project Schedule"

def analyze_piping():
    path = os.path.join(workspace, "BOP Piping Joint Master.xlsx")
    df = pd.read_excel(path, sheet_name='Piping')
    # Use 'Joint' as the quantity metric if it's the D/I
    # Let's check if 'Joint' is numeric
    df['Joint'] = pd.to_numeric(df['Joint'], errors='coerce').fillna(0)
    
    total_joints = df['Joint'].sum()
    summary_area = df.groupby('Area')['Joint'].sum()
    summary_system = df.groupby('System')['Joint'].sum()
    
    return {
        "total": total_joints,
        "by_area": summary_area,
        "by_system": summary_system
    }

def analyze_support():
    path = os.path.join(workspace, "Support Master(260330).xlsx")
    df = pd.read_excel(path, sheet_name='Master')
    
    total_supports = len(df)
    summary_area = df.groupby('Area').size()
    summary_system = df.groupby('System').size()
    
    return {
        "total": total_supports,
        "by_area": summary_area,
        "by_system": summary_system
    }

piping_data = analyze_piping()
support_data = analyze_support()

print("\n--- Piping Analysis ---")
print(f"Total Quantity (Joints/DI): {piping_data['total']}")
print("By Area:\n", piping_data['by_area'])
print("By System:\n", piping_data['by_system'])

print("\n--- Support Analysis ---")
print(f"Total Quantity (Count): {support_data['total']}")
print("By Area:\n", support_data['by_area'])
print("By System:\n", support_data['by_system'])

# Duration calculation
from datetime import datetime
start_date = datetime(2026, 4, 18)
end_date = datetime(2027, 5, 31)
days = (end_date - start_date).days
print(f"\nRemaining Days: {days}")

# Daily target
piping_teams = 40
support_teams = 10

print(f"\nDaily Required (Total):")
print(f"Piping: {piping_data['total'] / days:.2f} per day")
print(f"Support: {support_data['total'] / days:.2f} per day")

print(f"\nTarget per Team per Day:")
print(f"Piping: {(piping_data['total'] / days) / piping_teams:.2f} per team/day")
print(f"Support: {(support_data['total'] / days) / support_teams:.2f} per team/day")
