from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.api.v1.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

from fastapi import Request, status
from fastapi.responses import JSONResponse

# Configure Cross-Origin Resource Sharing (CORS) for Next.js frontend
origins = list(settings.BACKEND_CORS_ORIGINS or [])
for o in ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"]:
    if o not in origins:
        origins.append(o)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


import logging

logger = logging.getLogger("fitcheck.backend")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Logs full exception diagnostics to backend console and returns safe error with CORS headers."""
    logger.error(f"Unhandled backend exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    origin = request.headers.get("origin")
    headers = {}
    if origin:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
        headers["Access-Control-Allow-Methods"] = "*"
        headers["Access-Control-Allow-Headers"] = "*"

    # Provide safe, user-friendly error without leaking sensitive internals/passwords to the client
    err_str = str(exc).lower()
    if "operationalerror" in err_str or "access denied" in err_str or "mysql" in err_str or "database" in err_str:
        user_detail = "Database connection failed. Please check the development database configuration."
    else:
        user_detail = "An internal server error occurred. Please check backend service logs."

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": user_detail},
        headers=headers,
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "message": "FitCheck API is running.",
        "docs_url": f"{settings.API_V1_STR}/docs",
        "health_check": f"{settings.API_V1_STR}/health",
    }
