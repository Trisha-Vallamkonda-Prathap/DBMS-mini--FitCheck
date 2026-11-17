"""ADMIN-only, one-way widening of the existing review text attribute."""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.api.deps import require_admin
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.models import User

router = APIRouter()

ALTER_REVIEW_TEXT = (
    "ALTER TABLE FIT_REVIEW MODIFY COLUMN review_text MEDIUMTEXT "
    "CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL"
)
LOCK_NAME = "fitcheck.review_text.capacity"


class ReviewCapacityUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    storage_type: Literal["MEDIUMTEXT"]


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


def can_widen(column):
    # Refuse unexpected attributes rather than silently discarding them in MODIFY.
    return (
        column["storage_type"].lower() == "text"
        and column["max_bytes"] == 65535
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
        "available_upgrades": ["MEDIUMTEXT"] if can_widen(column) else [],
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
                if not can_widen(before):
                    raise HTTPException(409, "Review capacity is already increased or the column definition is unsupported.")
                connection.execute(text("SET SESSION lock_wait_timeout = 5"))
                # This is the only permitted ALTER. No request text is used in SQL.
                connection.execute(text(ALTER_REVIEW_TEXT))
                after = read_review_column(connection)
                if after["storage_type"].lower() != "mediumtext" or after["max_bytes"] != 16777215:
                    raise HTTPException(500, "The resulting review capacity could not be verified.")
                return capacity_result(after)
            finally:
                connection.execute(text("SELECT RELEASE_LOCK(:name)"), {"name": LOCK_NAME})
    except SQLAlchemyError:
        raise HTTPException(503, "Review capacity update failed. Check the administrative database connection and privileges, then refresh the setting.") from None
    finally:
        admin_engine.dispose()
