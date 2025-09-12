#!/usr/bin/env python
"""
Quick script to populate the database with sample data
Run this from the Django project root directory
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_sample_data():
    """Setup sample data for the social platform"""
    
    print("🚀 Setting up sample data for your social platform...")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()
    
    try:
        # Run migrations first
        print("🏗️  Running migrations...")
        execute_from_command_line(['manage.py', 'makemigrations'])
        execute_from_command_line(['manage.py', 'migrate'])
        
        # Create sample data
        print("👥 Creating sample data...")
        print("   - Creating 25 users")
        print("   - Creating 15 projects") 
        print("   - Creating 150 posts")
        print("   - Creating friendships and interactions")
        
        execute_from_command_line([
            'manage.py', 'create_sample_data', 
            '--users', '25', 
            '--posts', '150', 
            '--projects', '15'
        ])
        
        print("✅ Sample data created successfully!")
        print("")
        print("📊 Data Summary:")
        print("   - 25 Users with realistic names and emails")
        print("   - 15 Projects (Web Dev, ML, Mobile Apps, etc.)")
        print("   - 150 Posts with realistic #100DaysOfCode content")
        print("   - Random friendships and friend requests")
        print("   - Likes and comments on posts")
        print("")
        print("🔑 You can login with any user using:")
        print("   Email: [firstname].[lastname][number]@example.com")
        print("   Password: password123")
        print("")
        print("Example: alex.smith0@example.com / password123")
        print("")
        print("🎯 To add more posts later, run:")
        print("   python manage.py add_more_posts --count 50")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you're running this from the Django project directory")
        print("and that all dependencies are installed.")

def add_more_posts(count=50):
    """Add more posts to existing data"""
    
    print(f"📝 Adding {count} more posts...")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()
    
    try:
        execute_from_command_line([
            'manage.py', 'add_more_posts', 
            '--count', str(count)
        ])
        
        print(f"✅ Successfully added {count} new posts!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "add_posts":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        add_more_posts(count)
    else:
        setup_sample_data()
