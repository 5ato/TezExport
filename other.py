from typing import Optional, Union
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext._utils.types import FilterDataDict
from telegram.ext.filters import MessageFilter

from enum import Enum
from datetime import date


error_symbol = '.,/\'":[]{}()*%$#@!?&^`~'


def validate_fmo(value: list[str]) -> bool:
    if len(value) != 3:
        return False
    for i in value:
        for j in error_symbol:
            if j in i: return False
        if not i.isalpha(): return False
    return True


def validate_date(value: list[int]) -> bool:
    now = date.today()
    if len(value) != 3: return False
    if date(*value) < now: return False
    return True


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
        ]
    )


def find_product_in_enum(value: str) -> list[str]:
    for i in CategoryEnum:
        if i.value['value'] == value:
            return i.value['products']


class CategoryEnum(Enum):
    fruits_vegetables = {
        'num': 0,
        'value': 'Фрукты и овощи',
        'products': ['Яблоки', 'Груши', 'Абрикосы', 'Банан', 'Лемон', 'Апельсины', 'Мандарины', 'Картошка', 'Помидоры', 'Огурцы', 'Капуста',]
    }
    animals = {
        'num': 1,
        'value': 'Животные',
        'products': ['Баранина', 'Говядина', 'Лошадина', 'Курица', 'Индейка']
    }
    animal_products = {
        'num': 2,
        'value': 'Животные продукты',
        'products': ['Молоко', 'Яйца', 'Сыр', 'Шерсть', 'Творог', 'Масло', ]
    }
    beekeeping_products = {
        'num': 3,
        'value': 'Продукты пчеловодство',
        'products': ['Мёд', 'Перга', 'Крем-Мёд', 'Маточное  молочко', 'Нектар']
    }
    cereals_legumes = {
        'num': 4,
        'value': 'Зерновые и бобовые',
        'products': ['Рис', 'Пшеница', 'Овсянка', 'Кукуруза', 'Гречка', 'Фасоль', 'Горох', 'Соя', 'Чечевица', 'Маш']
    }
    