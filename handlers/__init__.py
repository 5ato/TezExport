__all__ = [
    'users_converset'
]


from telegram import Update
from telegram.ext import (
    CallbackContext, CommandHandler, filters, CallbackQueryHandler,
    ConversationHandler, MessageHandler,
)

from .users import (
    CONTACT, LOCATION, FMO_TYPING, callback_update_profile,
    get_contact, get_fmo, get_location, start, stop
)

users_converset = ConversationHandler(
    entry_points=[
        CommandHandler(['start'], callback=start), CallbackQueryHandler(callback_update_profile, pattern='change_profile'),
    ],
    states={
        FMO_TYPING: [MessageHandler(filters.ALL, callback=get_fmo)],
        CONTACT: [MessageHandler(filters.CONTACT, callback=get_contact)],
        LOCATION: [MessageHandler(filters.LOCATION, callback=get_location)],
    },
    fallbacks=[MessageHandler(filters.Text(['stop']), callback=stop)],
    per_message=False
)
