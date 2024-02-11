from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler,
    MessageHandler, CallbackQueryHandler, filters
)
from telegram.error import BadRequest

from .message import localization
from other import (
    inline_button_helps, FloatFilter, get_inline_name_product, 
    get_inline_category, get_inline_repeat, create_calendar, 
    proccess_calendar, get_inline_list_offers, get_inline_updel,
    get_inline_name_full_product, proccess_name_product,
    get_inline_unit_type, unit_type_message
)

from datetime import date


CATEGORY, NAME, UNIT_TYPE, COUNT, PACKING, PER_PACKING, MIN_PART, MEDIA, PRICE_PER, SHIPMENT = range(10)
HEAD_DESCRIPTION, DESCRIPTION, LOCATION = range(10, 13)


async def callback_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not context.user_data.get('language', None):
        context.user_data['language'] = context.bot_data['fermer_service'].get_only_language(update.effective_user.id)
    if not context.user_data.get('product', None):
        context.user_data['product'] = {
            'fermer_id': context.bot_data['fermer_service'].get(update.effective_user.id).id,
            'is_active': True,
        }
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text=localization[context.user_data['language']]['category_product'], 
        reply_markup=get_inline_category(context, context.bot_data['category_service'], context.user_data['language'])
    )
    return CATEGORY


async def callback_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['over'] = True
    await update.callback_query.edit_message_text(
        text=(localization[context.user_data['language']]['category_product'] + '\n\n' + 
              localization[context.user_data['language']]['previous'](context.user_data["product"]["category"])),
        reply_markup=get_inline_category(context, context.bot_data['category_service'])
    )
    return CATEGORY


async def callback_get_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    data = int(update.callback_query.data)
    context.user_data['product']['category'] = context.user_data['inline']['category'][data].__dict__['goods_categories_name_' + context.user_data['language']]
    context.user_data['product']['category_id'] = context.user_data['inline']['category'][data].id
    context.user_data['inline_buttons'] = get_inline_name_product(context.user_data['inline']['category'][data].goods, context, context.user_data['language'], 3, 9)
    context.user_data['name_index'] = 0
    reply_text = localization[context.user_data['language']]['category'](context.user_data["product"]["category"]) + '\n\n' + localization[context.user_data['language']]['name_product_typing']
    if context.user_data.get('over', None):
        reply_text += localization[context.user_data['language']]['previous'](context.user_data["product"]["name"])
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text=reply_text,
        reply_markup=get_inline_name_full_product(context.user_data['inline_buttons'][context.user_data['name_index']]),
    )
    return NAME


async def callback_get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    data = await proccess_name_product(update, context)
    if not data:
        return NAME
    data = int(update.callback_query.data)
    context.user_data['product']['unit_type_id'] = context.user_data['inline']['goods'][data].unit_types_id
    print(context.user_data['product']['unit_type_id'])
    context.user_data['product']['goods_id'] = context.user_data['inline']['goods'][data].id
    context.user_data['product']['name'] = context.user_data['inline']['goods'][data].goods_name
    reply_text = (localization[context.user_data['language']]['category'](context.user_data["product"]["category"]) + '\n' + 
                  localization[context.user_data['language']]['name'](context.user_data["product"]["name"]) + '\n\n')
    reply_text += unit_type_message[context.user_data['product']['unit_type_id']](context.user_data['language'], 'count_product')
    if context.user_data.get('over', None):
        reply_text += localization[context.user_data['language']]['previous'](context.user_data["product"]["seller_quantity"])
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text=reply_text,
    )
    return COUNT


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.effective_message.text.title()
    context.user_data['product']['name'] = name
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(localization[context.user_data['language']]['category'](context.user_data["product"]["category"]) + '\n' + 
             localization[context.user_data['language']]['name'](context.user_data["product"]["name"]) + '\n\n' +
             localization[context.user_data['language']]['choose_unit_type']),
        reply_markup=get_inline_unit_type(context.bot_data['unit_type_service'].get_all(), context.user_data['language'])
    )
    return UNIT_TYPE


async def callback_get_unit_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    data = [context.user_data['language'], context.user_data['product']['name'], int(update.callback_query.data), context.user_data['product']['category_id']]
    context.user_data['product']['unit_type_id'] = int(update.callback_query.data)
    context.user_data['product']['goods_id'] = context.bot_data['goods_service'].create(*data).id
    reply_text = (localization[context.user_data['language']]['category'](context.user_data["product"]["category"]) + '\n' + 
                  localization[context.user_data['language']]['name'](context.user_data["product"]["name"]) + '\n\n')
    reply_text += unit_type_message[int(update.callback_query.data)](context.user_data['language'], 'count_product')
    if context.user_data.get('over', None):
        reply_text += localization[context.user_data['language']]['previous'](context.user_data["product"]["seller_quantity"])
    await update.callback_query.edit_message_text(
        text=reply_text,
    )
    return COUNT


