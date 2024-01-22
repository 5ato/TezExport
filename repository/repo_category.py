from sqlalchemy import select, insert, update
from sqlalchemy.orm import joinedload

from database import Good_Category
from .service import Service

from typing import Sequence


class CategoryService(Service):
    def get(self, name: str) -> Good_Category:
        return self.session.execute(select(Good_Category).where(Good_Category.goods_categories_name==name)).scalar()
    
    def get_all_with_goods(self) -> Sequence[Good_Category]:
        return self.session.execute(select(Good_Category).options(joinedload(Good_Category.goods))).unique().scalars().all()
    
    def get_all(self) -> Sequence[str]:
        return self.session.execute(select(Good_Category.goods_categories_name)).scalars().all()
    