import qrcode
from io import BytesIO
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse, Response
from ..models import qr_code_query, qr_code_response
from ..tariffs import get_tariff_price

router = APIRouter(prefix="/qr_code", tags=["QR Code"])

# Генерация QR кода в байтах
def generate_qr_code(data: str) -> BytesIO:
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    bio = BytesIO()
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio


# Трансляция изображения QR кода в бота
@router.post("/image")
async def get_qr_code_image(
    query: qr_code_query
):
    try:
        # Подготовить данные для QR кода
        qr_data = f"tarif{query.tarif}, tarif_price:{get_tariff_price(query.tarif)}"
        # Генерация QR кода
        qr_image = generate_qr_code(qr_data)
        
        return StreamingResponse(
            qr_image, 
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename=qr_code_{query.user_id}_{query.tarif}.png"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating QR code: {str(e)}")

