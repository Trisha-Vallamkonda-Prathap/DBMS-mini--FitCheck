from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import OperationalError

from backend.app.api.v1.endpoints import review_settings as api
from backend.app.core.security import create_access_token


BASE_COLUMN = {
    "database_name": "fitcheck", "storage_type": "text", "max_bytes": 65535,
    "nullable": "NO", "charset": "utf8mb4", "collation": "utf8mb4_0900_ai_ci",
    "column_default": None, "extra": "", "comment": "",
}
WIDENED_COLUMN = {**BASE_COLUMN, "storage_type": "mediumtext", "max_bytes": 16777215}
PATH = "/api/v1/admin/review-settings"


def headers(role="ADMIN"):
    return {"Authorization": "Bearer " + create_access_token(subject=1 if role == "ADMIN" else 2, role=role)}


def setup_alter(monkeypatch, current=None, target=None, largest=0):
    monkeypatch.setattr(api.settings, "REVIEW_SETTINGS_DATABASE_URL", "mysql+pymysql://configured")
    engine = MagicMock()
    connection = engine.connect.return_value.execution_options.return_value.__enter__.return_value
    connection.dialect.name = "mysql"
    connection.execute.return_value.scalar.return_value = 1
    connection.execute.return_value.scalar_one.return_value = largest
    monkeypatch.setattr(api, "create_engine", lambda *a, **kw: engine)
    column = current or BASE_COLUMN
    monkeypatch.setattr(api, "read_review_column", MagicMock(side_effect=[BASE_COLUMN, column, target or WIDENED_COLUMN]))
    return engine, connection


def test_user_cannot_read_or_update_capacity(client):
    for method in ["get", "put"]:
        response = getattr(client, method)(PATH, headers=headers("USER"), **({"json": {"enabled": True}} if method == "put" else {}))
        assert response.status_code == 403
    assert client.get(PATH).status_code == 401


def test_admin_reads_actual_capacity(client, monkeypatch):
    monkeypatch.setattr(api, "read_review_column", lambda connection: BASE_COLUMN)
    response = client.get(PATH, headers=headers())
    assert response.status_code == 200
    assert response.json()["max_bytes"] == 65535
    assert response.json()["enabled"] is False
    assert response.json()["supported"] is True


def test_admin_widens_only_review_text(client, monkeypatch):
    engine, connection = setup_alter(monkeypatch)
    response = client.put(PATH, headers=headers(), json={"enabled": True})
    assert response.status_code == 200
    assert response.json()["storage_type"] == "MEDIUMTEXT"
    assert response.json()["max_bytes"] == 16777215
    assert response.json()["enabled"] is True
    statements = [str(call.args[0]) for call in connection.execute.call_args_list]
    assert [s for s in statements if s.startswith("ALTER")] == [api.ALTER_REVIEW_TEXT[True]]
    assert "NOT NULL" in api.ALTER_REVIEW_TEXT[True]
    assert "COLLATE utf8mb4_0900_ai_ci" in api.ALTER_REVIEW_TEXT[True]
    assert statements[-1] == "SELECT RELEASE_LOCK(:name)"
    engine.dispose.assert_called_once()


@pytest.mark.parametrize("changed", [
    {"storage_type": "longtext", "max_bytes": 4294967295},
    {"nullable": "YES"}, {"collation": "utf8mb4_bin"},
    {"comment": "must preserve"}, {"database_name": "other_database"},
])
def test_never_discards_unsupported_column_attributes(client, monkeypatch, changed):
    _, connection = setup_alter(monkeypatch, {**BASE_COLUMN, **changed})
    response = client.put(PATH, headers=headers(), json={"enabled": True})
    assert response.status_code == 409
    assert not any(str(call.args[0]).startswith("ALTER") for call in connection.execute.call_args_list)