async def get_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    num = round(float(update.effective_message.text.replace(',', '.')), 6)
    if num > 100000:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=localization[context.user_data['language']]['wrong_count'],
        )
        return COUNT
    context.user_data['product']['seller_quantity'] = num
    reply_text = (localization[context.user_data['language']]['category'](context.user_data["product"]["category"]) + '\n' + 
                  localization[context.user_data['language']]['name'](context.user_data["product"]["name"]) + '\n\n' +
                  localization[context.user_data['language']]['pack_product'])
    if context.user_data.get('over', None):
        reply_text += localization[context.user_data['language']]['previous'](context.user_data["product"]["pack_descript"])
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_text,
    )
    return PACKING


async def get_packing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['pack_descript']= update.effective_message.text
    reply_text = (localization[context.user_data['language']]['category'](context.user_data["product"]["category"]) + '\n' + 
                  localization[context.user_data['language']]['name'](context.user_data["product"]["name"]) + '\n\n')
    reply_text += unit_type_message[context.user_data['product']['unit_type_id']](context.user_data['language'], 'pack_quantity')
    if context.user_data.get('over', None):
        reply_text += localization[context.user_data['language']]['previous'](context.user_data["product"]["pack_quantity"])
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_text,
    )
    return PER_PACKING


async def get_per_packing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['pack_quantity']= round(float(update.effective_message.text.replace(',', '.')), 6)
    reply_text = (localization[context.user_data['language']]['category'](context.user_data["product"]["category"]) + '\n' + 
                  localization[context.user_data['language']]['name'](context.user_data["product"]["name"]) + '\n\n')
    reply_text += unit_type_message[context.user_data['product']['unit_type_id']](context.user_data['language'], 'min_part')
    if context.user_data.get('over', None):
        reply_text += localization[context.user_data['language']]['previous'](context.user_data["product"]["minimal_quantity"])
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_text
    )
    return MIN_PART


async def get_min_part(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['minimal_quantity'] = round(float(update.effective_message.text.replace(',', '.')), 6)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(localization[context.user_data['language']]['category'](context.user_data["product"]["category"]) + '\n' + 
              localization[context.user_data['language']]['name'](context.user_data["product"]["name"]) + '\n\n' +
              localization[context.user_data['language']]['foto_video'])
    )
    return MEDIA


async def get_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.effective_message.photo: context.user_data['product']['foto_video_file_name'] = update.effective_message.photo[1].file_id
    else: context.user_data['product']['foto_video_file_name'] = update.effective_message.video.file_id
    reply_text = (localization[context.user_data['language']]['category'](context.user_data["product"]["category"]) + '\n' + 
                  localization[context.user_data['language']]['name'](context.user_data["product"]["name"]) + '\n\n')
    reply_text += unit_type_message[context.user_data['product']['unit_type_id']](context.user_data['language'], 'price_per')
    if context.user_data.get('over', None):
        reply_text += localization[context.user_data['language']]['previous'](context.user_data["product"]["seller_price"])
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_text,
    )
    return PRICE_PER


async def get_price_per(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['seller_price'] = round(float(update.effective_message.text.replace(',', '.')), 6)
    context.user_data['product']['seller_sum'] = context.user_data["product"]["seller_quantity"] * 1000 * context.user_data["product"]["seller_price"]
    reply_text = (localization[context.user_data['language']]['seller_sum_data'](context.user_data['product']['seller_sum']) + '\n\n' +
                  localization[context.user_data['language']]['category'](context.user_data["product"]["category"]) + '\n' + 
                  localization[context.user_data['language']]['name'](context.user_data["product"]["name"]) + '\n\n' + 
                  localization[context.user_data['language']]['shipment'])
    if context.user_data.get('over', None):
        reply_text += localization[context.user_data['language']]['previous'](context.user_data["product"]["offer_end_date"])
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_text,
        reply_markup=create_calendar()
    )
    return SHIPMENT


