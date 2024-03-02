from sqlalchemy import insert, select

from database import Picture
from .service import Service


class PictureService(Service):
    def create(self, data: dict) -> Picture:
        self.session.execute(insert(Picture).values(**data))
        self.session.commit()
        return self.session.execute(select(Picture.Id).order_by(Picture.Id.desc())).scalars().first()
