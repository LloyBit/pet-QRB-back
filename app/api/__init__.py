from .monitoring import router as monitoring_router
from .users import router as users_router
from .payments import router as payments_router
from .tariffs import router as tariffs_router
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "QR Payment Server is running"}

router.include_router(monitoring_router)
router.include_router(users_router)
router.include_router(payments_router)
router.include_router(tariffs_router)