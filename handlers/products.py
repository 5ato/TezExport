from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes, ConversationHandler,
    MessageHandler, CallbackQueryHandler, filters
)
from telegram.error import BadRequest

from other import (
    inline_button_helps, FloatFilter, get_inline_name_product, 
    get_inline_category, get_inline_repeat, create_calendar, 
    proccess_calendar, get_inline_list_offers, get_inline_updel
)

from datetime import date


CATEGORY, NAME, COUNT, PACKING, PER_PACKING, MIN_PART, MEDIA, PRICE_PER, SHIPMENT = range(9)
HEAD_DESCRIPTION, DESCRIPTION, LOCATION = range(9, 12)


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
    reply_text = f'<b>Категория: {context.user_data["product"]["category"]}</b>\n\nНапишите наименование вашего продукта или выберите из списка'
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
    reply_text = (f'<b>Категория: {context.user_data["product"]["category"]}</b>\n' + f'<b>Наименование: {context.user_data["product"]["name"]}</b>\n\n'
                  f'Напишите количество вашего продукта(Можно дать дробное значение через запятую)')
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
    reply_text = (f'<b>Категория: {context.user_data["product"]["category"]}</b>\n' + f'<b>Наименование: {context.user_data["product"]["name"]}</b>\n\n'
                  f'Напишите количество вашего продукта(Можно дать дробное значение через запятую)')
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
    reply_text = (f'<b>Категория: {context.user_data["product"]["category"]}</b>\n' + 
                  f'<b>Наименование: {context.user_data["product"]["name"]}</b>\n\n' +
                  f'Напишите форму вашей упаковки')
    if context.user_data.get('over', None):
        reply_text += f'\n\n<em>Прошлое: {context.user_data["product"]["pack_descript"]}</em>'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_text,
    )
    return PACKING


async def get_packing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['pack_descript']= update.effective_message.text
    reply_text = (f'<b>Категория: {context.user_data["product"]["category"]}</b>\n' + 
                  f'<b>Наименование: {context.user_data["product"]["name"]}</b>\n\n' + 
                  'Напишите количество продукта в одной вашей упаковке в килограммах')
    if context.user_data.get('over', None):
        reply_text += f'\n\n<em>Прошлое: {context.user_data["product"]["pack_quantity"]}</em>'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_text,
    )
    return PER_PACKING


async def get_per_packing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['pack_quantity']= round(float(update.effective_message.text.replace(',', '.')), 6)
    reply_text = (f'<b>Категория: {context.user_data["product"]["category"]}</b>\n' + 
                  f'<b>Наименование: {context.user_data["product"]["name"]}</b>\n\n' +
                  'Напишите минимальную партию в тоннах')
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
        text=(f'<b>Категория: {context.user_data["product"]["category"]}</b>\n' + 
              f'<b>Наименование: {context.user_data["product"]["name"]}</b>\n\n' +
              'Пришли фото или видео вашего продукта')
    )
    return MEDIA


async def get_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.effective_message.photo: context.user_data['product']['foto_video_file_name'] = update.effective_message.photo[1].file_id
    else: context.user_data['product']['foto_video_file_name'] = update.effective_message.video.file_id
    reply_text = (f'<b>Категория: {context.user_data["product"]["category"]}</b>\n' + 
                  f'<b>Наименование: {context.user_data["product"]["name"]}</b>\n\n' +
                  'Напишите цену за килограм(Пишите в точности до 6 знаков после запятой)')
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
    reply_text = (f'<b>Рассчитанная сумма за весь товар: {context.user_data["product"]["seller_sum"]}</b>\n\n' +
                  f'<b>Категория: {context.user_data["product"]["category"]}</b>\n' + 
                  f'<b>Наименование: {context.user_data["product"]["name"]}</b>\n\n' + 
                  f'Напишите срок отгрузки(формат: день месяц год; Пример: 01 01 2001)')
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
    reply_text = (f'<b>Категория: {context.user_data["product"]["category"]}</b>\n' + 
                  f'<b>Наименование: {context.user_data["product"]["name"]}</b>\n\n' + 
                  'Напишите заголовок Вашего продукта(не больше 50 символов)')
    if context.user_data.get('over', None):
        reply_text += f'\n\n<em>Прошлое: {context.user_data["product"]["head_description"]}</em>'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_text,
    )
    return HEAD_DESCRIPTION


