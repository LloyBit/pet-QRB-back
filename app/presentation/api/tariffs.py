from fastapi import APIRouter, Depends, HTTPException, Request

from app.application.container import ServicesContainer
from app.presentation.api.models import (
    TariffActivateQuery,
    TariffCreate,
    TariffDeleteResponse,
    TariffRead,
    TariffUpdateRequest,
    TariffUpdateResponse,
)

router = APIRouter(prefix="/tariffs", tags=["tariffs"])

def get_container(request: Request) -> ServicesContainer:
    return request.app.state.container 

@router.post("/", response_model=TariffRead)
async def create_tariff(tariff: TariffCreate, container: ServicesContainer = Depends(get_container)):
    tariffs_service = container.get_tariffs_service()
    return await tariffs_service.create(tariff)

@router.get("/", response_model=list[TariffRead])
async def all_tariffs(container: ServicesContainer = Depends(get_container)):
    tariffs_service = container.get_tariffs_service()
    return await tariffs_service.get_all()

@router.get("/{name}", response_model=TariffRead)
async def get_tariff_by_name(name: str, container: ServicesContainer = Depends(get_container)):
    tariffs_service = container.get_tariffs_service()
    tariff = await tariffs_service.get_by_name(name)
    if not tariff:
        raise HTTPException(status_code=404, detail="Тариф не найден")
    return tariff

@router.patch("/{name}", response_model=TariffUpdateResponse)
async def update_tariff(name: str, tariff_data: TariffUpdateRequest, container: ServicesContainer = Depends(get_container)):
    tariffs_service = container.get_tariffs_service()
    updated_tariff = await tariffs_service.update(name, tariff_data)
    return TariffUpdateResponse(
        tariff_id=updated_tariff.tariff_id,
        name=updated_tariff.name,
        price=updated_tariff.price,
        features=updated_tariff.features
    )

@router.patch("/{name}/activation", response_model=TariffActivateQuery)
async def set_activate_tariff(name: str, tariff_data: TariffActivateQuery, container: ServicesContainer = Depends(get_container)):
    tariffs_service = container.get_tariffs_service()
    activated_tariff = await tariffs_service.set_activate(name, tariff_data)
    return TariffActivateQuery(
        is_active=activated_tariff.is_active
    )

@router.delete("/{name}", response_model=TariffDeleteResponse)
async def delete_tariffs_by_name(name: str, container: ServicesContainer = Depends(get_container)):
    tariffs_service = container.get_tariffs_service()
    result = await tariffs_service.delete_by_name(name)
    return TariffDeleteResponse(detail=result)
