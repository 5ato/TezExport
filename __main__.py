from telegram.ext import ApplicationBuilder, Defaults
from telegram.constants import ParseMode

from configuration import BotSettings, DatabaseSettings
from handlers import handlers
from database import get_sessionmaker, get_engine
from repository import (
    FermersService, CategoryService, OfferService, GoodsService,
    UnitTypeService, PictureService
)

from datetime import timezone, timedelta


if __name__ == '__main__':
    defaults = Defaults(parse_mode=ParseMode.HTML, tzinfo=timezone(offset=timedelta(hours=5), name='UZ'))
    application = ApplicationBuilder().token(BotSettings.TOKEN).defaults(defaults).build()
    engine = get_engine(DatabaseSettings.full_name())
    session = get_sessionmaker(engine)()
    application.bot_data['fermer_service'] = FermersService(session)
    application.bot_data['category_service'] = CategoryService(session)
    application.bot_data['offer_service'] = OfferService(session)
    application.bot_data['goods_service'] = GoodsService(session)
    application.bot_data['unit_type_service'] = UnitTypeService(session)
    application.bot_data['picture_service'] = PictureService(session)
    application.add_handlers(handlers)
    application.run_polling()
    