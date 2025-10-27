''' Модуль для объединения всех роутов '''
from fastapi import APIRouter

from app.presentation.api.payments import router as payments_router
from app.presentation.api.tariffs import router as tariffs_router

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "QR-Blockchain Server is running"}

router.include_router(payments_router)
router.include_router(tariffs_router)