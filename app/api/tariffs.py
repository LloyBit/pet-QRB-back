from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..infrastructure.db.postgres.database import get_session
from ..models import PatchTariffModel, TariffCreate, TariffRead
from ..services.container import ServicesContainer

router = APIRouter(prefix="/tariffs", tags=["tariffs"])

# Инициализируем контейнер
container = ServicesContainer()

@router.post("/", response_model=TariffRead)
async def create_tariff(tariff: TariffCreate, session: AsyncSession = Depends(get_session)):
    tariffs_service = container.get_tariffs_service()
    return await tariffs_service.create(session, tariff)

@router.get("/", response_model=list[TariffRead])
async def all_tariffs(session: AsyncSession = Depends(get_session)):
    tariffs_service = container.get_tariffs_service()
    return await tariffs_service.get_all(session)

@router.get("/{name}", response_model=TariffRead | None)
async def get_tariff_by_name(name: str, session: AsyncSession = Depends(get_session)):
    tariffs_service = container.get_tariffs_service()
    return await tariffs_service.get_by_name(session, name)

@router.patch("/{name}", response_model=TariffRead)
async def update_tariff(name: str, tariff_data: PatchTariffModel, session: AsyncSession = Depends(get_session)):
    tariffs_service = container.get_tariffs_service()
    return await tariffs_service.update(session, name, tariff_data)

@router.delete("/{name}")
async def delete_tariffs_by_name(name: str, session: AsyncSession = Depends(get_session)):
    tariffs_service = container.get_tariffs_service()
    deleted_count = await tariffs_service.delete_by_name(session, name)
    return {"detail": f"{deleted_count} тариф(ов) с именем '{name}' удалено успешно"}
