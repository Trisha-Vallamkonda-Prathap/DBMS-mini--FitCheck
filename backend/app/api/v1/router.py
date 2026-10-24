from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    health,
    auth,
    catalogue,
    profile,
    purchases,
    recommendations,
    reviews,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Member A Endpoints
api_router.include_router(catalogue.router, tags=["Catalogue"])
api_router.include_router(profile.router, tags=["Body Profile"])
api_router.include_router(purchases.router, tags=["Purchase History"])
api_router.include_router(recommendations.router, tags=["Recommendations"])

# Member B Endpoints
api_router.include_router(reviews.router, tags=["Fit Reviews & Semantic Search"])
