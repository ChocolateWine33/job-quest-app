LONG_JD = "Python, FastAPI, PostgreSQL. " * 15   # ~435 chars, schema requires 300+
CHANGED_JD = LONG_JD + "changed"


# ---------- helpers ----------

def create_application(client, headers, **overrides):
    payload = {"company_name": "Acme", "role": "Backend Dev", "job_description": LONG_JD}
    payload.update(overrides)
    response = client.post("/add_application", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()


def list_applications(client, headers):
    return client.get("/get_applications", headers=headers).json()


# ---------- create ----------

def test_add_application_returns_201_and_data(client, auth_headers):
    app = create_application(client, auth_headers)
    assert "id" in app
    assert app["company_name"] == "Acme"


def test_add_duplicate_application_returns_409(client, auth_headers):
    create_application(client, auth_headers)
    response = client.post(
        "/add_application",
        json={"company_name": "Acme", "role": "Backend Dev", "job_description": LONG_JD},
        headers=auth_headers,
    )
    assert response.status_code == 409


def test_same_application_allowed_for_different_users(client, auth_headers, other_auth_headers):
    # the duplicate rule must be per user, not global
    create_application(client, auth_headers)
    create_application(client, other_auth_headers)  # must not raise 409


# ---------- isolation: user B can't touch user A's data ----------

def test_list_only_returns_own_applications(client, auth_headers, other_auth_headers):
    create_application(client, auth_headers)
    response = client.get("/get_applications", headers=other_auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_other_user_cannot_update_application(client, auth_headers, other_auth_headers):
    app = create_application(client, auth_headers, job_description=LONG_JD)

    response = client.patch(
        f"/update_application/{app['id']}",
        json={"job_description": CHANGED_JD},
        headers=other_auth_headers,
    )
