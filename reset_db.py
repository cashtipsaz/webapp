import os
import sqlite3

# Remove the database file if it exists
db_path = "instance/cashtips.db"
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print("Database file removed successfully")
    except PermissionError:
        print("Database file is locked. Trying to recreate database...")
        # Continue anyway - the database will be recreated

# Create the instance directory if it doesn't exist
os.makedirs("instance", exist_ok=True)

# Create a new database with the updated schema
from app import app, db, User, FinancialEntry, Lesson, LessonProgress, Challenge, ChallengeProgress, PortfolioItem

with app.app_context():
    # Create all tables
    db.create_all()
    print("Database created successfully with updated schema")
    
    # Create sample data
    from datetime import datetime
    
    # Create admin user
    from werkzeug.security import generate_password_hash
    
    admin_user = User(
        username='admin',
        email='aryanleekha1@gmail.com',
        password_hash=generate_password_hash('admin123'),
        display_name='Admin',
        goal=1000.0,
        spending_goal=500.0,
        spending_days=30,
        spending_start_date=datetime.utcnow(),
        income_days=30,
        income_start_date=datetime.utcnow()
    )
    db.session.add(admin_user)
    
    # Create lessons
    lessons = [
        Lesson(title='Budgeting & Savings', description='Learn the basics of budgeting and saving money', 
               video_url='https://www.youtube.com/embed/2M5ExwnN2s4', points_reward=15),
        Lesson(title='Investing Basics', description='Introduction to investing and building wealth', 
               video_url='https://www.youtube.com/embed/tJd2Shdzh4s', points_reward=20),
    ]
    db.session.add_all(lessons)
    
    # Create challenges
    challenges = [
        Challenge(type='Daily', description='Track an Expense', points=15),
        Challenge(type='Daily', description='No Spend Day!', points=15),
        Challenge(type='Daily', description='Short Quiz', points=20),
        Challenge(type='Weekly', description='Review Your Budget', points=25),
        Challenge(type='Weekly', description='Learn Something New', points=30),
    ]
    db.session.add_all(challenges)
    
    db.session.commit()
    print("Sample data created successfully")
    print("Admin user created with username: admin, password: admin123") 