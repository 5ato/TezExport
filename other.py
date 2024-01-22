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


def create_calendar(year = None, month = None):
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


async def proccess_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
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


def get_inline_name_product(product: list[Good], context: ContextTypes.DEFAULT_TYPE, per_row: int = 3) -> InlineKeyboardMarkup:
    count, result = 0, []
    context.user_data['inline']['goods'] = product
    for key, item in enumerate(product):
        if count % per_row == 0: result.append([InlineKeyboardButton(text=item.goods_name, callback_data=str(key))])
        else: result[-1].append(InlineKeyboardButton(text=item.goods_name, callback_data=str(key)))
        count += 1
    result.append([InlineKeyboardButton('Назад', callback_data='back')])
    return InlineKeyboardMarkup(result)


def get_inline_category(context: ContextTypes.DEFAULT_TYPE, category_service: CategoryService, per_row: int = 3) -> InlineKeyboardMarkup:
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
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('Да', callback_data='yes'), InlineKeyboardButton('Нет', callback_data='no')]
        ]
    )


error_symbol = '.,/\'":[]{}()*%$#@!?&^`~'
 

def validate_name(value: list[str]) -> bool:
    if 2 > len(value) < 3:
        return False
    for i in value:
        for j in error_symbol:
            if j in i: return False
        if not i.isalpha(): return False
    return True


def convert_join_to_dict(data) -> dict[str, list[str]]:
        if not data: return data
        first = data[0][1]
        result = {}
        for i in data:
            if first == i[1]:
                if first not in result: result[first] = [i[0]]
                else: result[first].append(i[0])
            else:
                first = i[1]
                result[first] = [i[0]]
        return result


class FloatFilter(MessageFilter):
    def filter(self, message: Message) -> bool | FilterDataDict | None:
        try:
            message = round(float(message.text.replace(',', '.')), 6)
        except ValueError:
            return False
        return True


class DateFilter(MessageFilter):
    def filter(self, message: Message) -> bool | FilterDataDict | None:
        if len(message.text.split()) != 3: return False
        return all(i.isdigit() for i in message.text.split())


def inline_button_helps() -> InlineKeyboardMarkup:
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
            ]
        ]
    )
    