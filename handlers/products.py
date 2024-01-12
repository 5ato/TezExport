from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ContextTypes, ConversationHandler

from enum import Enum


CATEGORY, NAME, COUNT, PACKING, PER_PACKING, MIN_PART, MEDIA, PRICE_PER, SHIPMENT = range(9)
VALIDITY, DESCRIPTION, LOCATION_PRODUCT, MESSANGER = range(9, 13)


class CategoryEnum(str, Enum):
    fruits_vegetables = 'Фрукты и овощи'
    animals = 'Животные'
    animal_products = 'Животные продукты'
    beekeeping_products = 'Продукты пчеловодство'
    cereals_legumes = 'Зерновые и бобовые'


def get_inline_category(per_row: int = 3) -> InlineKeyboardMarkup:
    count, result = 0, []
    for i in CategoryEnum:
        if count % per_row == 0: result.append([InlineKeyboardButton(text=i.value, callback_data=i.value)])
        else: result[-1].append(InlineKeyboardButton(text=i.value, callback_data=i.value))
        count += 1
    return InlineKeyboardMarkup(result)


async def callback_add_product(update: Update, context: CallbackContext) -> int:
    context.user_data['product'] = {}
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text='Выберите категорию товара', reply_markup=get_inline_category()
    )
    return CATEGORY


async def callback_get_category(update: Update, context: CallbackContext) -> int:
    context.user_data['product']['category'] = update.callback_query.data
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text='Напишите название вашего продукта'
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['name'] = update.effective_message.text
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Напишите количество вашего продукта',
    )
    return COUNT


async def get_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['count'] = int(update.effective_message.text)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Напишите форму вашей упаковки',
    )
    return PACKING


async def get_packing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['packing']= update.effective_message.text
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Напишите количество продукта в одной вашей упаковке',
    )
    return PER_PACKING


async def get_per_packing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['per_packing']= int(update.effective_message.text)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Напишите минимальную партию в тоннах',
    )
    return MIN_PART



async def get_min_part(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['min_part'] = int(update.effective_message.text)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Пришли фото или видео вашего продукта',
    )
    return MEDIA



async def get_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['media'] = update.effective_message.photo or update.effective_message.video
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Напишите цену за килограм',
    )
    return PRICE_PER


async def get_price_per(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['price_per'] = int(update.effective_message.text)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Напишите срок отгрузки',
    )
    return SHIPMENT


async def get_shipment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['product']['shipment'] = update.effective_message.text
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='ПОКА ЧТО ВСЁ',
    )
    print(context.user_data['product'])
    print(context.user_data)
    return ConversationHandler.END
