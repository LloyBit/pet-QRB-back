from fastapi import APIRouter, HTTPException, Header

from ..application.container import ServicesContainer
from ..models import UserOut

router = APIRouter(prefix="/users", tags=["users"])

# Инициализируем контейнер
container = ServicesContainer()

@router.post("/", response_model=UserOut)
async def init_user(user_id: str = Header(alias="user_id")):
    try:
        user_id_int = int(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id in header")
    
    user_service = container.get_users_service()
    return await user_service.init_user(user_id_int)

@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int):
    user_service = container.get_users_service()
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

@router.patch("/{user_id}", response_model=UserOut)
async def change_user(user_id: int, user_data: UserOut):
    user_service = container.get_users_service()
    user = await user_service.change_user(user_id, user_data)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

@router.delete("/{user_id}")
async def delete_user(user_id: int):
    user_service = container.get_users_service()
    success = await user_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return {"detail": "Пользователь удалён"}
