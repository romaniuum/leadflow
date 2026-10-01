import pytest

STATUSES = ["new", "in_progress", "won", "lost"]
ALLOWED = {("new", "in_progress"), ("in_progress", "won"), ("in_progress", "lost")}

# how to bring a new lead to each status through the funnel
PATH_TO = {
    "new": [],
    "in_progress": ["in_progress"],
    "won": ["in_progress", "won"],
    "lost": ["in_progress", "lost"],
}


def set_status(client, lead_id, status):
    return client.patch(f"/leads/{lead_id}/status", json={"status": status})


@pytest.mark.parametrize("target", STATUSES)
@pytest.mark.parametrize("current", STATUSES)
def test_status_transition(client, lead, current, target):
    for status in PATH_TO[current]:
        assert set_status(client, lead["id"], status).status_code == 200

    response = set_status(client, lead["id"], target)

    if (current, target) in ALLOWED:
        assert response.status_code == 200
        assert response.json()["status"] == target
    else:
        assert response.status_code == 409
        assert client.get(f"/leads/{lead['id']}").json()["status"] == current


def test_status_unknown_value(client, lead):
    response = set_status(client, lead["id"], "foo")
    assert response.status_code == 422


def test_status_lead_not_found(client):
    response = set_status(client, 999, "in_progress")
    assert response.status_code == 404
