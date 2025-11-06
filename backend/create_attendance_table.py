#!/usr/bin/env python3
"""Create attendance_sessions table in Supabase"""

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

try:
    print("=== CREATING ATTENDANCE_SESSIONS TABLE ===")
    
    # Check if table exists first by trying to select from it
    try:
        response = supabase.table('attendance_sessions').select('id').limit(1).execute()
        print("✅ attendance_sessions table already exists")
    except Exception:
        print("❌ attendance_sessions table doesn't exist, need to create it manually")
        print("\nPlease create the table in Supabase with this SQL:")
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
        exit(1)
        
    # Test inserting a sample session
    print("=== TESTING SESSION CREATION ===")
    test_session = {
        "date": "2025-11-06",
        "subject": "Test Subject",
        "department": "Computer Science",
        "year": "2nd Year",
        "division": "A",
        "created_at": "2025-11-06T11:52:00",
        "duration_minutes": 10,
        "expires_at": "2025-11-06T12:02:00",
        "finalized": False,
        "ended_at": None,
        "students": []
    }
    
    response = supabase.table('attendance_sessions').insert(test_session).execute()
    print(f"✅ Test session created with ID: {response.data[0]['id']}")
    
    # Clean up test session
    session_id = response.data[0]['id']
    supabase.table('attendance_sessions').delete().eq('id', session_id).execute()
    print("✅ Test session cleaned up")
    
    print("\n🎉 attendance_sessions table is ready!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nIf the table doesn't exist, create it in Supabase SQL editor with:")
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