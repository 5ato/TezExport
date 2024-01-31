from sqlalchemy import select, insert

from database import Good
from .service import Service


class GoodsService(Service):
    def get(self, name: str) -> Good:
        return self.session.execute(select(Good).where(Good.goods_name==name)).scalar()

    def create(self, name: str, id_category: int) -> None:
        data = {
            'goods_name': name,
            'islicensable': True,
            'isclientrestricted': True,
            'goods_categories_id': id_category
        }
        self.session.execute(insert(Good).values(**data))
        self.session.commit()
        return self.get(name)