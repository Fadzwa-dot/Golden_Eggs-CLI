def test_authenticate_success(session, seed_users_and_securities, services):
    login = services["login"]
    creds = seed_users_and_securities
    assert login.authenticate("admin", "password263") is True


def test_authenticate_failure(session, seed_users_and_securities, services):
    login = services["login"]
    assert login.authenticate("admin", "wrongpass") is False
    assert login.authenticate("unknown", "x") is False