def test_request_whitelist_and_extra_fields(client):
    for payload in [{"enabled": "true"}, {"enabled": 1},
                    {"storage_type": "TEXT"}, {"enabled": True, "sql": "ALTER TABLE other"},
                    {"enabled": False, "column": "other"}]:
        assert client.put(PATH, headers=headers(), json=payload).status_code == 422


def test_missing_admin_connection(client, monkeypatch):
    monkeypatch.setattr(api.settings, "REVIEW_SETTINGS_DATABASE_URL", "")
    assert client.put(PATH, headers=headers(), json={"enabled": True}).status_code == 503


def test_lock_contention_prevents_alter(client, monkeypatch):
    _, connection = setup_alter(monkeypatch)
    connection.execute.return_value.scalar.return_value = 0
    assert client.put(PATH, headers=headers(), json={"enabled": True}).status_code == 409
    assert not any(str(call.args[0]).startswith("ALTER") for call in connection.execute.call_args_list)


def test_database_failure_does_not_expose_credentials(client, monkeypatch):
    _, connection = setup_alter(monkeypatch)
    connection.execute.side_effect = OperationalError("statement", {}, Exception("private credential"))
    response = client.put(PATH, headers=headers(), json={"enabled": True})
    assert response.status_code == 503
    assert "private credential" not in response.text


@pytest.mark.parametrize("largest", [0, 65535])
def test_safe_downgrade_locks_checks_bytes_and_preserves_attributes(client, monkeypatch, largest):
    _, connection = setup_alter(monkeypatch, WIDENED_COLUMN, BASE_COLUMN, largest)
    response = client.put(PATH, headers=headers(), json={"enabled": False})
    assert response.status_code == 200
    assert response.json()["enabled"] is False
    statements = [str(call.args[0]) for call in connection.execute.call_args_list]
    lock = statements.index("LOCK TABLES FIT_REVIEW WRITE")
    check = statements.index("SELECT COALESCE(MAX(OCTET_LENGTH(review_text)), 0) FROM FIT_REVIEW")
    alter = statements.index(api.ALTER_REVIEW_TEXT[False])
    unlock = statements.index("UNLOCK TABLES")
    assert lock < check < alter < unlock
    assert statements[-1] == "SELECT RELEASE_LOCK(:name)"


def test_oversized_review_blocks_downgrade_without_alter(client, monkeypatch):
    # 21,846 euro symbols fit in 21,846 characters, but require 65,538 UTF-8 bytes.
    _, connection = setup_alter(monkeypatch, WIDENED_COLUMN, BASE_COLUMN, len(("€" * 21846).encode("utf-8")))
    response = client.put(PATH, headers=headers(), json={"enabled": False})
    assert response.status_code == 409
    assert "exceed standard TEXT capacity" in response.json()["detail"]
    statements = [str(call.args[0]) for call in connection.execute.call_args_list]
    assert not any(s.startswith("ALTER") for s in statements)
    assert "UNLOCK TABLES" in statements


@pytest.mark.parametrize("enabled,column", [(False, BASE_COLUMN), (True, WIDENED_COLUMN)])
def test_matching_state_is_read_from_database_without_alter(client, monkeypatch, enabled, column):
    _, connection = setup_alter(monkeypatch, column)
    response = client.put(PATH, headers=headers(), json={"enabled": enabled})
    assert response.status_code == 200
    assert response.json()["enabled"] is enabled
    assert not any(str(call.args[0]).startswith("ALTER") for call in connection.execute.call_args_list)


def test_user_cannot_disable_extended_capacity(client):
    assert client.put(PATH, headers=headers("USER"), json={"enabled": False}).status_code == 403


def test_metadata_reads_mediumtext_as_enabled(client, monkeypatch):
    monkeypatch.setattr(api, "read_review_column", lambda connection: WIDENED_COLUMN)
    response = client.get(PATH, headers=headers())
    assert response.status_code == 200
    assert response.json()["enabled"] is True
    assert response.json()["storage_type"] == "MEDIUMTEXT"
