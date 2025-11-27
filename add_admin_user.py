from app.db import get_session
from app.models.user import User

def add_admin_user():
    username = "admin"
    password = "password263"
    first_name = "Admin"
    last_name = "User"
    balance = 0.0
    role = "admin"
    with get_session() as session:
        existing = session.query(User).filter_by(username=username).first()
        if existing:
            print(f"Admin user '{username}' already exists.")
            return
        admin = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            balance=balance,
            role=role
        )
        session.add(admin)
        session.commit()
        print(f"Admin user '{username}' added to the database.")

if __name__ == "__main__":
    add_admin_user()
