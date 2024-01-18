from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ContextTypes, ConversationHandler,
    MessageHandler, CallbackQueryHandler, filters
)

from other import (
    CategoryEnum, find_product_in_enum, validate_date, inline_button_helps,
    FloatFilter, DateFilter
)

from datetime import date


CATEGORY, NAME, COUNT, PACKING, PER_PACKING, MIN_PART, MEDIA, PRICE_PER, SHIPMENT = range(9)
VALIDITY, DESCRIPTION, LOCATION_PRODUCT, MESSANGER = range(9, 13)


def get_inline_name_product(product: list[str], per_row: int = 3) -> InlineKeyboardMarkup:
    count, result = 0, []
    for i in product:
        if count % per_row == 0: result.append([InlineKeyboardButton(text=i, callback_data=i)])
        else: result[-1].append(InlineKeyboardButton(text=i, callback_data=i))
        count += 1
    result.append([InlineKeyboardButton('Назад', callback_data='back')])
    return InlineKeyboardMarkup(result)


def get_inline_category(per_row: int = 3) -> InlineKeyboardMarkup:
    count, result = 0, []
    for i in CategoryEnum:
        if count % per_row == 0: result.append([InlineKeyboardButton(text=i.value['value'], callback_data=i.value['value'])])
        else: result[-1].append(InlineKeyboardButton(text=i.value['value'], callback_data=i.value['value']))
        count += 1
    return InlineKeyboardMarkup(result)


def get_inline_repeat() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('Да', callback_data='yes'), InlineKeyboardButton('Нет', callback_data='no')]
        ]
    )


async def callback_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product'] = {}
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text='Выберите категорию товара', reply_markup=get_inline_category()
    )
    return CATEGORY


async def callback_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['over'] = True
    await update.callback_query.edit_message_text(
        text=f'Выберите категорию товара\n\n<em>Прошлое: {context.user_data["product"]["category"]}</em>', reply_markup=get_inline_category(),
    )
    return CATEGORY


async def callback_get_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    data = update.callback_query.data
    context.user_data['product']['category'] = data
    product_name = find_product_in_enum(data)
    reply_text = f'<b>Категория: {context.user_data["product"]["category"]}</b>\n\nНапишите название вашего продукта или выберите название вашего продукта из списка'
    if context.user_data.get('over', None):
        reply_text += f'\n\n<em>Прошлое: {context.user_data["product"]["name"]}</em>'
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text=reply_text,
        reply_markup=get_inline_name_product(product_name, 4),
    )
    return NAME


async def callback_get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['name'] = update.callback_query.data
    reply_text = f'<b>Категория: {context.user_data["product"]["category"]}</b>\n\nНапишите количество вашего продукта(Можно значение с плавающей точкой)'
    if context.user_data.get('over', None):
        reply_text += f'\n\n<em>Прошлое: {context.user_data["product"]["count"]}</em>'
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text=reply_text,
    )
    return COUNT


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['name'] = update.effective_message.text
    reply_text = f'<b>Категория: {context.user_data["product"]["category"]}</b>\n\nНапишите количество вашего продукта(Можно значение с плавающей точкой)'
    if context.user_data.get('over', None):
        reply_text += f'\n\n</em>Прошлое: {context.user_data["product"]["count"]}</em>'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_text,
    )
    return COUNT


async def get_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    num = round(float(update.effective_message.text.replace(',', '.')), 6)
    context.user_data['product']['count'] = num
    reply_text = f'<b>Категория: {context.user_data["product"]["category"]}</b>\n\nНапишите форму вашей упаковки'
    if context.user_data.get('over', None):
        reply_text += f'\n\n<em>Прошлое: {context.user_data["product"]["packing"]}</em>'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_text,
    )
    return PACKING


async def get_packing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['packing']= update.effective_message.text
    reply_text = f'<b>Категория: {context.user_data["product"]["category"]}</b>\n\nНапишите количество продукта в одной вашей упаковке в килограммах'
    if context.user_data.get('over', None):
        reply_text += f'\n\n<em>Прошлое: {context.user_data["product"]["per_packing"]}</em>'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_text,
    )
    return PER_PACKING


async def get_per_packing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['per_packing']= round(float(update.effective_message.text.replace(',', '.')), 6)
    reply_text = f'<b>Категория: {context.user_data["product"]["category"]}</b>\n\nНапишите минимальную партию в тоннах'
    if context.user_data.get('over', None):
        reply_text += f'\n\n<em>Прошлое: {context.user_data["product"]["min_part"]}</em>'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_text
    )
    return MIN_PART



async def get_min_part(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['min_part'] = round(float(update.effective_message.text.replace(',', '.')), 6)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'<b>Категория: {context.user_data["product"]["category"]}</b>\n\nПришли фото или видео вашего продукта'
    )
    return MEDIA



async def get_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['media'] = update.effective_message.photo or update.effective_message.video
    reply_text = f'<b>Категория: {context.user_data["product"]["category"]}</b>\n\nНапишите цену за килограм(Пишите в точности до 6 знаков после запятой)'
    if context.user_data.get('over', None):
        reply_text += f'\n\n<em>Прошлое: {context.user_data["product"]["price_per"]}</em>'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_text,
    )
    return PRICE_PER


async def get_price_per(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['price_per'] = round(float(update.effective_message.text.replace(',', '.')), 6)
    reply_text = f'<b>Категория: {context.user_data["product"]["category"]}</b>\n\nНапишите срок отгрузки(формат: день месяц год; Пример: 01 01 2001)'
    if context.user_data.get('over', None):
        reply_text += f'\n\n<em>Прошлое: {context.user_data["product"]["shipment"]}</em>'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Рассчитанная сумма за весь товар: {context.user_data["product"]["count"] * 1000 * context.user_data["product"]["price_per"]}'
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_text,
    )
    return SHIPMENT


async def get_shipment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    shipment = list(map(lambda x: int(x), update.effective_message.text.split()))[::-1]
    context.user_data['over'] = False
    if validate_date(shipment):
        context.user_data['product']['shipment'] = date(*shipment)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Вы ввели некорректную форму даты или значения(формат: день месяц год; Пример: 01 01 2001)'
        )
        return SHIPMENT
    data = context.user_data['product']
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(f'Категория: {data["category"]}\nНазвание: {data["name"]}\nКоличество: {data["count"]}\nУпаковка: {data["packing"]}\n' +
            f'Количество продукта в одной упаковке: {data["per_packing"]}\nМинимальная партия в тоннах: {data["min_part"]}\n' +
            f'Цена за килограмм: {data["price_per"]}\nДата отгрузки: {data["shipment"]}\nВсё верно?'),
        reply_markup=get_inline_repeat()
    )
    return ConversationHandler.END


async def callback_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.delete_message()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Вы успешно добавили свой продукт'
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Чем могу помочь?',
        reply_markup=inline_button_helps()
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Вы отменили добавление продукта\nЧем могу помочь?'
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
                MessageHandler(DateFilter(), callback=get_shipment)
            ],
        },
        fallbacks=[
            MessageHandler(DateFilter(), callback=get_shipment)
        ],
    ),
    CallbackQueryHandler(callback_yes, 'yes')
]
