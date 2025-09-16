from fastapi import APIRouter, HTTPException

from ..application.container import ServicesContainer
from ..models import TariffCreate, TariffRead, PatchTariffModel

router = APIRouter(prefix="/tariffs", tags=["tariffs"])

# Инициализируем контейнер
container = ServicesContainer()

@router.post("/", response_model=TariffRead)
async def create_tariff(tariff: TariffCreate):
    tariffs_service = container.get_tariffs_service()
    return await tariffs_service.create(tariff)

@router.get("/", response_model=list[TariffRead])
async def all_tariffs():
    tariffs_service = container.get_tariffs_service()
    return await tariffs_service.get_all()

@router.get("/{name}", response_model=TariffRead)
async def get_tariff_by_name(name: str):
    tariffs_service = container.get_tariffs_service()
    tariff = await tariffs_service.get_by_name(name)
    if not tariff:
        raise HTTPException(status_code=404, detail="Тариф не найден")
    return tariff

@router.patch("/{name}", response_model=TariffRead)
async def update_tariff(name: str, tariff_data: PatchTariffModel):
    tariffs_service = container.get_tariffs_service()
    return await tariffs_service.update(name, tariff_data)

@router.delete("/{name}")
async def delete_tariffs_by_name(name: str):
    tariffs_service = container.get_tariffs_service()
    return await tariffs_service.delete_by_name(name)
