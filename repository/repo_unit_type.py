from sqlalchemy import select

from database import UnitTypes
from .service import Service

from typing import Sequence


class UnitTypeService(Service):
    def get_all(self) -> Sequence[UnitTypes] | None:
        return self.session.execute(select(UnitTypes)).scalars().all()
