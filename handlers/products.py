from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler,
    MessageHandler, CallbackQueryHandler, filters
)

from other import (
    inline_button_helps, FloatFilter, get_inline_name_product, 
    get_inline_category, get_inline_repeat,
    create_calendar, proccess_calendar,
)

from datetime import date


CATEGORY, NAME, COUNT, PACKING, PER_PACKING, MIN_PART, MEDIA, PRICE_PER, SHIPMENT = range(9)
VALIDITY, DESCRIPTION, LOCATION_PRODUCT, MESSANGER = range(9, 13)


async def callback_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not context.user_data.get('product', None):
        context.user_data['product'] = {
            'fermer_id': context.bot_data['fermer_service'].get(update.effective_user.id).id,
            'is_active': True,
        }
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text='Выберите категорию товара', reply_markup=get_inline_category(context, context.bot_data['category_service'])
    )
    return CATEGORY


async def callback_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['over'] = True
    await update.callback_query.edit_message_text(
        text=f'Выберите категорию товара\n\n<em>Прошлое: {context.user_data["product"]["category"]}</em>', 
        reply_markup=get_inline_category(context, context.bot_data['category_service'])
    )
    return CATEGORY


async def callback_get_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    data = int(update.callback_query.data)
    context.user_data['product']['category'] = context.user_data['inline']['category'][data].goods_categories_name
    context.user_data['product']['category_id'] = context.user_data['inline']['category'][data].id
    product_name = context.user_data['inline']['category'][data].goods
    reply_text = f'<b>Категория: {context.user_data["product"]["category"]}</b>\n\nНапишите название вашего продукта или выберите название вашего продукта из списка'
    if context.user_data.get('over', None):
        reply_text += f'\n\n<em>Прошлое: {context.user_data["product"]["name"]}</em>'
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text=reply_text,
        reply_markup=get_inline_name_product(product_name, context, 4),
    )
    return NAME


async def callback_get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    data = int(update.callback_query.data)
    context.user_data['product']['goods_id'] = context.user_data['inline']['goods'][data].id
    context.user_data['product']['name'] = context.user_data['inline']['goods'][data].goods_name
    reply_text = f'<b>Категория: {context.user_data["product"]["category"]}</b>\n\nНапишите количество вашего продукта(Можно значение с плавающей точкой)'
    if context.user_data.get('over', None):
        reply_text += f'\n\n<em>Прошлое: {context.user_data["product"]["seller_quantity"]}</em>'
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text=reply_text,
    )
    return COUNT


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.effective_message.text.title()
    context.user_data['product']['name'] = name
    context.user_data['product']['goods_id'] = context.bot_data['goods_service'].create(name, context.user_data['product']['category_id']).id
    reply_text = f'<b>Категория: {context.user_data["product"]["category"]}</b>\n\nНапишите количество вашего продукта(Можно значение с плавающей точкой)'
    if context.user_data.get('over', None):
        reply_text += f'\n\n</em>Прошлое: {context.user_data["product"]["seller_quantity"]}</em>'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_text,
    )
    return COUNT


async def get_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    num = round(float(update.effective_message.text.replace(',', '.')), 6)
    context.user_data['product']['seller_quantity'] = num
    reply_text = f'<b>Категория: {context.user_data["product"]["category"]}</b>\n\nНапишите форму вашей упаковки'
    if context.user_data.get('over', None):
        reply_text += f'\n\n<em>Прошлое: {context.user_data["product"]["pack_descript"]}</em>'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_text,
    )
    return PACKING


async def get_packing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['pack_descript']= update.effective_message.text
    reply_text = f'<b>Категория: {context.user_data["product"]["category"]}</b>\n\nНапишите количество продукта в одной вашей упаковке в килограммах'
    if context.user_data.get('over', None):
        reply_text += f'\n\n<em>Прошлое: {context.user_data["product"]["pack_quantity"]}</em>'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_text,
    )
    return PER_PACKING


async def get_per_packing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['pack_quantity']= round(float(update.effective_message.text.replace(',', '.')), 6)
    reply_text = f'<b>Категория: {context.user_data["product"]["category"]}</b>\n\nНапишите минимальную партию в тоннах'
    if context.user_data.get('over', None):
        reply_text += f'\n\n<em>Прошлое: {context.user_data["product"]["minimal_quantity"]}</em>'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_text
    )
    return MIN_PART


async def get_min_part(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['minimal_quantity'] = round(float(update.effective_message.text.replace(',', '.')), 6)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'<b>Категория: {context.user_data["product"]["category"]}</b>\n\nПришли фото или видео вашего продукта'
    )
    return MEDIA


