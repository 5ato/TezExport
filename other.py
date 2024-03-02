from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from telegram.ext._utils.types import FilterDataDict
from telegram.ext.filters import MessageFilter
from telegram.ext import ContextTypes
from telegram import File

from database import Good, UnitTypes
from repository import CategoryService
from handlers.message import localization

from datetime import date, timedelta
import calendar
import requests
import os


unit_type_message = {
    4: lambda language, message: localization[language][message + '_' + 'head'],
    3: lambda language, message: localization[language][message + '_' + 'pieces'],
    1: lambda language, message: localization[language][message + '_' + 'ton'],
    2: lambda language, message: localization[language][message + '_' + 'kg'],
}


def __generate_callback_data(action: str, year: str, month: str, day: str):
    return f'{action} {year} {month} {day}'


def create_calendar(year: int = None, month: int = None) -> InlineKeyboardButton:
    """Create calendar

    Args:
        year (int, optional): Year. Defaults to None.
        month (int, optional): Number month. Defaults to None.

    Returns:
        InlineKeyboardButton: InlineKeyboardButton array in array for calendar
    """
    now = date.today()
    if not month: month = now.month
    if not year: year = now.year
    result = [[InlineKeyboardButton(f'{calendar.month_name[month]} {year}', callback_data=__generate_callback_data('IGNORE', year, month, 0))]]
    row = []
    for i in ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']:
        row.append([InlineKeyboardButton(i, callback_data=__generate_callback_data('IGNORE', year, month, 0))])
    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row = []
        for day_in_week in week:
            if day_in_week != 0: 
                row.append(InlineKeyboardButton(str(day_in_week), callback_data=__generate_callback_data('DAY', year, month, day_in_week)))
                day = day_in_week
            else: row.append(InlineKeyboardButton(' ', callback_data=__generate_callback_data('IGNORE', year, month, 0)))
        result.append(row)
    row = []
    row.append(InlineKeyboardButton("<",callback_data=__generate_callback_data('PREV', year, month, day)))
    row.append(InlineKeyboardButton(" ",callback_data=__generate_callback_data('IGNORE', year, month, 0)))
    row.append(InlineKeyboardButton(">",callback_data=__generate_callback_data('NEXT', year, month, day)))
    result.append(row)
    
    return InlineKeyboardMarkup(result)


async def proccess_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    """Create calendar in telegram

    Args:
        update (Update): Update object from python telegram bot
        context (ContextTypes.DEFAULT_TYPE): ContextTypes object from python telegram bot
        text (str): Any text for message in calendar

    Returns:
        None: None
    """
    action = update.callback_query.data.split()[0]
    year, month, day = [int(i) for i in update.callback_query.data.split()[1::]]
    curr = date(year, month, 1)
    if action == 'IGNORE':
        await update.callback_query.answer()
    elif action == 'DAY':
        return date(year, month, day)
    elif action == 'PREV':
        pre = curr - timedelta(days=1)
        await update.callback_query.delete_message()
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=text,
            reply_markup=create_calendar(pre.year, pre.month)
        )
    elif action == 'NEXT':
        next = curr + timedelta(days=31)
        await update.callback_query.delete_message()
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=text,
            reply_markup=create_calendar(next.year, next.month)
        )


def get_inline_list_offers(context: ContextTypes.DEFAULT_TYPE, per_row: int = 3) -> InlineKeyboardMarkup:
    """Generate list of offers in inline keyboard

    Args:
        context (ContextTypes.DEFAULT_TYPE): ContextTypes object from python telegram bot
        per_row (int, optional): Count offers per in one row. Defaults to 3.

    Returns:
        InlineKeyboardMarkup: Inline keyboard
    """
    count, result = 0, []
    for key, item in enumerate(context.user_data['list_offers']):
        if count % per_row == 0: result.append([InlineKeyboardButton(text=item.good.goods_name, callback_data=str(key))])
        else: result[-1].append(InlineKeyboardButton(text=item.good.goods_name, callback_data=str(key)))
        count += 1
    return InlineKeyboardMarkup(result)


