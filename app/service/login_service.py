# app/service/login_service.py
from typing import Optional


class LoginService:
	"""
	Simple login service used by the CLI.
	Provides authenticate(username, password) -> bool and logout().
	Uses SQLAlchemy database for authentication.
	"""

	def __init__(self) -> None:
		# no state required for now
		pass

	def authenticate(self, username: str, password: str) -> bool:
		"""
		Validate username/password against the database using SQLAlchemy.
		Returns True on success, False on failure.
		"""
		try:
			from app.db import get_session
			from app.models.user import User
			with get_session() as session:
				user = session.query(User).filter_by(username=username).first()
				if user is None:
					return False
				if str(user.password) == str(password):
					return True
				return False
		except Exception as e:
			print(f"Authentication error: {e}")
			return False

	def logout(self) -> None:
		"""Logout does nothing in database mode."""
		pass
