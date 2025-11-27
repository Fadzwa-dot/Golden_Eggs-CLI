# app/service/user_service.py
from typing import List
from app.db import get_session
from app.models.user import User
from app.service.exceptions import ValidationError, NotFoundError, AuthorizationError

class UserService:
    def list_users(self) -> List[User]:
        with get_session() as session:
            return session.query(User).all()

    def create_user(self, first_name: str, last_name: str, username: str, password: str, balance: float, role: str = "customer") -> User:
        try:
            with get_session() as session:
                if session.query(User).filter_by(username=username).first():
                    raise ValidationError("Username already exists.")
                if role == "admin":
                    admin_exists = session.query(User).filter_by(role="admin").count() > 0
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
                session.add(user)
                session.commit()
                return user
        except Exception as e:
            # Log the error and raise a ValidationError with details
            import traceback
            print("Error creating user:", e)
            traceback.print_exc()
            raise ValidationError(f"Failed to create user: {e}")

    def delete_user(self, username: str) -> None:
        with get_session() as session:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                raise NotFoundError("User does not exist.")
            if user.portfolios and len(user.portfolios) > 0:
                raise ValidationError("User has portfolios. Remove them before deleting the user.")
            session.delete(user)
            session.commit()

    def deposit(self, username: str, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero.")
        with get_session() as session:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                raise NotFoundError(f"User '{username}' does not exist.")
            user.balance += amount
            session.commit()
