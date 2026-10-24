from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.redis import ping_redis
from backend.app.schemas import HealthStatus

router = APIRouter()


@router.get("/health", response_model=HealthStatus)
def check_health(db: Session = Depends(get_db)):
    """
    Health check endpoint verifying:
    1. FastAPI application execution
    2. MySQL relational database connectivity (via SQLAlchemy)
    3. Redis Stack vector database connectivity
    """
    mysql_ok = False
    try:
        db.execute(text("SELECT 1"))
        mysql_ok = True
    except Exception:
        mysql_ok = False

    redis_ok = ping_redis()

    return HealthStatus(
        status="healthy" if (mysql_ok and redis_ok) else "degraded",
        environment=settings.ENVIRONMENT,
        mysql_connected=mysql_ok,
        redis_connected=redis_ok,
        timestamp=datetime.now(timezone.utc),
    )
