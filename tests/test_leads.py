import pytest


def test_create_lead(client):
    response = client.post(
        "/leads", json={"client_name": "Ivan", "source": "site", "amount": "1500.50"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] > 0
    assert data["client_name"] == "Ivan"
    assert data["amount"] == "1500.50"
    assert data["status"] == "new"
    assert "created_at" in data


@pytest.mark.parametrize(
    "payload",
    [
        {"client_name": "", "source": "site", "amount": 100},
        {"client_name": "Ivan", "source": "site", "amount": -1},
        {"client_name": "Ivan", "source": "site", "amount": "10.555"},
        {"client_name": "Ivan", "amount": 100},
    ],
)
def test_create_lead_invalid(client, payload):
    response = client.post("/leads", json=payload)
    assert response.status_code == 422


def test_list_leads(client, lead):
    client.post("/leads", json={"client_name": "Olga", "source": "telegram", "amount": 300})

    response = client.get("/leads")
    assert response.status_code == 200
    assert [item["client_name"] for item in response.json()] == ["Ivan", "Olga"]


def test_list_leads_filter_by_status(client, lead):
    other = client.post(
        "/leads", json={"client_name": "Olga", "source": "telegram", "amount": 300}
    ).json()
    client.patch(f"/leads/{other['id']}/status", json={"status": "in_progress"})

    response = client.get("/leads", params={"status": "in_progress"})
    assert [item["id"] for item in response.json()] == [other["id"]]


def test_list_leads_unknown_status(client):
    response = client.get("/leads", params={"status": "foo"})
    assert response.status_code == 422


def test_get_lead(client, lead):
    response = client.get(f"/leads/{lead['id']}")
    assert response.status_code == 200
    assert response.json() == lead


def test_get_lead_not_found(client):
    response = client.get("/leads/999")
    assert response.status_code == 404


def test_update_lead(client, lead):
    response = client.patch(f"/leads/{lead['id']}", json={"amount": "2000"})
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == "2000.00"
    # fields not sent in PATCH must stay the same
    assert data["client_name"] == "Ivan"
    assert data["source"] == "site"


def test_update_lead_status_not_allowed(client, lead):
    response = client.patch(f"/leads/{lead['id']}", json={"status": "won"})
    assert response.status_code == 422
    assert client.get(f"/leads/{lead['id']}").json()["status"] == "new"


def test_update_lead_not_found(client):
    response = client.patch("/leads/999", json={"amount": "2000"})
    assert response.status_code == 404


def test_delete_lead(client, lead):
    response = client.delete(f"/leads/{lead['id']}")
    assert response.status_code == 204
    assert client.get(f"/leads/{lead['id']}").status_code == 404


def test_delete_lead_not_found(client):
    response = client.delete("/leads/999")
    assert response.status_code == 404