async def get_head_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if len(update.effective_message.text) >= 50:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Максимально 50 символов, Вы ввели <b>больше 50 символов</b>'
        )
        return HEAD_DESCRIPTION
    context.user_data['product']['head_description'] = update.effective_message.text
    reply_text = (f'<b>Категория: {context.user_data["product"]["category"]}</b>\n' + 
                  f'<b>Наименование: {context.user_data["product"]["name"]}</b>\n\n'
                  'Напишите описание Вашего продукта')
    if context.user_data.get('over', None):
        reply_text += f'\n\n<em>Прошлое: {context.user_data["product"]["description"]}</em>'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_text,
    )
    return DESCRIPTION


async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['description'] = update.effective_message.text
    if context.user_data.get('over', None) and context.user_data['product'].get('location', None):
        location = context.user_data['product']['location'].split()
        await context.bot.send_location(
            chat_id=update.effective_chat.id,
            latitude=location[0].split('=')[1],
            longitude=location[1].split('=')[1],
        )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(f'<b>Категория: {context.user_data["product"]["category"]}</b>\n' + 
              f'<b>Наименование: {context.user_data["product"]["name"]}</b>\n\n' + 
              'Отправьте локацию нахождения вашего продукта(по желанию)'),
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Дать локацию', request_location=True), KeyboardButton('Пропустить')]], resize_keyboard=True, one_time_keyboard=True)
    )
    return LOCATION


async def skip_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    data = context.user_data['product']
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(f'Категория: {data["category"]}\nНаименование: {data["name"]}\nКоличество: {data["seller_quantity"]}\nУпаковка: {data["pack_descript"]}\n' +
            f'Количество продукта в одной упаковке: {data["pack_quantity"]}\nМинимальная партия в тоннах: {data["minimal_quantity"]}\n' +
            f'Цена за килограмм: {data["seller_price"]}\nПолная сумма: {data["seller_sum"]}\nДата отгрузки: {data["offer_end_date"]}\n' +
            f'Заголовок: {data["head_description"]}\nОписание товара: {data["description"]}'),
        reply_markup=ReplyKeyboardRemove(True)
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Всё верно?',
        reply_markup=get_inline_repeat()
    )
    return ConversationHandler.END


async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['location'] = f'lat={update.message.location.latitude} long={update.message.location.longitude}'
    data = context.user_data['product']
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(f'Категория: {data["category"]}\nНаименование: {data["name"]}\nКоличество: {data["seller_quantity"]}\nУпаковка: {data["pack_descript"]}\n' +
            f'Количество продукта в одной упаковке: {data["pack_quantity"]}\nМинимальная партия в тоннах: {data["minimal_quantity"]}\n' +
            f'Цена за килограмм: {data["seller_price"]}\nПолная сумма: {data["seller_sum"]}\nДата отгрузки: {data["offer_end_date"]}\n' +
            f'Заголовок: {data["head_description"]}\nОписание товара: {data["description"]}'),
        reply_markup=ReplyKeyboardRemove(True)
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Всё верно?',
        reply_markup=get_inline_repeat()
    )
    return ConversationHandler.END


async def callback_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.delete_message()
    del context.user_data['product']['category'], context.user_data['product']['name'], context.user_data['product']['category_id']
    if context.user_data.get('updated', None):
        context.bot_data['offer_service'].update(context.user_data['product']['id'], context.user_data['product'])
        del context.user_data['updated']
    else:
        context.bot_data['offer_service'].create(context.user_data['product'])
    context.user_data['over'] = False
    del context.user_data['product'], context.user_data['inline']
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='<b>Вы успешно добавили свой продукт</b>\n\nЧем могу помочь?',
        reply_markup=inline_button_helps()
    )
    print(context.user_data)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='<b>Вы отменили добавление продукта</b>\n\nЧем могу помочь?',
        reply_markup=inline_button_helps()
    )
    return ConversationHandler.END


async def callback_list_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.bot_data['offer_service'].get_list_from_user(update.effective_user.id)
    context.user_data['list_offers'] = data
    await update.callback_query.answer()
    await update.callback_query.delete_message()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Выберите код одного из Ваших товаров',
        reply_markup=get_inline_list_offers(context)
    )


