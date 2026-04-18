from supabase import create_client, Client
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv(r'c:\Users\PCLOVE\Downloads\Construction Daily Report\.env')

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def list_tables():
    # Attempting to fetch from rpc or just common names since direct listing of tables isn't always enabled for anon key
    # Let's try to query 'joints' or 'JointMaster' or 'JOINT_MASTER'
    tables_to_try = ["joint_master", "Joint_Master", "JointMaster", "joints", "JOINT_MASTER", "construction_joints"]
    for t in tables_to_try:
        try:
            print(f"Trying {t}...")
            response = supabase.table(t).select("*").limit(1).execute()
            print(f"Success! {t} exists. Columns: {pd.DataFrame(response.data).columns.tolist()}")
            return t
        except Exception as e:
            print(f"Failed {t}: {e}")

if __name__ == "__main__":
    list_tables()
