from src.app import activities

ACTIVITY = "Chess Club"
EMAIL = "new.student@mergington.edu"


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_with_expected_fields(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert set(data) == set(activities)
    for details in data.values():
        assert {"description", "schedule", "max_participants", "participants"} <= set(details)


def test_signup_success(client):
    response = client.post(f"/activities/{ACTIVITY}/signup", params={"email": EMAIL})
    assert response.status_code == 200
    assert EMAIL in response.json()["message"]
    assert EMAIL in client.get("/activities").json()[ACTIVITY]["participants"]


def test_signup_unknown_activity(client):
    response = client.post("/activities/Nope/signup", params={"email": EMAIL})
    assert response.status_code == 404


def test_signup_duplicate_rejected(client):
    client.post(f"/activities/{ACTIVITY}/signup", params={"email": EMAIL})
    response = client.post(f"/activities/{ACTIVITY}/signup", params={"email": EMAIL})
    assert response.status_code == 400
    assert activities[ACTIVITY]["participants"].count(EMAIL) == 1


def test_signup_full_activity_rejected(client):
    activities[ACTIVITY]["max_participants"] = 1
    activities[ACTIVITY]["participants"] = ["first@mergington.edu"]
    response = client.post(f"/activities/{ACTIVITY}/signup", params={"email": EMAIL})
    assert response.status_code == 400
    assert EMAIL not in activities[ACTIVITY]["participants"]


def test_signup_requires_email(client):
    response = client.post(f"/activities/{ACTIVITY}/signup")
    assert response.status_code == 422


def test_unregister_success(client):
    client.post(f"/activities/{ACTIVITY}/signup", params={"email": EMAIL})
    response = client.delete(f"/activities/{ACTIVITY}/participants", params={"email": EMAIL})
    assert response.status_code == 200
    assert EMAIL not in activities[ACTIVITY]["participants"]


def test_unregister_unknown_activity(client):
    response = client.delete("/activities/Nope/participants", params={"email": EMAIL})
    assert response.status_code == 404


def test_unregister_participant_not_registered(client):
    response = client.delete(f"/activities/{ACTIVITY}/participants", params={"email": EMAIL})
    assert response.status_code == 404


def test_unregister_requires_email(client):
    response = client.delete(f"/activities/{ACTIVITY}/participants")
    assert response.status_code == 422


def test_can_signup_again_after_unregister(client):
    client.post(f"/activities/{ACTIVITY}/signup", params={"email": EMAIL})
    client.delete(f"/activities/{ACTIVITY}/participants", params={"email": EMAIL})
    response = client.post(f"/activities/{ACTIVITY}/signup", params={"email": EMAIL})
    assert response.status_code == 200
