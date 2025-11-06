#!/usr/bin/env python3
"""Test Supabase connection and create attendance_sessions table"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print(f"URL: {SUPABASE_URL}")
print(f"Key: {SUPABASE_KEY[:10]}..." if SUPABASE_KEY else "Key: None")

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=== TESTING SUPABASE CONNECTION ===")

# Test basic connection
try:
    # Test with existing students table
    response = supabase.table('students').select('id').limit(1).execute()
    print("✅ Supabase connection works")
    print(f"Students table has {len(response.data)} records (showing 1)")
except Exception as e:
    print(f"❌ Supabase connection failed: {e}")
    exit(1)

print("\n=== CREATING ATTENDANCE_SESSIONS TABLE ===")
print("""
To create the table, go to Supabase Dashboard > SQL Editor and run:

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