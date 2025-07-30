from app import app, db, User

with app.app_context():
    users = User.query.all()
    print(f"Total Users: {len(users)}")
    print("\nAll Users:")
    print("-" * 80)
    for user in users:
        print(f"ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"Display Name: {user.display_name}")
        print(f"Email: {user.email}")
        print(f"Points: {user.points}")
        print(f"Streak: {user.streak}")
        print(f"Assets: ${user.assets:.2f}")
        print(f"Lessons Done: {user.lessons_done}")
        print(f"Challenges Done: {user.challenges_done}")
        print(f"Created: {user.created_at}")
        print("-" * 80) 