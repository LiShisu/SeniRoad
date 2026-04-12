from fastapi import APIRouter, Depends
from app.database import get_db
from app.dependencies import get_current_user
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/")
async def list_destinations(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取目的地列表"""
    pass

@router.post("/")
async def create_destination(
    dest_data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建目的地"""
    pass
