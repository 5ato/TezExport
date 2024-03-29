from sqlalchemy import update, select, insert
from sqlalchemy.exc import PendingRollbackError

from telegram.ext import ContextTypes

from database import Fermer
from .service import Service


class FermersService(Service):

    def get(self, telegram_id: int) -> Fermer:
        try:
            _ = self.session.connection()
        except PendingRollbackError:
            self.session.rollback()
        return self.session.execute(select(Fermer).where(Fermer.telegram_id==telegram_id)).scalar()
    
    def get_only_language(self, telegram_id: int) -> str:
        return self.session.execute(select(Fermer.language).where(Fermer.telegram_id==telegram_id)).scalar()
    
    def get_by_username(self, username: str) -> Fermer:
        return self.session.execute(select(Fermer).where(Fermer.username==username)).scalar()

    def create(self, data: ContextTypes.DEFAULT_TYPE.user_data) -> None:
        self.session.execute(insert(Fermer).values(**data))
        self.session.commit()

    def update(self, telegram_id: int, data: dict) -> None:
        self.session.execute(update(Fermer).where(Fermer.telegram_id==telegram_id).values(**data))
        self.session.commit()
        