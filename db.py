# db.py
from typing import Optional, Dict, List, Any
from app.domain.user import User
from app.domain.security import Security
from app.domain.portfolio import Portfolio
from app.domain.investment import Investment

# In-memory "database" state
logged_in_user: Optional[User] = None
users: Dict[str, User] = {}
securities: Dict[str, Security] = {}
