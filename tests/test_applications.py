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
    create_application(client, auth_headers)
    create_application(client, other_auth_headers)


# ---------- isolation ----------

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

    assert response.status_code == 404
    mine = list_applications(client, auth_headers)
    assert mine[0]["job_description"] == LONG_JD


def test_other_user_cannot_delete_application(client, auth_headers, other_auth_headers):
    app = create_application(client, auth_headers)

    response = client.delete(f"/delete_application/{app['id']}", headers=other_auth_headers)

    assert response.status_code == 404
    assert len(list_applications(client, auth_headers)) == 1


# ---------- update (PATCH) ----------

def test_patch_only_job_description_keeps_other_fields(client, auth_headers):
    app = create_application(client, auth_headers, job_description=LONG_JD)

    response = client.patch(
        f"/update_application/{app['id']}",
        json={"job_description": CHANGED_JD},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["job_description"] == CHANGED_JD
    assert data["status"] == app["status"]


def test_patch_only_status_keeps_job_description(client, auth_headers):
    app = create_application(client, auth_headers, job_description=LONG_JD)

    response = client.patch(
        f"/update_application/{app['id']}",
        json={"status": "Interview"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Interview"
    assert response.json()["job_description"] == LONG_JD


def test_patch_nonexistent_application_returns_404(client, auth_headers):
    response = client.patch(
        "/update_application/9999",
        json={"job_description": LONG_JD},
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------- delete ----------

def test_delete_application_removes_it(client, auth_headers):
    app = create_application(client, auth_headers)

    response = client.delete(f"/delete_application/{app['id']}", headers=auth_headers)

    assert response.status_code == 200
    assert list_applications(client, auth_headers) == []


def test_delete_nonexistent_application_returns_404(client, auth_headers):
    response = client.delete("/delete_application/9999", headers=auth_headers)
    assert response.status_code == 404


# ---------- auth ----------

def test_applications_routes_require_token(client):
    assert client.get("/get_applications").status_code == 401
    assert client.post("/add_application", json={}).status_code == 401
    assert client.delete("/delete_application/1").status_code == 401
