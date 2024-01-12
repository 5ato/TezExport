__all__ = [
    'handlers'
]


from telegram.ext import (
    CommandHandler, filters, CallbackQueryHandler,
    ConversationHandler, MessageHandler,
)

from .users import (
    CONTACT, LOCATION, FMO_TYPING, callback_update_profile,
    get_contact, get_fmo, get_location, start, cancel, skip_location,
    callback_update_location, only_location
)
from .products import (
    CATEGORY, NAME, COUNT, PACKING, MIN_PART,
    MEDIA, PRICE_PER, SHIPMENT, VALIDITY, PER_PACKING,
    DESCRIPTION, LOCATION_PRODUCT, MESSANGER,
    callback_add_product, get_count, get_media, 
    get_min_part, get_name, get_packing, get_per_packing,
    get_price_per, get_shipment, callback_get_category
)


handlers = [
    ConversationHandler(
    entry_points=[
        CommandHandler(['start'], callback=start), CallbackQueryHandler(callback_update_profile, pattern='change_profile'),
    ],
    states={
        FMO_TYPING: [MessageHandler(filters.ALL, callback=get_fmo)],
        CONTACT: [MessageHandler(filters.CONTACT, callback=get_contact)],
        LOCATION: [MessageHandler(filters.LOCATION, callback=get_location), MessageHandler(filters.Text(['Пропустить']), skip_location)],
    },
    fallbacks=[MessageHandler(filters.Text(['stop']), callback=cancel)],
    per_message=False
    ),
    ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_update_location, pattern='change_location')],
        states={
            LOCATION: [MessageHandler(filters.LOCATION, callback=only_location), MessageHandler(filters.Text(['Отмена']), skip_location)]
        },
        fallbacks=[MessageHandler(filters.Text('stop'), callback=cancel)],
    ),
    CallbackQueryHandler(callback_update_location, pattern='change_location'),
    MessageHandler(filters.Text(['Отмена']), skip_location),
    ConversationHandler(
        entry_points=[
            CallbackQueryHandler(callback_add_product, pattern='add_product'),
        ],
        states= {
            CATEGORY: [CallbackQueryHandler(callback_get_category)],
            NAME: [MessageHandler(filters.TEXT, callback=get_name)],
            COUNT: [MessageHandler(filters.TEXT, callback=get_count)],
            PACKING: [MessageHandler(filters.TEXT, callback=get_packing)],
            PER_PACKING: [MessageHandler(filters.TEXT, callback=get_per_packing)],
            MIN_PART: [MessageHandler(filters.TEXT, callback=get_min_part)],
            MEDIA: [MessageHandler((filters.PHOTO | filters.VIDEO), callback=get_media)],
            PRICE_PER: [MessageHandler(filters.TEXT, callback=get_price_per)],
            SHIPMENT: [MessageHandler(filters.TEXT, callback=get_shipment)],
        },
        fallbacks=[MessageHandler(filters.TEXT, callback=get_shipment),]
    )
]