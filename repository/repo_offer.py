from sqlalchemy import insert, select, delete, update

from typing import Sequence

from .service import Service
from database import Offer, Fermer, Good, Good_Category


class OfferService(Service):
    def create(self, data) -> None:
        self.session.execute(insert(Offer).values(**data))
        self.session.commit()
        
    def get_full_join(self, id: int) -> Offer:
        return self.session.execute(
            select(
                Offer
            ).where(Offer.id==id)\
            .join_from(Offer, Good, Offer.goods_id==Good.id)\
            .join_from(Good, Good_Category, Good.goods_categories_id==Good_Category.id)
        ).scalar()
        
    def update(self, id: int, data: dict) -> None:
        self.session.execute(update(Offer).where(Offer.id==id).values(**data))
        self.session.commit()

    def get_list_from_user(self, telegram_id: int) -> Sequence[Offer]:
        return self.session.execute(select(Offer).where(
            Offer.fermer_id==select(Fermer.id)\
            .where(Fermer.telegram_id==telegram_id).scalar_subquery()
        ).join_from(Offer, Good, Offer.goods_id==Good.id).join_from(
            Good, Good_Category, Good.goods_categories_id==Good_Category.id)).scalars().all()
        
    def delete(self, id: int) -> None:
        self.session.execute(delete(Offer).where(Offer.id==id))
        self.session.commit()
    