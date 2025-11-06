import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Test Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print(f"SUPABASE_URL: {SUPABASE_URL}")
print(f"SUPABASE_KEY: {SUPABASE_KEY[:20]}...")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client created successfully")
    
    # Test connection by checking auth_users table
    result = supabase.table('auth_users').select("id").limit(1).execute()
    print(f"✅ Connection test successful: {result}")
    
except Exception as e:
    print(f"❌ Supabase connection error: {e}")