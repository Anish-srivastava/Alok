#!/usr/bin/env python3
"""
Quick database test to check if we can connect and see what collections exist
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print(f"Connecting to Supabase...")
print(f"URL: {SUPABASE_URL}")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase connection successful")

    # Try to check some tables
    print("\n--- Checking students table ---")
    try:
        students_result = supabase.table("students").select("*").limit(5).execute()
        print(f"Students found: {len(students_result.data)}")
        if students_result.data:
            print("Sample student:", students_result.data[0])
    except Exception as e:
        print(f"❌ Error accessing students table: {e}")

    print("\n--- Checking attendance_records table ---")
    try:
        attendance_result = supabase.table("attendance_records").select("*").limit(5).execute()
        print(f"Attendance records found: {len(attendance_result.data)}")
        if attendance_result.data:
            print("Sample attendance record:", attendance_result.data[0])
    except Exception as e:
        print(f"❌ Error accessing attendance_records table: {e}")

    print("\n--- Testing simple query ---")
    try:
        # Try a simple health check
        result = supabase.table("students").select("count", count="exact").execute()
        print(f"Total students count: {result.count}")
    except Exception as e:
        print(f"❌ Error with count query: {e}")

except Exception as e:
    print(f"❌ Failed to connect to Supabase: {e}")