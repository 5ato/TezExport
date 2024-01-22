from sqlalchemy import insert

from .service import Service
from database import Offer


class OfferService(Service):
    def create(self, data) -> None:
        self.session.execute(insert(Offer).values(**data))
        self.session.commit()
