from supabase import create_client, Client
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv(r'c:\Users\PCLOVE\Downloads\Construction Daily Report\.env')

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def inspect_table():
    response = supabase.table("joint_master").select("*").limit(5).execute()
    df = pd.DataFrame(response.data)
    print("Columns:", df.columns.tolist())
    print("Head:\n", df.head())

if __name__ == "__main__":
    inspect_table()