async def get_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.effective_message.photo: context.user_data['product']['foto_video_file_name'] = update.effective_message.photo[1].file_id
    else: context.user_data['product']['foto_video_file_name'] = update.effective_message.video.file_id
    reply_text = f'<b>Категория: {context.user_data["product"]["category"]}</b>\n\nНапишите цену за килограм(Пишите в точности до 6 знаков после запятой)'
    if context.user_data.get('over', None):
        reply_text += f'\n\n<em>Прошлое: {context.user_data["product"]["seller_price"]}</em>'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_text,
    )
    return PRICE_PER


async def get_price_per(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['seller_price'] = round(float(update.effective_message.text.replace(',', '.')), 6)
    context.user_data['product']['seller_sum'] = context.user_data["product"]["seller_quantity"] * 1000 * context.user_data["product"]["seller_price"]
    reply_text = f'<b>Рассчитанная сумма за весь товар: {context.user_data["product"]["seller_sum"]}</b>\n\n' + \
        f'<b>Категория: {context.user_data["product"]["category"]}</b>' + \
        f'\n\nНапишите срок отгрузки(формат: день месяц год; Пример: 01 01 2001)'
    if context.user_data.get('over', None):
        reply_text += f'\n\n<em>Прошлое: {context.user_data["product"]["offer_end_date"]}</em>'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_text,
        reply_markup=create_calendar()
    )
    return SHIPMENT


async def callback_get_shipment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    shipment = await proccess_calendar(update, context, 'Выберите дату')
    if not shipment: return SHIPMENT
    context.user_data['over'] = False
    if shipment > date.today():
        context.user_data['product']['offer_start_date'] = date.today()
        context.user_data['product']['offer_end_date'] = shipment
        await update.callback_query.delete_message()
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Вы ввели некорректную форму даты или значения(формат: день месяц год; Пример: 01 01 2001)'
        )
        return SHIPMENT
    data = context.user_data['product']
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(f'Категория: {data["category"]}\nНазвание: {data["name"]}\nКоличество: {data["seller_quantity"]}\nУпаковка: {data["pack_descript"]}\n' +
            f'Количество продукта в одной упаковке: {data["pack_quantity"]}\nМинимальная партия в тоннах: {data["minimal_quantity"]}\n' +
            f'Цена за килограмм: {data["seller_price"]}\nПолная сумма: {data["seller_sum"]}\nДата отгрузки: {data["offer_end_date"]}'),
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='<b>Всё верно?</b>',
        reply_markup=get_inline_repeat()
    )
    return ConversationHandler.END


async def callback_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.delete_message()
    del context.user_data['product']['category'], context.user_data['product']['name'], context.user_data['product']['category_id']
    context.bot_data['offer_service'].create(context.user_data['product'])
    del context.user_data['product'], context.user_data['inline']
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='<b>Вы успешно добавили свой продукт</b>\n\nЧем могу помочь?',
        reply_markup=inline_button_helps()
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='<b>Вы отменили добавление продукта</b>\n\nЧем могу помочь?',
        reply_markup=inline_button_helps()
    )
    return ConversationHandler.END


product_handlers = [
    ConversationHandler(
        entry_points=[
            CallbackQueryHandler(callback_add_product, pattern='add_product'),
            CallbackQueryHandler(callback_no, pattern='no')
        ],
        states= {
            CATEGORY: [CallbackQueryHandler(callback_get_category)],
            NAME: [
                MessageHandler(filters.TEXT, callback=get_name),
                CallbackQueryHandler(callback_add_product, pattern='back'),
                CallbackQueryHandler(callback_get_name),
            ],
            COUNT: [MessageHandler(FloatFilter(), callback=get_count)],
            PACKING: [MessageHandler(filters.TEXT, callback=get_packing)],
            PER_PACKING: [MessageHandler(FloatFilter(), callback=get_per_packing)],
            MIN_PART: [MessageHandler(FloatFilter(), callback=get_min_part)],
            MEDIA: [MessageHandler((filters.PHOTO | filters.VIDEO), callback=get_media)],
            PRICE_PER: [MessageHandler(FloatFilter(), callback=get_price_per)],
            SHIPMENT: [
                CallbackQueryHandler(callback=callback_get_shipment)
            ],
        },
        fallbacks=[
            CallbackQueryHandler(callback=callback_get_shipment)
        ],
    ),
    CallbackQueryHandler(callback_yes, 'yes')
]
