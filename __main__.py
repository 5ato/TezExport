from telegram.ext import ApplicationBuilder, Defaults
from telegram.constants import ParseMode

from configuration import BotSettings
from handlers import handlers

from datetime import timezone, timedelta


if __name__ == '__main__':
    defaults = Defaults(parse_mode=ParseMode.HTML, tzinfo=timezone(offset=timedelta(hours=5), name='UZ'))
    application = ApplicationBuilder().token(BotSettings.TOKEN).defaults(defaults).build()
    application.add_handlers(handlers)
    application.run_polling()
    