async def callback_get_shipment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    shipment = await proccess_calendar(update, context, localization[context.user_data['language']]['choose_date'])
    if not shipment: return SHIPMENT
    if shipment > date.today():
        context.user_data['product']['offer_start_date'] = date.today()
        context.user_data['product']['offer_end_date'] = shipment
        await update.callback_query.delete_message()
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=localization[context.user_data['language']]['wrong_date']
        )
        return SHIPMENT
    reply_text = (localization[context.user_data['language']]['category'](context.user_data["product"]["category"]) + '\n' + 
                  localization[context.user_data['language']]['name'](context.user_data["product"]["name"]) + '\n\n' + 
                  localization[context.user_data['language']]['head_description_data'])
    if context.user_data.get('over', None):
        reply_text += localization[context.user_data['language']]['previous'](context.user_data["product"]["head_description"])
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_text,
    )
    return HEAD_DESCRIPTION


async def get_head_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if len(update.effective_message.text) >= 50:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=localization[context.user_data['language']]['wrong_head_description']
        )
        return HEAD_DESCRIPTION
    context.user_data['product']['head_description'] = update.effective_message.text
    reply_text = (localization[context.user_data['language']]['category'](context.user_data["product"]["category"]) + '\n' + 
                  localization[context.user_data['language']]['name'](context.user_data["product"]["name"]) + '\n\n' +
                  localization[context.user_data['language']]['description_data'])
    if context.user_data.get('over', None):
        reply_text += localization[context.user_data['language']]['previous'](context.user_data["product"]["description"])
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
        text=(localization[context.user_data['language']]['category'](context.user_data["product"]["category"]) + '\n' + 
              localization[context.user_data['language']]['name'](context.user_data["product"]["name"]) + '\n\n' +
              localization[context.user_data['language']]['location']),
        reply_markup=ReplyKeyboardMarkup(
            [
                [
                    KeyboardButton(localization[context.user_data['language']]['get_location'], request_location=True), 
                    KeyboardButton(localization[context.user_data['language']]['skip'])
                ]
            ], 
            resize_keyboard=True, 
            one_time_keyboard=True)
    )
    return LOCATION


async def skip_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    data = context.user_data['product']
    lang_local = localization[context.user_data["language"]]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(lang_local["category"](data["category"]) + '\n' + 
              lang_local['name'](data["name"]) + '\n' + 
              lang_local['seller_quantity'](data["seller_quantity"]) + '\n' + 
              lang_local['pack_descript'](data["pack_descript"]) + '\n' +
              lang_local['pack_quantity'](data["pack_quantity"]) + '\n' + 
              lang_local['minimal_quantity'](data["minimal_quantity"]) + '\n' +
              lang_local['seller_price'](data["seller_price"]) + '\n' + 
              lang_local['seller_sum'](data["seller_sum"]) + '\n' + 
              lang_local['offer_end_date'](data["offer_end_date"]) + '\n' +
              lang_local['head_description'](data["head_description"]) + '\n' + 
              lang_local['description'](data["description"])),
        reply_markup=ReplyKeyboardRemove(True)
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=lang_local['all_right'],
        reply_markup=get_inline_repeat(lang_local)
    )
    return ConversationHandler.END


async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['location'] = f'lat={update.message.location.latitude} long={update.message.location.longitude}'
    data = context.user_data['product']
    lang_local = localization[context.user_data["language"]]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(lang_local["category"](data["category"]) + '\n' + 
              lang_local['name'](data["name"]) + '\n' + 
              lang_local['seller_quantity'](data["seller_quantity"]) + '\n' + 
              lang_local['pack_descript'](data["pack_descript"]) + '\n' +
              lang_local['pack_quantity'](data["pack_quantity"]) + '\n' + 
              lang_local['minimal_quantity'](data["minimal_quantity"]) + '\n' +
              lang_local['seller_price'](data["seller_price"]) + '\n' + 
              lang_local['seller_sum'](data["seller_sum"]) + '\n' + 
              lang_local['offer_end_date'](data["offer_end_date"]) + '\n' +
              lang_local['head_description'](data["head_description"]) + '\n' + 
              lang_local['description'](data["description"])),
        reply_markup=ReplyKeyboardRemove(True)
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=lang_local['all_right'],
        reply_markup=get_inline_repeat(lang_local)
    )
    return ConversationHandler.END


async def callback_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.delete_message()
    del context.user_data['product']['category'], context.user_data['product']['name'], context.user_data['product']['category_id'], context.user_data['product']['unit_type_id']
    if context.user_data.get('updated', None):
        context.bot_data['offer_service'].update(context.user_data['product']['id'], context.user_data['product'])
        del context.user_data['updated']
    else:
        context.bot_data['offer_service'].create(context.user_data['product'])
    context.user_data['over'] = False
    del context.user_data['product'], context.user_data['inline'], context.user_data['inline_buttons'], context.user_data['name_index']
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=localization[context.user_data['language']]['success_product'],
        reply_markup=inline_button_helps(context.user_data['language'])
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='<b>Вы отменили добавление продукта</b>\n\nЧем могу помочь?',
        reply_markup=inline_button_helps()
    )
    return ConversationHandler.END


