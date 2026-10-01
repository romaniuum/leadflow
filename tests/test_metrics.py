def test_metrics(client, lead):
    client.get(f"/leads/{lead['id']}")

    response = client.get("/metrics")
    assert response.status_code == 200
    # path is the route template, not the real id, so metrics don't grow per lead
    assert 'handler="/leads/{lead_id}"' in response.text
    assert "http_request_duration_seconds" in response.text
