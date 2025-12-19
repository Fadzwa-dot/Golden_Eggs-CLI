# app/service/user_service.py
from typing import List
from app.database import db
from app.models.user import User
from app.service.exceptions import ValidationError, NotFoundError, AuthorizationError

class UserService:
    def list_users(self) -> List[User]:
        return db.session.query(User).all()

    def create_user(self, first_name: str, last_name: str, username: str, password: str, balance: float, role: str = "customer") -> User:
        try:
            if db.session.query(User).filter_by(username=username).first():
                raise ValidationError("Username already exists.")
            if role == "admin":
                admin_exists = db.session.query(User).filter_by(role="admin").count() > 0
                # Allow creation if no admin exists yet
                pass
            user = User(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password,
                balance=balance,
                role=role
            )
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            # Log the error and raise a ValidationError with details
            import traceback
            print("Error creating user:", e)
            traceback.print_exc()
            raise ValidationError(f"Failed to create user: {e}")

    def delete_user(self, username: str) -> None:
        user = db.session.query(User).filter_by(username=username).first()
        if not user:
            raise NotFoundError("User does not exist.")
        if user.portfolios and len(user.portfolios) > 0:
            raise ValidationError("User has portfolios. Remove them before deleting the user.")
        db.session.delete(user)
        db.session.commit()

    def deposit(self, username: str, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero.")
        user = db.session.query(User).filter_by(username=username).first()
        if not user:
            raise NotFoundError(f"User '{username}' does not exist.")
        user.balance += amount
        db.session.commit()
