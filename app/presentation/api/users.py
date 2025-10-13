from fastapi import APIRouter, Depends, HTTPException, Request

from app.presentation.api.models import UserCreateRequest, UserDeleteResponse, UserOut
from app.application.container import ServicesContainer

router = APIRouter(prefix="/users", tags=["users"])

def get_container(request: Request) -> ServicesContainer:
    return request.app.state.container 

@router.post("/", response_model=UserOut)
async def init_user(user_data: UserCreateRequest, container: ServicesContainer = Depends(get_container)):    
    user_service = container.get_users_service()
    return await user_service.init_user(user_data.user_id)

@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int, container: ServicesContainer = Depends(get_container)):
    user_service = container.get_users_service()
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

@router.delete("/{user_id}", response_model=UserDeleteResponse)
async def delete_user(user_id: int, container: ServicesContainer = Depends(get_container)):
    user_service = container.get_users_service()
    success = await user_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return UserDeleteResponse(detail="Пользователь удалён")
