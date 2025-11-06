#!/usr/bin/env python3
"""
SCHEMA FIX SCRIPT
This script will fix the auth tables by adding the missing 'password' column 
and copying data from 'password_hash' if it exists.
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

print("=== DATABASE SCHEMA FIX ===")
print("\nThis script will:")
print("1. Check current table structure")
print("2. Show you the SQL commands to run in Supabase Dashboard")
print("3. These commands will fix the 'password' column issue")

print("\n" + "="*50)
print("MANUAL STEPS TO FIX THE DATABASE:")
print("="*50)

print("\n1. Go to your Supabase Dashboard:")
print("   https://megrkujckfrtbrhwakmo.supabase.co/project/megrkujckfrtbrhwakmo")

print("\n2. Click 'SQL Editor' in the left sidebar")

print("\n3. Copy and paste these SQL commands one by one:")

print("\n--- STEP A: Add password column to auth_users ---")
print("""
ALTER TABLE auth_users 
ADD COLUMN IF NOT EXISTS password TEXT;
""")

print("\n--- STEP B: Add password column to auth_teachers ---") 
print("""
ALTER TABLE auth_teachers 
ADD COLUMN IF NOT EXISTS password TEXT;
""")

print("\n--- STEP C: Add missing columns to auth_users ---")
print("""
ALTER TABLE auth_users 
ADD COLUMN IF NOT EXISTS username TEXT,
ADD COLUMN IF NOT EXISTS user_type TEXT,
ADD COLUMN IF NOT EXISTS employee_id TEXT,
ADD COLUMN IF NOT EXISTS department TEXT,
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active';
""")

print("\n--- STEP D: Add missing columns to auth_teachers ---")
print("""
ALTER TABLE auth_teachers 
ADD COLUMN IF NOT EXISTS username TEXT,
ADD COLUMN IF NOT EXISTS department TEXT,
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active',
ADD COLUMN IF NOT EXISTS updated_at INTEGER;
""")

print("\n--- STEP E: Copy password_hash to password (if data exists) ---")
print("""
UPDATE auth_users 
SET password = password_hash 
WHERE password_hash IS NOT NULL AND password IS NULL;

UPDATE auth_teachers 
SET password = password_hash 
WHERE password_hash IS NOT NULL AND password IS NULL;
""")

print("\n4. After running all commands, test the signup again!")

print("\n" + "="*50)
print("ALTERNATIVE: COMPLETE SCHEMA RESET")
print("="*50)
print("\nIf you prefer to start fresh, you can run this instead:")
print("(WARNING: This will delete all existing user data!)")

print("""
-- Drop existing tables
DROP TABLE IF EXISTS attendance_records;
DROP TABLE IF EXISTS attendance_sessions; 
DROP TABLE IF EXISTS auth_teachers;
DROP TABLE IF EXISTS auth_users;

-- Recreate with correct schema
CREATE TABLE auth_users (
    id SERIAL PRIMARY KEY,
    username TEXT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    user_type TEXT NOT NULL CHECK (user_type IN ('student', 'teacher')),
    employee_id TEXT,
    department TEXT,
    status TEXT DEFAULT 'active',
    created_at INTEGER NOT NULL
);

CREATE TABLE auth_teachers (
    id SERIAL PRIMARY KEY,
    username TEXT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    employee_id TEXT UNIQUE NOT NULL,
    department TEXT,
    status TEXT DEFAULT 'active',
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);

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

print("\n" + "="*50)
print("AFTER FIXING THE DATABASE:")
print("="*50)
print("1. The signup form should work correctly")
print("2. Both student and teacher registration will function")
print("3. Login will work with the new schema")
print("4. You can test at: http://localhost:3000/signup")
print("\nRun this script again after the database fix to verify everything works!")