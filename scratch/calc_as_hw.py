import pandas as pd
import os

workspace = r"c:\Users\PCLOVE\Downloads\Project Schedule"
piping_path = os.path.join(workspace, "BOP Piping Joint Master.xlsx")

df = pd.read_excel(piping_path, sheet_name='Piping')
# Use the previously established scale factor
scale_factor = 109358.0 / 437037.0

# Filter for AS (Aux Steam) and HW (Hot Water)
mask = (df['System'].isin(['AS', 'HW'])) & (df['Unit'].isin(['B0', 'B1', 'B0, B1']))
as_hw_df = df[mask]

total_di = as_hw_df['Joint'].sum() * scale_factor
print(f"TOTAL_AS_HW_DI: {total_di:.0f}")

# Distribution by Area (Estimated based on path: PR4 -> PR3 -> MB -> GT11)
# We divide by 4 major areas
distributed_di = total_di / 4
print(f"DISTRIBUTED_DI_PER_AREA: {distributed_di:.0f}")
