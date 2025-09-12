#!/bin/bash

echo "🚀 Creating sample data for your social platform..."

# Navigate to the Django project directory
cd /home/robot/Documents/code/social-100/100_days_of__api

# Check if virtual environment exists and activate it
if [ -f "venv/bin/activate" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
elif [ -f "../venv/bin/activate" ]; then
    echo "📦 Activating virtual environment..."
    source ../venv/bin/activate
fi

echo "🏗️  Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo "👥 Creating sample data..."
echo "   - Creating 25 users"
echo "   - Creating 15 projects" 
echo "   - Creating 150 posts"
echo "   - Creating friendships and interactions"

python manage.py create_sample_data --users 25 --posts 150 --projects 15

echo "✅ Sample data created successfully!"
echo ""
echo "📊 Data Summary:"
echo "   - 25 Users with realistic names and emails"
echo "   - 15 Projects (Web Dev, ML, Mobile Apps, etc.)"
echo "   - 150 Posts with realistic #100DaysOfCode content"
echo "   - Random friendships and friend requests"
echo "   - Likes and comments on posts"
echo ""
echo "🔑 You can login with any user using:"
echo "   Email: [firstname].[lastname][number]@example.com"
echo "   Password: password123"
echo ""
echo "Example: alex.smith0@example.com / password123"
echo ""
echo "🎯 To add more posts later, run:"
echo "   python manage.py add_more_posts --count 50"
