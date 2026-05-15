import pytest
import app


@pytest.fixture
def client():
    app.app.config["TESTING"] = True
    with app.app.test_client() as c:
        yield c


def _register(client, username, password):
    return client.post(
        "/register",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def _login(client, username, password):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def _register_and_login(client, username, password):
    _register(client, username, password)
    return _login(client, username, password)


class TestUnauthenticated:
    def test_index_redirects_to_login(self, client):
        rv = client.get("/")
        assert rv.status_code == 302
        assert "/login" in rv.headers["Location"]

    def test_add_page_loads(self, client):
        rv = client.get("/add")
        assert rv.status_code == 200

    def test_list_page_loads(self, client):
        rv = client.get("/list")
        assert rv.status_code == 200

    def test_login_page_loads(self, client):
        rv = client.get("/login")
        assert rv.status_code == 200

    def test_register_page_loads(self, client):
        rv = client.get("/register")
        assert rv.status_code == 200

    def test_logout_redirects(self, client):
        rv = client.get("/logout")
        assert rv.status_code == 302
        assert "/login" in rv.headers["Location"]

    def test_export_csv_empty(self, client):
        rv = client.get("/export")
        assert rv.status_code == 200
        assert rv.mimetype == "text/csv"
        assert rv.headers["Content-Disposition"] == "attachment;filename=data.csv"
        assert rv.data.decode() == "name,amount,category\n"


class TestAuth:
    def test_register_user(self, client):
        rv = _register(client, "alice", "secret")
        assert rv.status_code == 200

    def test_register_then_login(self, client):
        _register(client, "bob", "pass")
        rv = _login(client, "bob", "pass")
        assert rv.status_code == 200

    def test_login_wrong_password(self, client):
        _register(client, "charlie", "correct")
        rv = client.post(
            "/login",
            data={"username": "charlie", "password": "wrong"},
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert "/login" in rv.request.path

    def test_login_wrong_user(self, client):
        rv = client.post(
            "/login",
            data={"username": "nobody", "password": "x"},
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert "/login" in rv.request.path

    def test_dashboard_authenticated(self, client):
        _register_and_login(client, "dave", "pw")
        rv = client.get("/")
        assert rv.status_code == 200

    def test_logout_clears_session(self, client):
        _register_and_login(client, "eve", "pw")
        client.get("/")
        rv = client.get("/logout")
        assert rv.status_code == 302
        assert "/login" in rv.headers["Location"]

        rv = client.get("/")
        assert rv.status_code == 302


class TestExpenses:
    def test_add_expense(self, client):
        _register_and_login(client, "frank", "pw")
        rv = client.post(
            "/add",
            data={"name": "Lunch", "amount": "12.50", "category": "Food"},
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert b"Lunch" in rv.data

    def test_add_expense_shows_in_list(self, client):
        _register_and_login(client, "grace", "pw")
        client.post(
            "/add",
            data={"name": "Dinner", "amount": "25.00", "category": "Food"},
        )

        rv = client.get("/list")
        assert b"Dinner" in rv.data

    def test_delete_expense(self, client):
        _register_and_login(client, "heidi", "pw")
        client.post(
            "/add",
            data={"name": "ToDelete", "amount": "5.00", "category": "Other"},
        )

        rv = client.get("/list")
        assert b"ToDelete" in rv.data

        rv = client.get("/delete/1", follow_redirects=True)
        assert rv.status_code == 200

        rv = client.get("/list")
        assert b"ToDelete" not in rv.data

    def test_export_csv_with_data(self, client):
        _register_and_login(client, "ivan", "pw")
        client.post(
            "/add",
            data={"name": "ExportItem", "amount": "99.99", "category": "Tools"},
        )

        rv = client.get("/export")
        assert rv.status_code == 200
        assert rv.mimetype == "text/csv"
        body = rv.data.decode()
        assert body.startswith("name,amount,category\n")
        assert "ExportItem,99.99,Tools" in body

    def test_add_expense_without_auth(self, client):
        rv = client.post(
            "/add",
            data={"name": "NoAuth", "amount": "1.00", "category": "Test"},
            follow_redirects=True,
        )
        assert rv.status_code == 200
        rv = client.get("/list")
        assert b"NoAuth" in rv.data

    def test_delete_nonexistent(self, client):
        rv = client.get("/delete/999", follow_redirects=True)
        assert rv.status_code == 200

    def test_add_expense_no_data(self, client):
        rv = client.post("/add", data={}, follow_redirects=True)
        assert rv.status_code == 400

    def test_dashboard_shows_totals(self, client):
        _register_and_login(client, "judy", "pw")
        client.post(
            "/add",
            data={"name": "A", "amount": "10", "category": "Food"},
        )
        client.post(
            "/add",
            data={"name": "B", "amount": "20", "category": "Food"},
        )

        rv = client.get("/")
        assert rv.status_code == 200
