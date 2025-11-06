#!/usr/bin/env python3
"""Test auth tables structure in Supabase"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=== TESTING AUTH TABLES STRUCTURE ===")

# Test auth_users table
print("\n1. Testing auth_users table:")
try:
    # Try to select all columns to see what exists
    response = supabase.table('auth_users').select('*').limit(1).execute()
    print("✅ auth_users table exists")
    if response.data:
        print(f"Columns: {list(response.data[0].keys())}")
    else:
        print("Table is empty - will try to insert test record to see schema error")
        
        # Try a test insert to see what columns are missing
        test_user = {
            "username": "test",
            "email": "test@example.com", 
            "password": "test123",
            "user_type": "student",
            "created_at": 1234567890
        }
        try:
            result = supabase.table('auth_users').insert(test_user).execute()
            print("✅ Test insert successful - schema is correct")
            # Clean up test record
            if result.data:
                supabase.table('auth_users').delete().eq('email', 'test@example.com').execute()
                print("✅ Test record cleaned up")
        except Exception as insert_error:
            print(f"❌ Insert failed: {insert_error}")
            
except Exception as e:
    print(f"❌ auth_users table error: {e}")

# Test auth_teachers table  
print("\n2. Testing auth_teachers table:")
try:
    response = supabase.table('auth_teachers').select('*').limit(1).execute()
    print("✅ auth_teachers table exists")
    if response.data:
        print(f"Columns: {list(response.data[0].keys())}")
    else:
        print("Table is empty - will try to insert test record to see schema error")
        
        # Try a test insert to see what columns are missing
        test_teacher = {
            "username": "test_teacher",
            "email": "teacher@example.com",
            "password": "test123", 
            "employee_id": "EMP001",
            "department": "Computer Science",
            "created_at": 1234567890
        }
        try:
            result = supabase.table('auth_teachers').insert(test_teacher).execute()
            print("✅ Test insert successful - schema is correct")
            # Clean up test record
            if result.data:
                supabase.table('auth_teachers').delete().eq('email', 'teacher@example.com').execute()
                print("✅ Test record cleaned up")
        except Exception as insert_error:
            print(f"❌ Insert failed: {insert_error}")
            
except Exception as e:
    print(f"❌ auth_teachers table error: {e}")

print("\n=== SUMMARY ===")
print("If you see 'password' column errors, you need to update your Supabase schema.")
print("Use the CORRECTED_SQL_SCHEMA.txt file to fix the database structure.")