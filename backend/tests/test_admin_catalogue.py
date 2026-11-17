from datetime import date

import pytest
from sqlalchemy import event, select, text

from backend.app.core.security import create_access_token
from backend.app.models import Garment, GarmentSize, GarmentMeasurement, FitReview, Purchase


def headers(role="ADMIN"):
    return {"Authorization": "Bearer " + create_access_token(subject=1 if role == "ADMIN" else 2, role=role)}


@pytest.fixture(autouse=True)
def enforce_database_foreign_keys(db_session):
    # Existing fixtures use SQLite; enable actual database FKs only for these tests.
    db_session.execute(text("PRAGMA foreign_keys = ON"))
    assert db_session.execute(text("PRAGMA foreign_keys")).scalar() == 1
    yield
    db_session.rollback()
    db_session.execute(text("PRAGMA foreign_keys = OFF"))


def new_garment(db_session):
    row = Garment(brand_id=1, garment_name="CODEX isolated garment", garment_category="Trousers", fit_type="STRAIGHT")
    db_session.add(row)
    db_session.commit()
    return row.garment_id


def test_admin_adds_size_and_database_rejects_duplicate(client, db_session):
    garment_id = new_garment(db_session)
    path = f"/api/v1/admin/garments/{garment_id}/sizes"
    response = client.post(path, headers=headers(), json={"size_label": " CODEX-SIZE "})
    assert response.status_code == 201
    assert response.json()["size_label"] == "CODEX-SIZE"
    assert response.json()["garment_id"] == garment_id
    assert client.post(path, headers=headers(), json={"size_label": "CODEX-SIZE"}).status_code == 409


def test_admin_adds_measurements_and_duplicate_is_friendly(client, db_session):
    garment_id = new_garment(db_session)
    size_id = client.post(f"/api/v1/admin/garments/{garment_id}/sizes", headers=headers(), json={"size_label": "CODEX-SIZE"}).json()["garment_size_id"]
    path = f"/api/v1/admin/garment-sizes/{size_id}/measurements"
    for kind, value in [("waist", 72), ("hip", 98)]:
        response = client.post(path, headers=headers(), json={"measurement_type": kind, "measurement_value": value, "unit": "cm"})
        assert response.status_code == 201
    response = client.post(path, headers=headers(), json={"measurement_type": "waist", "measurement_value": 75, "unit": "cm"})
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_user_cannot_write_catalogue(client):
    for method, path, payload in [
        ("post", "/admin/garments/1/sizes", {"size_label": "CODEX"}),
        ("post", "/admin/garment-sizes/1/measurements", {"measurement_type": "waist", "measurement_value": 72, "unit": "cm"}),
        ("delete", "/admin/garment-sizes/1", None),
        ("delete", "/admin/garments/1", None),
    ]:
        response = getattr(client, method)("/api/v1" + path, headers=headers("USER"), **({"json": payload} if payload else {}))
        assert response.status_code == 403
    assert client.delete("/api/v1/admin/garments/1").status_code == 401


def test_size_delete_uses_only_parent_sql_and_database_cascade(client, db_session):
    garment_id = new_garment(db_session)
    size = GarmentSize(garment_id=garment_id, size_label="CODEX-CASCADE")
    db_session.add(size)
    db_session.flush()
    size_id = size.garment_size_id
    db_session.add_all([GarmentMeasurement(garment_size_id=size_id, measurement_type=kind, measurement_value=value, unit="cm") for kind, value in [("waist", 72), ("hip", 98)]])
    db_session.commit()
    # Even when children are loaded, Core parent deletion must bypass ORM cascades.
    assert len(size.measurements) == 2
    statements = []
    def capture(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("DELETE"):
            statements.append(statement)
    event.listen(db_session.bind, "before_cursor_execute", capture)
    try:
        assert client.delete(f"/api/v1/admin/garment-sizes/{size_id}", headers=headers()).status_code == 200
    finally:
        event.remove(db_session.bind, "before_cursor_execute", capture)
    assert len(statements) == 1
    assert "GARMENT_SIZE" in statements[0] and "GARMENT_MEASUREMENT" not in statements[0]
    assert not db_session.execute(select(GarmentMeasurement).where(GarmentMeasurement.garment_size_id == size_id)).all()
    assert not db_session.execute(select(GarmentSize).where(GarmentSize.garment_size_id == size_id)).all()


def test_garment_delete_is_restricted_without_removing_sizes(client, db_session):
    garment_id = new_garment(db_session)
    row = GarmentSize(garment_id=garment_id, size_label="CODEX-RESTRICT")
    db_session.add(row)
    db_session.commit()
    size_id = row.garment_size_id
    response = client.delete(f"/api/v1/admin/garments/{garment_id}", headers=headers())
    assert response.status_code == 409
    assert "still has catalogue sizes" in response.json()["detail"]
    assert db_session.get(Garment, garment_id) is not None
    assert db_session.get(GarmentSize, size_id) is not None


def test_garment_delete_without_children_succeeds(client, db_session):
    garment_id = new_garment(db_session)
    assert client.delete(f"/api/v1/admin/garments/{garment_id}", headers=headers()).status_code == 200
    assert db_session.execute(select(Garment).where(Garment.garment_id == garment_id)).first() is None


@pytest.mark.parametrize("reference", ["purchase", "review"])
def test_size_delete_preserves_referenced_data(client, db_session, reference):
    garment_id = new_garment(db_session)
    row = GarmentSize(garment_id=garment_id, size_label="CODEX-REFERENCED")
    db_session.add(row)
    db_session.flush()
    size_id = row.garment_size_id
    if reference == "purchase":
        child = Purchase(user_id=2, garment_size_id=size_id, purchase_date=date.today(), outcome="KEPT")
    else:
        child = FitReview(user_id=2, garment_size_id=size_id, overall_fit="TRUE_TO_SIZE", review_text="CODEX isolated review")
    db_session.add(child)
    db_session.commit()
    response = client.delete(f"/api/v1/admin/garment-sizes/{size_id}", headers=headers())
    assert response.status_code == 409
    assert "purchases or fit reviews" in response.json()["detail"]
    assert db_session.get(GarmentSize, size_id) is not None
    assert db_session.query(type(child)).filter_by(garment_size_id=size_id).count() == 1


def test_invalid_measurements_and_blank_sizes_are_rejected(client):
    for payload in [{"measurement_type": "shoulder", "measurement_value": 72, "unit": "cm"},
                    {"measurement_type": "waist", "measurement_value": 0, "unit": "cm"},
                    {"measurement_type": "waist", "measurement_value": 72, "unit": "mm"},
                    {"measurement_type": "waist", "measurement_value": 72.123, "unit": "cm"}]:
        assert client.post("/api/v1/admin/garment-sizes/1/measurements", headers=headers(), json=payload).status_code == 422
    assert client.post("/api/v1/admin/garments/1/sizes", headers=headers(), json={"size_label": "  "}).status_code == 422


def test_missing_catalogue_rows_return_404(client):
    assert client.post("/api/v1/admin/garments/999999/sizes", headers=headers(), json={"size_label": "CODEX"}).status_code == 404
    assert client.post("/api/v1/admin/garment-sizes/999999/measurements", headers=headers(), json={"measurement_type": "waist", "measurement_value": 72, "unit": "cm"}).status_code == 404
    assert client.delete("/api/v1/admin/garment-sizes/999999", headers=headers()).status_code == 404
    assert client.delete("/api/v1/admin/garments/999999", headers=headers()).status_code == 404
