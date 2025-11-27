from app.db import get_session
from app.models.user import User

# List all users in the database
with get_session() as session:
    users = session.query(User).all()
    print("Username | First Name | Last Name | Role | Balance")
    for user in users:
        print(f"{user.username} | {user.first_name} | {user.last_name} | {user.role} | {user.balance}")
