import pytest

from app.routers.analytics import conversion

PATH_TO = {
    "new": [],
    "in_progress": ["in_progress"],
    "won": ["in_progress", "won"],
    "lost": ["in_progress", "lost"],
}


def make_lead(client, source, amount, status):
    lead = client.post(
        "/leads", json={"client_name": "Client", "source": source, "amount": amount}
    ).json()
    for step in PATH_TO[status]:
        client.patch(f"/leads/{lead['id']}/status", json={"status": step})


@pytest.fixture
def leads(client):
    make_lead(client, "site", "1000", "won")
    make_lead(client, "site", "500.50", "won")
    make_lead(client, "site", "200", "lost")
    make_lead(client, "telegram", "300", "in_progress")
    make_lead(client, "instagram", "100", "new")


@pytest.mark.parametrize(
    "won, lost, expected",
    [(0, 0, None), (1, 0, 100.0), (0, 3, 0.0), (2, 1, 66.7), (1, 2, 33.3)],
)
def test_conversion(won, lost, expected):
    assert conversion(won, lost) == expected


def test_funnel(client, leads):
    response = client.get("/analytics/funnel")
    assert response.status_code == 200
    assert response.json() == {
        "total": 5,
        "by_status": {"new": 1, "in_progress": 1, "won": 2, "lost": 1},
        "conversion_percent": 66.7,
    }


def test_funnel_empty(client):
    response = client.get("/analytics/funnel")
    assert response.json() == {
        "total": 0,
        "by_status": {"new": 0, "in_progress": 0, "won": 0, "lost": 0},
        "conversion_percent": None,
    }


def test_sources(client, leads):
    response = client.get("/analytics/sources")
    assert response.status_code == 200
    assert response.json() == [
        {
            "source": "site",
            "total": 3,
            "won": 2,
            "won_amount": "1500.50",
            "conversion_percent": 66.7,
        },
        {
            "source": "instagram",
            "total": 1,
            "won": 0,
            "won_amount": "0.00",
            "conversion_percent": None,
        },
        {
            "source": "telegram",
            "total": 1,
            "won": 0,
            "won_amount": "0.00",
            "conversion_percent": None,
        },
    ]


def test_sources_empty(client):
    response = client.get("/analytics/sources")
    assert response.json() == []
