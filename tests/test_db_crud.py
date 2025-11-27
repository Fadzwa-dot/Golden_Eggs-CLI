from app.db import get_session
from app.models.user import User


def test_db_insert_update_delete(session):
    with get_session() as s:
        u = User(username="bob", first_name="Bob", last_name="Tester", password="pw", balance=50.0, role="customer")
        s.add(u)
        s.commit()
        # read
        fetched = s.query(User).filter_by(username="bob").first()
        assert fetched is not None
        # update
        fetched.balance = 75.0
        s.commit()
        updated = s.query(User).filter_by(username="bob").first()
        assert updated.balance == 75.0
        # delete
        s.delete(updated)
        s.commit()
        deleted = s.query(User).filter_by(username="bob").first()
        assert deleted is None
