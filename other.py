from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from telegram.ext._utils.types import FilterDataDict
from telegram.ext.filters import MessageFilter
from telegram.ext import ContextTypes

from database import Good
from repository import CategoryService

from datetime import date, timedelta
import calendar


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
    print(year, month)
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
    print(action, year, month, day)
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
    print(context.user_data['name_index'])
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


def get_inline_name_product(product: list[Good], context: ContextTypes.DEFAULT_TYPE, per_row: int = 3, one_time: int = 15) -> list[list[InlineKeyboardButton]]:
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
    for key, item in enumerate(product):
        if count_one_time % one_time == 0:
            if count_per_row % per_row == 0: result.append([[InlineKeyboardButton(text=item.goods_name, callback_data=str(key))]])
            else: result[-1].append(InlineKeyboardButton(text=item.goods_name, callback_data=str(key)))
            count_per_row += 1
        else:
            if count_per_row % per_row == 0: result[-1].append([InlineKeyboardButton(text=item.goods_name, callback_data=str(key))])
            else: result[-1][-1].append(InlineKeyboardButton(text=item.goods_name, callback_data=str(key)))
            count_per_row += 1
        count_one_time += 1
    return result


def get_inline_category(context: ContextTypes.DEFAULT_TYPE, category_service: CategoryService, per_row: int = 3) -> InlineKeyboardMarkup:
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
    for key, item in enumerate(context.user_data['inline']['category']):
        if count % per_row == 0: result.append([InlineKeyboardButton(text=item.goods_categories_name, callback_data=str(key))])
        else: result[-1].append(InlineKeyboardButton(text=item.goods_categories_name, callback_data=str(key)))
        count += 1
    return InlineKeyboardMarkup(result)


def get_inline_repeat() -> InlineKeyboardMarkup:
    """Create inline keyboard for choose user "Yes" or "No"

    Returns:
        InlineKeyboardMarkup: Inline keyboard
    """
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('Да', callback_data='yes'), InlineKeyboardButton('Нет', callback_data='no')]
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


def get_inline_updel(id: int) -> InlineKeyboardMarkup:
    """Create inline keyboard for offer: update(Обновить), delete(Удалить), skip(Пропустить)

    Args:
        id (int): Id offer in table for callback data

    Returns:
        InlineKeyboardMarkup: Inline keyboard
    """
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('Обнововить', callback_data=f'update:{id}'),
                InlineKeyboardButton('Удалить', callback_data=f'delete:{id}'),
            ],
            [
                InlineKeyboardButton('Назад в меню', callback_data='skip:-1'),
            ],
        ]
    )


def get_inline_language() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('Рус', callback_data='ru'), InlineKeyboardButton("O'z", callback_data='uz'), InlineKeyboardButton('Eng', callback_data='en')]
        ]
    )


def inline_button_helps() -> InlineKeyboardMarkup:
    """Create inline keyboard for menu

    Returns:
        InlineKeyboardMarkup: Inline keyboard
    """
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('Изменить профиль', callback_data='change_profile'),
                InlineKeyboardButton('Изменить локацию', callback_data='change_location')
            ],
            [
                InlineKeyboardButton('Добавить товар', callback_data='add_product'),
            ],
            [
                InlineKeyboardButton('Список товаров', callback_data='list_product')
            ],
            [
                InlineKeyboardButton('Наш сайт', url='https://tezexport.uz/')
            ]
        ]
    )
    