from fastapi import APIRouter
from app.api.endpoints import categories, medicines, ai, invoices, batches, auth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(medicines.router, prefix="/medicines", tags=["Medicines"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Integration"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["Invoices / POS"])
api_router.include_router(batches.router, prefix="/batches", tags=["Inventory Batches"])