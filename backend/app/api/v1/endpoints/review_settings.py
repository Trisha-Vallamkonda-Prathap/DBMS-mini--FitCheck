"""ADMIN-only extended review storage with a byte-safe return to standard capacity."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, StrictBool
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.api.deps import require_admin
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.models import User

router = APIRouter()

ALTER_REVIEW_TEXT = {
    False: "ALTER TABLE FIT_REVIEW MODIFY COLUMN review_text TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL",
    True: "ALTER TABLE FIT_REVIEW MODIFY COLUMN review_text MEDIUMTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL",
}
TEXT_MAX_BYTES = 65535
LOCK_NAME = "fitcheck.review_text.capacity"


class ReviewCapacityUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enabled: StrictBool


def read_review_column(connection):
    row = connection.execute(text("""
        SELECT TABLE_SCHEMA AS database_name, COLUMN_TYPE AS storage_type,
               CHARACTER_OCTET_LENGTH AS max_bytes, IS_NULLABLE AS nullable,
               CHARACTER_SET_NAME AS charset, COLLATION_NAME AS collation,
               COLUMN_DEFAULT AS column_default, EXTRA AS extra,
               COLUMN_COMMENT AS comment
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'FIT_REVIEW' AND COLUMN_NAME = 'review_text'
    """)).mappings().one_or_none()
    if row is None:
        raise HTTPException(409, "Review text column was not found in the configured database.")
    return dict(row)


def supported_column(column):
    # Refuse unexpected attributes rather than silently discarding them in MODIFY.
    return (
        column["storage_type"].lower() in ("text", "mediumtext")
        and column["max_bytes"] == {"text": TEXT_MAX_BYTES, "mediumtext": 16777215}[column["storage_type"].lower()]
        and column["nullable"] == "NO"
        and column["charset"] == "utf8mb4"
        and column["collation"] == "utf8mb4_0900_ai_ci"
        and column["column_default"] is None
        and not column["extra"] and not column["comment"]
    )


def capacity_result(column):
    return {
        "storage_type": column["storage_type"].upper(),
        "max_bytes": column["max_bytes"],
        "enabled": column["storage_type"].lower() == "mediumtext",
        "supported": supported_column(column),
        "updates_enabled": bool(settings.REVIEW_SETTINGS_DATABASE_URL),
    }


@router.get("/admin/review-settings")
def get_review_settings(
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return capacity_result(read_review_column(db.connection()))


@router.put("/admin/review-settings")
def update_review_settings(
    request: ReviewCapacityUpdate,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if not settings.REVIEW_SETTINGS_DATABASE_URL:
        raise HTTPException(503, "Review capacity updates require an administrative database connection.")
    expected_database = read_review_column(db.connection())["database_name"]
    admin_engine = create_engine(settings.REVIEW_SETTINGS_DATABASE_URL, echo=False)
    try:
        # MySQL DDL implicitly commits. Keep it off the runtime ORM connection.
        with admin_engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
            if connection.dialect.name != "mysql":
                raise HTTPException(409, "Review capacity updates require MySQL.")
            acquired = connection.execute(
                text("SELECT GET_LOCK(:name, 5)"), {"name": LOCK_NAME}
            ).scalar()
            if acquired != 1:
                raise HTTPException(409, "Another review capacity update is in progress. Try again.")
            try:
                before = read_review_column(connection)
                if before["database_name"] != expected_database:
                    raise HTTPException(409, "Administrative and runtime database names must match.")
                if not supported_column(before):
                    raise HTTPException(409, "The current review column definition is unsupported; no changes were made.")
                target_type = "mediumtext" if request.enabled else "text"
                if before["storage_type"].lower() == target_type:
                    return capacity_result(before)
                connection.execute(text("SET SESSION lock_wait_timeout = 5"))
                table_locked = False
                try:
                    if not request.enabled:
                        # Prevent inserts/updates between the byte-length check and ALTER.
                        connection.execute(text("LOCK TABLES FIT_REVIEW WRITE"))
                        table_locked = True
                        largest = connection.execute(text(
                            "SELECT COALESCE(MAX(OCTET_LENGTH(review_text)), 0) FROM FIT_REVIEW"
                        )).scalar_one()
                        if largest > TEXT_MAX_BYTES:
                            raise HTTPException(409, "Extended capacity cannot be disabled because one or more existing reviews exceed standard TEXT capacity (65,535 bytes).")
                    # Only these two complete, hard-coded ALTER statements are permitted.
                    connection.execute(text(ALTER_REVIEW_TEXT[request.enabled]))
                    after = read_review_column(connection)
                    if not supported_column(after) or after["storage_type"].lower() != target_type:
                        raise HTTPException(500, "The resulting review capacity could not be verified. Refresh the setting.")
                    return capacity_result(after)
                finally:
                    if table_locked:
                        connection.execute(text("UNLOCK TABLES"))
            finally:
                connection.execute(text("SELECT RELEASE_LOCK(:name)"), {"name": LOCK_NAME})
    except SQLAlchemyError:
        raise HTTPException(503, "Review capacity update failed. Check the administrative database connection and privileges, then refresh the setting.") from None
    finally:
        admin_engine.dispose()