async def callback_list_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('language', None):
        context.user_data['language'] = context.bot_data['fermer_service'].get_only_language(update.effective_user.id)
    data = context.bot_data['offer_service'].get_list_from_user(update.effective_user.id)
    await update.callback_query.answer()
    await update.callback_query.delete_message()
    if data:
        context.user_data['list_offers'] = data
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=localization[context.user_data['language']]['code'],
            reply_markup=get_inline_list_offers(context)
        )
    else:
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=localization[context.user_data['language']]['not_code'],
        reply_markup=inline_button_helps()
    )


async def callback_get_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.delete_message()
    data = context.user_data['list_offers'][int(update.callback_query.data)]
    name = data.good.__dict__.get('goods_name_' + context.user_data["language"], None)
    if not name: name = data.good.goods_name
    lang_local = localization[context.user_data["language"]]
    if data.foto_video_file_name:
        try:
            await context.bot.send_document(
                chat_id=update.effective_chat.id, 
                caption=(lang_local["category"](data.good.good_category.__dict__['goods_categories_name_' + context.user_data["language"]]) + '\n' + 
                        lang_local['name'](name) + '\n' + 
                        lang_local['seller_quantity'](float(data.seller_quantity)) + '\n' + 
                        lang_local['pack_descript'](data.pack_descript) + '\n' +
                        lang_local['pack_quantity'](float(data.pack_quantity)) + '\n' + 
                        lang_local['minimal_quantity'](float(data.minimal_quantity)) + '\n' +
                        lang_local['seller_price'](float(data.seller_price)) + '\n' + 
                        lang_local['seller_sum'](float(data.seller_sum)) + '\n' + 
                        lang_local['offer_end_date'](data.offer_end_date) + '\n' +
                        lang_local['head_description'](data.head_description) + '\n' + 
                        lang_local['description'](data.description)),
                reply_markup=get_inline_updel(context.user_data['language'], data.id),
                document=data.foto_video_file_name
            )
        except BadRequest:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id, 
                caption=(lang_local["category"](data.good.good_category.__dict__['goods_categories_name_' + context.user_data["language"]]) + '\n' + 
                        lang_local['name'](name) + '\n' + 
                        lang_local['seller_quantity'](float(data.seller_quantity)) + '\n' + 
                        lang_local['pack_descript'](data.pack_descript) + '\n' +
                        lang_local['pack_quantity'](float(data.pack_quantity)) + '\n' + 
                        lang_local['minimal_quantity'](float(data.minimal_quantity)) + '\n' +
                        lang_local['seller_price'](float(data.seller_price)) + '\n' + 
                        lang_local['seller_sum'](float(data.seller_sum)) + '\n' + 
                        lang_local['offer_end_date'](data.offer_end_date) + '\n' +
                        lang_local['head_description'](data.head_description) + '\n' + 
                        lang_local['description'](data.description)),
                reply_markup=get_inline_updel(context.user_data['language'], data.id),
                photo=data.foto_video_file_name
            )


async def callback_updel_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.delete_message()
    action, id = update.callback_query.data.split(':')
    if action == 'delete':
        context.bot_data['offer_service'].delete(int(id))
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=localization[context.user_data['language']]['delete_success'],
            reply_markup=inline_button_helps(context.user_data['language'])
        )
    elif action == 'skip':
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=localization[context.user_data['language']]['home_menu'],
        reply_markup=inline_button_helps(context.user_data['language'])
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
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(localization[context.user_data['language']]['category_product'] + '\n\n' +
                  localization[context.user_data['language']]['previous'](context.user_data["product"]["category"])), 
            reply_markup=get_inline_category(context, context.bot_data['category_service'], context.user_data['language'])
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
            UNIT_TYPE: [CallbackQueryHandler(callback_get_unit_type)],
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
            LOCATION: [MessageHandler(filters.LOCATION, get_location), MessageHandler(filters.Text(['Пропустить', 'Skip', "O'tkazib yuborish"]), skip_location)]
        },
        fallbacks=[
            MessageHandler(filters.LOCATION, get_location), MessageHandler(filters.Text(['Пропустить', 'Skip', "O'tkazib yuborish"]), skip_location)
        ],
    ),
    CallbackQueryHandler(callback_yes, 'yes'),
    CallbackQueryHandler(callback_list_product, 'list_product'),
    CallbackQueryHandler(callback_get_product)
]
