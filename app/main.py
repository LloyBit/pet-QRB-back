from fastapi import FastAPI
from .api.qr_code import router as qr_code_router
from .api.check_payment import router as check_payment_router


app = FastAPI(title="QR Payment Server", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "QR Payment Server is running"}

# Include all API routers
app.include_router(qr_code_router)
app.include_router(check_payment_router)
