import pytest
from backend.app.core.security import create_access_token


def test_get_brands(client):
    """Tests GET /api/v1/brands returns all brands in catalogue."""
    response = client.get("/api/v1/brands")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    brand_names = [b["brand_name"] for b in data]
    assert "Levis" in brand_names
    assert "Zara" in brand_names


def test_get_garments_and_filter(client):
    """Tests GET /api/v1/garments and query param filtering."""
    # All garments
    response = client.get("/api/v1/garments")
    assert response.status_code == 200
    assert len(response.json()) >= 3

    # Filter by brand_id=1 (Levis)
    resp_filtered = client.get("/api/v1/garments?brand_id=1")
    assert resp_filtered.status_code == 200
    garments = resp_filtered.json()
    assert all(g["brand_id"] == 1 for g in garments)

    # Filter by category=Trousers
    resp_cat = client.get("/api/v1/garments?category=Trousers")
    assert resp_cat.status_code == 200
    assert all(g["garment_category"] == "Trousers" for g in resp_cat.json())


def test_get_garment_detail_and_sizes(client):
    """Tests GET /api/v1/garments/{id} and GET /api/v1/garments/{id}/sizes."""
    response = client.get("/api/v1/garments/1")
    assert response.status_code == 200
    data = response.json()
    assert data["garment_name"] == "Levis 501 Original"
    assert len(data["sizes"]) == 5

    # Sizes endpoint
    resp_sizes = client.get("/api/v1/garments/1/sizes")
    assert resp_sizes.status_code == 200
    sizes = resp_sizes.json()
    assert len(sizes) == 5
    size_labels = [s["size_label"] for s in sizes]
    assert "28" in size_labels

    # 404 for invalid garment
    resp_404 = client.get("/api/v1/garments/99999")
    assert resp_404.status_code == 404


def test_profile_lifecycle(client):
    """Tests GET /api/v1/profile and PUT /api/v1/profile."""
    token = create_access_token(subject=2, role="USER")
    headers = {"Authorization": f"Bearer {token}"}

    # Get profile for user 2 (Priya)
    get_res = client.get("/api/v1/profile", headers=headers)
    assert get_res.status_code == 200
    profile = get_res.json()
    assert profile["waist"] == 68.0

    # Update profile
    update_payload = {
        "waist": 69.0,
        "hip": 95.0,
        "preferred_fit": "TIGHT",
    }
    put_res = client.put("/api/v1/profile", json=update_payload, headers=headers)
    assert put_res.status_code == 200
    updated = put_res.json()
    assert updated["waist"] == 69.0
    assert updated["preferred_fit"] == "TIGHT"

    # Inconsistent measurements (hip < waist) should fail
    bad_payload = {"waist": 90.0, "hip": 70.0}
    bad_res = client.put("/api/v1/profile", json=bad_payload, headers=headers)
    assert bad_res.status_code == 422


def test_purchase_lifecycle(client):
    """Tests GET /api/v1/purchases and POST /api/v1/purchases."""
    token = create_access_token(subject=2, role="USER")
    headers = {"Authorization": f"Bearer {token}"}

    # View existing purchases
    get_res = client.get("/api/v1/purchases", headers=headers)
    assert get_res.status_code == 200
    purchases = get_res.json()
    assert len(purchases) >= 1
    assert purchases[0]["brand_name"] == "Levis"

    # Create new purchase
    new_purchase_payload = {
        "garment_size_id": 8,  # Zara 38
        "outcome": "KEPT",
        "fit_satisfaction": "GOOD",
        "fit_preference": "REGULAR",
    }
    post_res = client.post("/api/v1/purchases", json=new_purchase_payload, headers=headers)
    assert post_res.status_code == 201
    created = post_res.json()
    assert created["garment_size_id"] == 8
    assert created["brand_name"] == "Zara"

    # Invalid garment_size_id should return 404
    bad_purchase = {
        "garment_size_id": 99999,
        "outcome": "KEPT",
    }
    bad_res = client.post("/api/v1/purchases", json=bad_purchase, headers=headers)
    assert bad_res.status_code == 404


def test_recommendation_api_endpoint(client):
    """Tests POST /api/v1/recommendations endpoint."""
    token = create_access_token(subject=2, role="USER")
    headers = {"Authorization": f"Bearer {token}"}

    req_payload = {
        "target_garment_id": 2,  # Zara Z1975
    }
    response = client.post("/api/v1/recommendations", json=req_payload, headers=headers)
    assert response.status_code == 200
    rec = response.json()
    assert rec["target_garment_name"] == "Zara Z1975 Wide Leg"
    assert rec["target_brand_name"] == "Zara"
    assert rec["primary_recommendation"]["size_label"] == "38"
    assert len(rec["all_sizes_ranked"]) > 0
    assert "explanation" in rec
