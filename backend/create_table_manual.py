#!/usr/bin/env python3
"""Create attendance_sessions table in Supabase using manual SQL execution"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Missing SUPABASE_URL or SUPABASE_KEY in .env file")
    exit(1)

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=== CREATING ATTENDANCE_SESSIONS TABLE ===")

# Since we can't create tables via the client API, let's just test inserting
# First test if table exists by trying to insert a dummy record

test_session = {
    "date": "2025-11-06",
    "subject": "Test Subject",
    "department": "Computer Science",
    "year": "2nd Year", 
    "division": "A",
    "created_at": "2025-11-06T12:00:00",
    "duration_minutes": 10,
    "expires_at": "2025-11-06T12:10:00",
    "finalized": False,
    "ended_at": None,
    "students": []
}

try:
    # Try to insert a test record
    response = supabase.table('attendance_sessions').insert(test_session).execute()
    print("✅ Table exists and test record inserted!")
    
    # Clean up the test record
    test_id = response.data[0]['id']
    supabase.table('attendance_sessions').delete().eq('id', test_id).execute()
    print("✅ Test record cleaned up")
    
except Exception as e:
    error_msg = str(e)
    if 'does not exist' in error_msg:
        print("❌ Table 'attendance_sessions' does not exist")
        print("\nPlease create it manually in Supabase SQL Editor:")
        print("1. Go to your Supabase Dashboard")
        print("2. Click 'SQL Editor' in the sidebar")
        print("3. Run this SQL command:")
        print("""
CREATE TABLE attendance_sessions (
    id SERIAL PRIMARY KEY,
    date TEXT,
    subject TEXT,
    department TEXT,
    year TEXT,
    division TEXT,
    created_at TEXT,
    duration_minutes INTEGER DEFAULT 10,
    expires_at TEXT,
    finalized BOOLEAN DEFAULT FALSE,
    ended_at TEXT,
    students JSONB DEFAULT '[]'::jsonb,
    created_at_ts TIMESTAMP DEFAULT NOW()
);
        """)
    else:
        print(f"❌ Other error: {e}")

print("\n=== NEXT STEPS ===")
print("1. Create the table using the SQL above")
print("2. Try creating an attendance session again")
print("3. The session should include the duration timer feature")