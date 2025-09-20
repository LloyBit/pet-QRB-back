from fastapi import APIRouter, HTTPException, Depends

from app.application.container import ServicesContainer
from app.presentation.api.models import UserOut, UserUpdateRequest, UserDeleteResponse, UserCreateRequest

router = APIRouter(prefix="/users", tags=["users"])

# Инициализируем контейнер
container = ServicesContainer()

# Dependency для получения сервиса
def get_user_service():
    return container.get_users_service()

@router.post("/", response_model=UserOut)
async def init_user(user_data: UserCreateRequest, user_service = Depends(get_user_service)):    
    return await user_service.init_user(user_data.user_id)

@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: str, user_service = Depends(get_user_service)):
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

@router.patch("/{user_id}", response_model=UserOut)
async def change_user(user_id: str, user_data: UserUpdateRequest, user_service = Depends(get_user_service)):
    user = await user_service.change_user(user_id, user_data)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

@router.delete("/{user_id}", response_model=UserDeleteResponse)
async def delete_user(user_id: str, user_service = Depends(get_user_service)):
    success = await user_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return UserDeleteResponse(detail="Пользователь удалён")