async def proccess_name_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data
    await update.callback_query.answer()
    if data == 'PREV':
        if context.user_data['name_index'] > 0:
            context.user_data['name_index'] -= 1
            await update.callback_query.edit_message_reply_markup(
                reply_markup=get_inline_name_full_product(context.user_data['inline_buttons'][context.user_data['name_index']])
            )
    elif data == 'NEXT':
        if context.user_data['name_index'] < len(context.user_data['inline_buttons'])-1:
            context.user_data['name_index'] += 1
            await update.callback_query.edit_message_reply_markup(
                reply_markup=get_inline_name_full_product(context.user_data['inline_buttons'][context.user_data['name_index']])
            )
    else:
        return update.callback_query.data
      

def get_inline_name_full_product(result: list[Good]):
    if [InlineKeyboardButton('Назад', callback_data='back')] not in result:
        result.append([InlineKeyboardButton('<<<', callback_data='PREV'), InlineKeyboardButton('>>', callback_data='NEXT')])
        result.append([InlineKeyboardButton('Назад', callback_data='back')])
    return InlineKeyboardMarkup(result)


def get_inline_unit_type(unit_types: list[UnitTypes], language: str, per_row: int = 3) -> InlineKeyboardMarkup:
    count, result = 0, []
    for item in unit_types:
        if item.__dict__['unit_types_name_' + language]:
            name = item.__dict__['unit_types_name_' + language]
        else:
            name = item.unit_types_name
        if count % per_row == 0: result.append([InlineKeyboardButton(text=name, callback_data=str(item.id))])
        else: result[-1].append(InlineKeyboardButton(text=name, callback_data=str(item.id)))
        count += 1
    return InlineKeyboardMarkup(result)


def get_inline_name_product(product: list[Good], context: ContextTypes.DEFAULT_TYPE, language: str, per_row: int = 3, one_time: int = 15) -> list[list[InlineKeyboardButton]]:
    """Generate list of goods name in inline keyboard

    Args:
        product (list[Good]): Table object from SQLAlchemy Good
        context (ContextTypes.DEFAULT_TYPE): ContextTypes object from python telegram bot
        per_row (int, optional): Count goods name per in one row. Defaults to 3.

    Returns:
        InlineKeyboardMarkup: Inline keyboard
    """
    count_per_row, count_one_time, result = 0, 0, []
    context.user_data['inline']['goods'] = product
    name = ''
    for key, item in enumerate(product):
        if item.__dict__['goods_name_' + language]:
            name = item.__dict__['goods_name_' + language]
        else:
            name = item.goods_name
        if count_one_time % one_time == 0:
            if count_per_row % per_row == 0:result.append([[InlineKeyboardButton(text=name, callback_data=str(key))]])
            else: result[-1].append(InlineKeyboardButton(text=name, callback_data=str(key)))
            count_per_row += 1
        else:
            if count_per_row % per_row == 0: result[-1].append([InlineKeyboardButton(text=name, callback_data=str(key))])
            else: result[-1][-1].append(InlineKeyboardButton(text=name, callback_data=str(key)))
            count_per_row += 1
        count_one_time += 1
    return result


def get_inline_category(context: ContextTypes.DEFAULT_TYPE, category_service: CategoryService, language: str, per_row: int = 3) -> InlineKeyboardMarkup:
    """Generate list of categories name in inline keyboard

    Args:
        context (ContextTypes.DEFAULT_TYPE): ContextTypes object from python telegram bot
        category_service (CategoryService): Service for categories table
        per_row (int, optional): Count categories name per in one row. Defaults to 3.

    Returns:
        InlineKeyboardMarkup: Inline keyboard
    """
    count, result = 0, []
    if not context.user_data.get('inline', None):
        context.user_data['inline'] = {}
        context.user_data['inline']['category'] = category_service.get_all_with_goods()
    print(context.user_data['inline']['category'])
    for key, item in enumerate(context.user_data['inline']['category']):
        print(item.__dict__)
        if count % per_row == 0: result.append([InlineKeyboardButton(text=item.__dict__['goods_categories_name_' + language], callback_data=str(key))])
        else: result[-1].append(InlineKeyboardButton(text=item.__dict__['goods_categories_name_' + language], callback_data=str(key)))
        count += 1
    return InlineKeyboardMarkup(result)


