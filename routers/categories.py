from typing import Dict, List

from fastapi import APIRouter
from pydantic import BaseModel

from core.categories import list_categories

router = APIRouter(prefix="/categories", tags=["categories"])


class CategoryLabel(BaseModel):
    en: str
    fa: str


class CategoryItem(BaseModel):
    id: str
    label: CategoryLabel


@router.get("", response_model=List[CategoryItem])
def get_categories() -> List[Dict[str, object]]:
    """Return the canonical news category taxonomy."""
    return list_categories()
