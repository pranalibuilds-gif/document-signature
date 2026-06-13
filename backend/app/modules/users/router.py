from fastapi import APIRouter, Depends
from app.core.deps import get_current_user
from app.modules.users.models import User
from app.modules.users.schemas import UserRead

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
