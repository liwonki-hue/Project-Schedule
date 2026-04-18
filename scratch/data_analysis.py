import pandas as pd
import os

workspace = r"c:\Users\PCLOVE\Downloads\Project Schedule"

def get_piping_data():
    path = os.path.join(workspace, "BOP Piping Joint Master.xlsx")
    # Let's check 'Piping' sheet for granular data or 'System'/'Area' for summaries
    df_piping = pd.read_excel(path, sheet_name='Piping')
    print("Piping Columns:", df_piping.columns.tolist())
    print(df_piping.head())
    
    # Try to find D/I column
    di_cols = [c for c in df_piping.columns if 'D/I' in str(c) or 'DI' in str(c)]
    print("Possible D/I columns:", di_cols)
    return df_piping

def get_support_data():
    path = os.path.join(workspace, "Support Master(260330).xlsx")
    df_support = pd.read_excel(path, sheet_name='Master')
    print("Support Columns:", df_support.columns.tolist())
    print(df_support.head())
    return df_support

get_piping_data()
get_support_data()
