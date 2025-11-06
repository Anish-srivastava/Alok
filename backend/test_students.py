#!/usr/bin/env python3
"""Test script to check students in Supabase database"""

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
    # Check total students
    print("=== CHECKING STUDENTS DATABASE ===")
    
    # Get all students
    response = supabase.table('students').select('*').execute()
    students = response.data
    
    print(f"Total students: {len(students)}")
    
    if students:
        print("\n=== STUDENT DETAILS ===")
        for i, student in enumerate(students, 1):
            print(f"{i}. ID: {student.get('student_id')}")
            print(f"   Name: {student.get('student_name')}")
            print(f"   Email: {student.get('email')}")
            print(f"   Face Registered: {student.get('face_registered')}")
            
            embeddings = student.get('embeddings')
            if embeddings:
                print(f"   Embeddings: {len(embeddings)} face(s)")
                print(f"   Embedding length: {len(embeddings[0]) if embeddings else 0}")
            else:
                print(f"   Embeddings: None")
            print()
    else:
        print("\nNo students found in database!")
        print("\nTo register a student:")
        print("1. Go to http://localhost:3001/student/registrationform")
        print("2. Fill the form and capture 5 face images")
        print("3. Submit the registration")
        
except Exception as e:
    print(f"Database error: {e}")