async def callback_get_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.delete_message()
    data = context.user_data['list_offers'][int(update.callback_query.data)]
    if data.foto_video_file_name:
        try:
            await context.bot.send_document(
                chat_id=update.effective_chat.id, 
                caption=(f'<b>Категория</b>: {data.good.good_category.goods_categories_name}\n<b>Название</b>: {data.good.goods_name}\n' +
                    f'<b>Количество</b>: {float(data.seller_quantity)}\n<b>Упаковка</b>: {data.pack_descript}\n' +
                    f'<b>Количество продукта в одной упаковке</b>: {float(data.pack_quantity)}\n' +
                    f'<b>Минимальная партия в тоннах</b>: {float(data.minimal_quantity)}\n<b>Цена за килограмм</b>: {float(data.seller_price)}\n' +
                    f'<b>Полная сумма</b>: {float(data.seller_sum)}\n<b>Дата отгрузки</b>: {data.offer_end_date}' +
                    f'<b>Заголовок</b>: {data.head_description}\n<b>Описание продукта</b>: {data.description}'),
                reply_markup=get_inline_updel(data.id),
                document=data.foto_video_file_name
            )
        except BadRequest:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id, 
                caption=(f'<b>Категория</b>: {data.good.good_category.goods_categories_name}\n<b>Название</b>: {data.good.goods_name}\n' +
                    f'<b>Количество</b>: {float(data.seller_quantity)}\n<b>Упаковка</b>: {data.pack_descript}\n' +
                    f'<b>Количество продукта в одной упаковке</b>: {float(data.pack_quantity)}\n' +
                    f'<b>Минимальная партия в тоннах</b>: {float(data.minimal_quantity)}\n<b>Цена за килограмм</b>: {float(data.seller_price)}\n' +
                    f'<b>Полная сумма</b>: {float(data.seller_sum)}\n<b>Дата отгрузки</b>: {data.offer_end_date}' +
                    f'<b>Заголовок</b>: {data.head_description}\n<b>Описание продукта</b>: {data.description}'),
                reply_markup=get_inline_updel(data.id),
                photo=data.foto_video_file_name
            )


async def callback_updel_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    print(update.callback_query.data)
    action, id = update.callback_query.data.split(':')
    if action == 'delete':
        context.bot_data['offer_service'].delete(int(id))
        await update.callback_query.delete_message()
        await update.callback_query.edit_message_text(
            text='<b>Вы успешно удалили товар</b>\n\nЧем могу помочь Вам?',
            reply_markup=inline_button_helps()
        )
    elif action == 'skip':
        await update.callback_query.delete_message()
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Чем могу Вам помочь?',
        reply_markup=inline_button_helps()
    )
    elif action == 'update':
        data = context.bot_data['offer_service'].get_full_join(id)
        context.user_data['product'] = data.as_dict()
        context.user_data['product'].update(
            {
                'category': data.good.good_category.goods_categories_name,
                'name': data.good.goods_name,
                'category_id': data.good.good_category.id
            }
        )
        context.user_data['over'] = True
        context.user_data['updated'] = True
        await update.callback_query.edit_message_text(
            text=f'Выберите категорию товара\n\n<em>Прошлое: {context.user_data["product"]["category"]}</em>', 
            reply_markup=get_inline_category(context, context.bot_data['category_service'])
        )
        return CATEGORY


product_handlers = [
    ConversationHandler(
        entry_points=[
            CallbackQueryHandler(callback_add_product, pattern='add_product'),
            CallbackQueryHandler(callback_no, pattern='no'),
            CallbackQueryHandler(callback_updel_product, pattern=r'\b(delete|update|skip)\b')
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
            HEAD_DESCRIPTION: [MessageHandler(filters.TEXT, get_head_description)],
            DESCRIPTION: [MessageHandler(filters.TEXT, get_description)],
            LOCATION: [MessageHandler(filters.LOCATION, get_location), MessageHandler(filters.Text(['Пропустить']), skip_location)]
        },
        fallbacks=[
            MessageHandler(filters.LOCATION, get_location), MessageHandler(filters.Text(['Пропустить']), skip_location)
        ],
    ),
    CallbackQueryHandler(callback_yes, 'yes'),
    CallbackQueryHandler(callback_list_product, 'list_product'),
    CallbackQueryHandler(callback_get_product)
]