def get_inline_repeat(lang_local: dict) -> InlineKeyboardMarkup:
    """Create inline keyboard for choose user "Yes" or "No"

    Returns:
        InlineKeyboardMarkup: Inline keyboard
    """
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(lang_local['yes'], callback_data='yes'), InlineKeyboardButton(lang_local['no'], callback_data='no')]
        ]
    )


def validate_phone(phone: str) -> bool:
    """Check validate phone from user

    Args:
        phone (str): Phone like: "901234567" or "+901234567"

    Returns:
        bool: Valid or not
    """
    if len(phone) not in (9, 10):
        return False
    if not phone.isdigit():
        return False
    return '+' + phone if phone[0] != '+' else phone


class FloatFilter(MessageFilter):
    def filter(self, message: Message) -> bool | FilterDataDict | None:
        """Filter message only int or float

        Args:
            message (Message): Message object from python telegram bot

        Returns:
            bool | FilterDataDict | None: Valid or not
        """
        try:
            message = round(float(message.text.replace(',', '.')), 6)
        except ValueError:
            return False
        return True


async def save_media(data: File):
    print(data)
    print(data.file_path)
    name = data.file_path.split('/')[-1].split()[-1]
    return name, requests.get(data.file_path).content
    print(name)
    if not os.path.exists(f'C:/TezTelegramBot/media/{telegram_id}'):
        os.makedirs(f'C:/TezTelegramBot/media/{telegram_id}')
    if not os.path.exists(f'C:/TezTelegramBot/media/{telegram_id}/{data.file_id}'):
        os.makedirs(f'C:/TezTelegramBot/media/{telegram_id}/{data.file_id}')
    with open(f'C:/TezTelegramBot/media/{telegram_id}/{data.file_id}.{name}', 'wb') as file:
        file.write(requests.get(data.file_path).content)
        


def get_inline_updel(language: str, id: int) -> InlineKeyboardMarkup:
    """Create inline keyboard for offer: update(Обновить), delete(Удалить), skip(Пропустить)

    Args:
        id (int): Id offer in table for callback data

    Returns:
        InlineKeyboardMarkup: Inline keyboard
    """
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(localization[language]['update'], callback_data=f'update:{id}'),
                InlineKeyboardButton(localization[language]['delete'], callback_data=f'delete:{id}'),
            ],
            [
                InlineKeyboardButton(localization[language]['back'], callback_data='skip:-1'),
            ],
        ]
    )


def get_inline_language() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('Рус', callback_data='ru'), InlineKeyboardButton("O'z", callback_data='uz'), InlineKeyboardButton('Eng', callback_data='en')]
        ]
    )


def inline_button_helps(language: str) -> InlineKeyboardMarkup:
    """Create inline keyboard for menu

    Returns:
        InlineKeyboardMarkup: Inline keyboard
    """
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(localization[language]['inline_change'], callback_data='change_profile'),
                InlineKeyboardButton(localization[language]['inline_location'], callback_data='change_location')
            ],
            [
                InlineKeyboardButton(localization[language]['inline_add_product'], callback_data='add_product'),
            ],
            [
                InlineKeyboardButton(localization[language]['inline_list_product'], callback_data='list_product')
            ],
            [
                InlineKeyboardButton(localization[language]['inline_site'], url='https://tezexport.uz/')
            ]
        ]
    )
