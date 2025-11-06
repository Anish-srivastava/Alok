#!/usr/bin/env python3
"""
Database Schema Diagnosis and Complete Fix
This will check the current schema and provide the exact SQL needed
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("🔍 DATABASE SCHEMA DIAGNOSIS")
print("=" * 80)

def check_table_schema(table_name):
    """Check what columns exist in a table"""
    print(f"\n📋 Checking {table_name} table...")
    try:
        # Try to get table info by attempting a select with limit 0
        response = supabase.table(table_name).select('*').limit(0).execute()
        print(f"✅ {table_name} table exists")
        
        # Try a test insert to see what columns are expected
        test_data = {"test": "value"}
        try:
            result = supabase.table(table_name).insert(test_data).execute()
            print(f"⚠️ Unexpected: test insert succeeded on {table_name}")
        except Exception as insert_error:
            error_msg = str(insert_error)
            if "Could not find" in error_msg and "column" in error_msg:
                print(f"❌ Missing columns detected in {table_name}")
                print(f"Error: {error_msg}")
            elif "violates not-null constraint" in error_msg:
                print(f"⚠️ NOT NULL constraint issues in {table_name}")
                print(f"Error: {error_msg}")
            else:
                print(f"ℹ️ Other constraint in {table_name}: {error_msg}")
                
    except Exception as table_error:
        print(f"❌ {table_name} table error: {table_error}")
    
    return True

# Check both auth tables
check_table_schema('auth_users')
check_table_schema('auth_teachers')

print("\n" + "=" * 80)
print("🛠️ DEFINITIVE SOLUTION")
print("=" * 80)

print("""
The 'password' column error indicates the database schema is not properly updated.

🎯 IMMEDIATE ACTION REQUIRED:

1. Go to Supabase Dashboard:
   👉 https://megrkujckfrtbrhwakmo.supabase.co/project/megrkujckfrtbrhwakmo

2. Click 'SQL Editor' in the left sidebar

3. Copy and paste this COMPLETE schema reset:
""")

print("""
-- ===== COMPLETE SCHEMA RESET =====
-- This will fix ALL schema issues at once

-- Drop existing problematic tables
DROP TABLE IF EXISTS attendance_records CASCADE;
DROP TABLE IF EXISTS attendance_sessions CASCADE;
DROP TABLE IF EXISTS auth_teachers CASCADE;
DROP TABLE IF EXISTS auth_users CASCADE;

-- Create auth_users with CORRECT schema
CREATE TABLE auth_users (
    id SERIAL PRIMARY KEY,
    username TEXT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,  -- ✅ This fixes the 'password' column error
    user_type TEXT NOT NULL CHECK (user_type IN ('student', 'teacher')),
    employee_id TEXT,
    student_id TEXT,
    department TEXT,
    status TEXT DEFAULT 'active',
    role TEXT,
    created_at INTEGER NOT NULL,
    updated_at INTEGER DEFAULT EXTRACT(EPOCH FROM NOW())::INTEGER -- ✅ This fixes NOT NULL constraint
);

-- Create auth_teachers with CORRECT schema
CREATE TABLE auth_teachers (
    id SERIAL PRIMARY KEY,
    username TEXT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,  -- ✅ This fixes the 'password' column error
    employee_id TEXT UNIQUE NOT NULL,
    department TEXT,
    status TEXT DEFAULT 'active',
    role TEXT DEFAULT 'teacher',
    created_at INTEGER NOT NULL,
    updated_at INTEGER DEFAULT EXTRACT(EPOCH FROM NOW())::INTEGER -- ✅ This fixes NOT NULL constraint
);

-- Create attendance_sessions table
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

-- Create attendance_records table
CREATE TABLE attendance_records (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES attendance_sessions(id),
    student_id TEXT NOT NULL,
    student_name TEXT NOT NULL,
    present BOOLEAN DEFAULT FALSE,
    marked_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
""")

print("\n" + "=" * 80)
print("✅ AFTER RUNNING THE SQL ABOVE:")
print("=" * 80)
print("1. The 'password' column error will be FIXED")
print("2. The 'updated_at' constraint error will be FIXED") 
print("3. ALL missing columns will be added")
print("4. Run this script again to verify: python schema_diagnosis.py")
print("5. Test signup: http://localhost:3000/signup")

print("\n🚨 IMPORTANT: This will delete any existing user data!")
print("If you have important user data, export it first.")

print("\n" + "=" * 80)
print("🧪 VERIFICATION STEPS:")
print("=" * 80)
print("After applying the schema:")
print("1. python test_auth_tables.py")
print("2. python simple_signup_test.py")  
print("3. Test frontend signup form")
print("4. Both student and teacher signup should work!")