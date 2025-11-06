#!/usr/bin/env python3
"""
COMPREHENSIVE DATABASE SCHEMA FIX
This script will provide the complete SQL commands to fix all schema issues at once
"""

print("=" * 80)
print("🔧 COMPREHENSIVE DATABASE SCHEMA FIX")
print("=" * 80)

print("\n🎯 CURRENT ISSUE:")
print("Either 'password' column missing OR 'updated_at' NOT NULL constraint issue")

print("\n📋 SOLUTION: Complete Schema Reset (Recommended)")
print("This will recreate tables with the correct structure")

print("\n" + "=" * 60)
print("STEP 1: GO TO SUPABASE DASHBOARD")
print("=" * 60)
print("1. Visit: https://megrkujckfrtbrhwakmo.supabase.co/project/megrkujckfrtbrhwakmo")
print("2. Click 'SQL Editor' in the left sidebar")
print("3. Copy and paste the following SQL commands:")

print("\n" + "=" * 60)
print("STEP 2: COMPLETE TABLE RECREATION")
print("=" * 60)

print("""
-- ===== BACKUP EXISTING DATA (if any exists) =====
-- Skip this if tables are empty

-- Create backup tables (optional)
-- CREATE TABLE auth_users_backup AS SELECT * FROM auth_users;
-- CREATE TABLE auth_teachers_backup AS SELECT * FROM auth_teachers;

-- ===== DROP EXISTING TABLES =====
DROP TABLE IF EXISTS attendance_records CASCADE;
DROP TABLE IF EXISTS attendance_sessions CASCADE;
DROP TABLE IF EXISTS auth_teachers CASCADE;
DROP TABLE IF EXISTS auth_users CASCADE;

-- ===== CREATE CORRECTED TABLES =====

-- Auth Users Table (Students + General Users)
CREATE TABLE auth_users (
    id SERIAL PRIMARY KEY,
    username TEXT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    user_type TEXT NOT NULL CHECK (user_type IN ('student', 'teacher')),
    employee_id TEXT,
    student_id TEXT,
    department TEXT,
    status TEXT DEFAULT 'active',
    role TEXT,
    created_at INTEGER NOT NULL,
    updated_at INTEGER DEFAULT EXTRACT(EPOCH FROM NOW())::INTEGER,
    password_hash TEXT  -- Keep for compatibility but make it optional
);

-- Auth Teachers Table (Teachers Only)
CREATE TABLE auth_teachers (
    id SERIAL PRIMARY KEY,
    username TEXT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    employee_id TEXT UNIQUE NOT NULL,
    department TEXT,
    status TEXT DEFAULT 'active',
    role TEXT DEFAULT 'teacher',
    created_at INTEGER NOT NULL,
    updated_at INTEGER DEFAULT EXTRACT(EPOCH FROM NOW())::INTEGER,
    password_hash TEXT  -- Keep for compatibility but make it optional
);

-- Attendance Sessions Table
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

-- Attendance Records Table
CREATE TABLE attendance_records (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES attendance_sessions(id),
    student_id TEXT NOT NULL,
    student_name TEXT NOT NULL,
    present BOOLEAN DEFAULT FALSE,
    marked_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ===== CREATE INDEXES FOR PERFORMANCE =====
CREATE INDEX idx_auth_users_email ON auth_users(email);
CREATE INDEX idx_auth_teachers_email ON auth_teachers(email);
CREATE INDEX idx_auth_teachers_employee_id ON auth_teachers(employee_id);
CREATE INDEX idx_attendance_sessions_date ON attendance_sessions(date);
CREATE INDEX idx_attendance_records_session_id ON attendance_records(session_id);
""")

print("\n" + "=" * 60)
print("STEP 3: VERIFY SCHEMA CREATION")
print("=" * 60)
print("After running the SQL commands above, test with:")
print("1. Run: python test_auth_tables.py")
print("2. Run: python simple_signup_test.py")
print("3. Test frontend: http://localhost:3000/signup")

print("\n" + "=" * 60)
print("STEP 4: ALTERNATIVE QUICK FIX (if tables have data)")
print("=" * 60)
print("If you don't want to recreate tables, run these commands instead:")
print("""
-- Quick fix without dropping tables
ALTER TABLE auth_users 
ADD COLUMN IF NOT EXISTS password TEXT,
ADD COLUMN IF NOT EXISTS role TEXT,
ADD COLUMN IF NOT EXISTS student_id TEXT,
ALTER COLUMN updated_at DROP NOT NULL,
ALTER COLUMN updated_at SET DEFAULT EXTRACT(EPOCH FROM NOW())::INTEGER;

ALTER TABLE auth_teachers 
ADD COLUMN IF NOT EXISTS password TEXT,
ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'teacher',
ALTER COLUMN updated_at DROP NOT NULL,
ALTER COLUMN updated_at SET DEFAULT EXTRACT(EPOCH FROM NOW())::INTEGER;

-- Copy password_hash to password if needed
UPDATE auth_users SET password = password_hash WHERE password IS NULL AND password_hash IS NOT NULL;
UPDATE auth_teachers SET password = password_hash WHERE password IS NULL AND password_hash IS NOT NULL;
""")

print("\n" + "=" * 80)
print("🎉 AFTER COMPLETING THE DATABASE FIX:")
print("=" * 80)
print("✅ Signup will work for both students and teachers")
print("✅ Login will work correctly")
print("✅ All schema constraints will be satisfied")
print("✅ Frontend http://localhost:3000/signup will work")
print("\n🔄 Run the test again after applying the fix!")