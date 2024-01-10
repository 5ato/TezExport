from telegram.ext import ApplicationBuilder, Defaults
from telegram.constants import ParseMode

from configuration import BotSettings
from handlers import users_converset

from datetime import timezone, timedelta


if __name__ == '__main__':
    defaults = Defaults(parse_mode=ParseMode.HTML, tzinfo=timezone(offset=timedelta(hours=5), name='UZ'))
    application = ApplicationBuilder().token(BotSettings.TOKEN).defaults(defaults).build()
    application.add_handler(users_converset)
    application.run_polling()
    