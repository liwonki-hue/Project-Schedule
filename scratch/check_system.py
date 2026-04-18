import pandas as pd
import os

workspace = r"c:\Users\PCLOVE\Downloads\Project Schedule"
path = os.path.join(workspace, "BOP Piping Joint Master.xlsx")

df = pd.read_excel(path, sheet_name='System')
# The image shows columns S, F, Total
# In the head(20) output:
# Unnamed: 1 is Gubun?
# Unnamed: 2 is S?
# Unnamed: 3 is F?
# Unnamed: 4 is Total?

print(df.iloc[1:30, 0:6])
