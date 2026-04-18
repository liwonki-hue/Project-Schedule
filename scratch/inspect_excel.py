import pandas as pd
import os

def inspect_excel(file_path):
    print(f"\n--- Inspecting: {file_path} ---")
    try:
        xl = pd.ExcelFile(file_path)
        print(f"Sheet names: {xl.sheet_names}")
        for sheet_name in xl.sheet_names[:2]: # Check first two sheets
            df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=5)
            print(f"\nSheet: {sheet_name}")
            print(f"Columns: {df.columns.tolist()}")
            print(f"Sample data:\n{df.head(2)}")
    except Exception as e:
        print(f"Error: {e}")

workspace = r"c:\Users\PCLOVE\Downloads\Project Schedule"
inspect_excel(os.path.join(workspace, "BOP Piping Joint Master.xlsx"))
inspect_excel(os.path.join(workspace, "Support Master(260330).xlsx"))
