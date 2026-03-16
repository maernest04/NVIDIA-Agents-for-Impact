"""
Tests for GET /resources/ and GET /resources/{id}.

Uses an in-memory SQLite DB (see conftest.py) — never touches campus_resources.db.
Run with: python3 -m pytest tests/test_resources.py -v -s
"""
import json


def _dump(label: str, url: str, data) -> None:
    print(f"\n{'─' * 60}")
    print(f"  QUERY : {url}")
    print(f"  {label}")
    print(f"{'─' * 60}")
    print(json.dumps(data, indent=2))


class TestListResources:
    def test_returns_all_resources(self, client):
        url = "/resources/"
        response = client.get(url)
        data = response.json()
        _dump(f"All resources ({len(data)} total)", url, data)

        assert response.status_code == 200
        assert len(data) == 7

    def test_each_resource_has_required_fields(self, client):
        url = "/resources/"
        response = client.get(url)
        data = response.json()
        _dump("Field check — every record", url, [list(r.keys()) for r in data])

        for item in data:
            assert "id" in item
            assert "resource_name" in item
            assert "phone_number" in item
            assert "email" in item
            assert "description" in item

    def test_search_by_name_exact_substring(self, client):
        url = "/resources/?search=CAPS"
        response = client.get(url)
        data = response.json()
        _dump("Search: name substring 'CAPS'", url, data)

        assert response.status_code == 200
        assert len(data) == 1
        assert "Counseling and Psychological Services" in data[0]["resource_name"]

    def test_search_by_name_case_insensitive(self, client):
        url = "/resources/?search=caps"
        response = client.get(url)
        data = response.json()
        _dump("Search: lowercase 'caps' (case-insensitive)", url, data)

        assert response.status_code == 200
        assert any("Counseling" in r["resource_name"] for r in data)

    def test_search_by_description_keyword(self, client):
        url = "/resources/?search=financial aid"
        response = client.get(url)
        data = response.json()
        _dump("Search: description keyword 'financial aid'", url, data)

        assert response.status_code == 200
        names = [r["resource_name"] for r in data]
        assert "Financial Aid and Scholarship Office (FASO)" in names

    def test_search_matches_multiple_resources(self, client):
        url = "/resources/?search=students"
        response = client.get(url)
        data = response.json()
        _dump(f"Search: 'students' — {len(data)} match(es)", url, data)

        assert response.status_code == 200
        assert len(data) > 1

    def test_search_no_match_returns_empty_list(self, client):
        url = "/resources/?search=xyznonexistent123"
        response = client.get(url)
        data = response.json()
        _dump("Search: no match", url, data)

        assert response.status_code == 200
        assert data == []

    def test_search_crisis_returns_hotline(self, client):
        url = "/resources/?search=crisis"
        response = client.get(url)
        data = response.json()
        _dump("Search: 'crisis' — crisis hotlines", url, data)

        assert response.status_code == 200
        names = [r["resource_name"] for r in data]
        assert any("Crisis" in n for n in names)

    def test_search_domestic_violence_returns_hotline(self, client):
        url = "/resources/?search=domestic violence"
        response = client.get(url)
        data = response.json()
        _dump("Search: 'domestic violence'", url, data)

        assert response.status_code == 200
        assert len(data) == 1
        assert data[0]["resource_name"] == "National Domestic Violence Hotline"
        assert data[0]["phone_number"] == "1-800-799-7233"

    def test_search_lgbtq_returns_pride_center(self, client):
        url = "/resources/?search=LGBTQ"
        response = client.get(url)
        data = response.json()
        _dump("Search: 'LGBTQ'", url, data)

        assert response.status_code == 200
        names = [r["resource_name"] for r in data]
        assert "PRIDE Center" in names

    def test_search_food_returns_sjsu_cares(self, client):
        url = "/resources/?search=food"
        response = client.get(url)
        data = response.json()
        _dump("Search: 'food'", url, data)

        assert response.status_code == 200
        names = [r["resource_name"] for r in data]
        assert "SJSU Cares" in names

    def test_empty_search_param_returns_all(self, client):
        url = "/resources/?search="
        response = client.get(url)
        data = response.json()
        _dump(f"Search: empty string — {len(data)} record(s)", url, data)

        assert response.status_code == 200
        assert len(data) == 7


class TestGetResourceById:
    def test_get_first_resource(self, client):
        url = "/resources/1"
        response = client.get(url)
        data = response.json()
        _dump("GET by ID: 1 (CAPS)", url, data)

        assert response.status_code == 200
        assert data["id"] == 1
        assert data["resource_name"] == "Counseling and Psychological Services (CAPS)"
        assert data["phone_number"] == "408-924-5678"
        assert data["email"] == "studentwellnesscenter@sjsu.edu"

    def test_get_crisis_lifeline_resource(self, client):
        url = "/resources/4"
        response = client.get(url)
        data = response.json()
        _dump("GET by ID: 4 (988 Lifeline)", url, data)

        assert response.status_code == 200
        assert data["resource_name"] == "988 Suicide & Crisis Lifeline"
        assert data["phone_number"] == "988"

    def test_get_sjsu_cares_resource(self, client):
        url = "/resources/7"
        response = client.get(url)
        data = response.json()
        _dump("GET by ID: 7 (SJSU Cares)", url, data)

        assert response.status_code == 200
        assert data["resource_name"] == "SJSU Cares"
        assert "food" in data["description"].lower()
        assert "housing" in data["description"].lower()

    def test_not_found_returns_404(self, client):
        url = "/resources/9999"
        response = client.get(url)
        data = response.json()
        _dump("GET by ID: 9999 (not found)", url, data)

        assert response.status_code == 404
        assert data["detail"] == "Resource not found"

    def test_zero_id_returns_404(self, client):
        url = "/resources/0"
        response = client.get(url)
        data = response.json()
        _dump("GET by ID: 0 (not found)", url, data)

        assert response.status_code == 404

    def test_response_contains_all_fields(self, client):
        url = "/resources/2"
        response = client.get(url)
        data = response.json()
        _dump("GET by ID: 2 — field check", url, data)

        assert response.status_code == 200
        assert set(data.keys()) == {"id", "resource_name", "phone_number", "email", "description"}
