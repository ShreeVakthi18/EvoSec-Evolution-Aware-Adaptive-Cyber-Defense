import concurrent.futures

from tests.conftest import make_client


def test_concurrent_requests_from_many_users_do_not_corrupt_state():
    """Original prototype had no locking around shared dicts; concurrent
    requests could race. This drives many simultaneous users through the
    middleware and checks the resulting state is internally consistent."""

    def hit(ip: str):
        c = make_client(ip)
        for _ in range(5):
            c.get("/login")
        return ip

    ips = [f"10.0.3.{i}" for i in range(1, 31)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        list(pool.map(hit, ips))

    c = make_client(ips[0])
    data = c.get("/dashboard-data").json()
    seen_users = {u["user"] for u in data}
    assert seen_users == set(ips)
    for u in data:
        assert u["requests"] == 5
        assert u["status"] == "NORMAL"


def test_per_user_history_is_bounded():
    from app.config import settings
    from app.risk_engine import store

    original_cap = settings.max_history_per_user
    settings.max_history_per_user = 10
    try:
        c = make_client("10.0.3.100")
        for _ in range(25):
            c.get("/login")
        history = store.history_for("10.0.3.100")
        assert len(history) == 10
    finally:
        settings.max_history_per_user = original_cap
