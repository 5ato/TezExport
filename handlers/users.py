from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton
)
from telegram.ext import (
    ContextTypes, ConversationHandler, CallbackContext
)
from other import validate_fmo, inline_button_helps


FMO_TYPING, CONTACT, LOCATION = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_text = 'Здравствуйте, '
    if context.user_data: reply_text += 'Как я вижу, вы уже зарегистрированы, чем могу помочь?'
    else: reply_text += 'Сначало нужно пройти регистрацию\nКак вас зовут? Фамилия, имя и отчество введите через пробел'
    await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=reply_text,
        )
    return FMO_TYPING


async def get_fmo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    fmo = validate_fmo(update.message.text.split())
    if not fmo:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Вы ввели некорректные данные\nПовторите написать свою фамилию, имя и отчество'
        )
        return FMO_TYPING
    context.user_data['fmo'] = update.message.text.capitalize()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Поделитесь своим контактом',
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton('Отправить контакт', request_contact=True)]], 
            resize_keyboard=True, 
            one_time_keyboard=True
        )
    )
    return CONTACT


async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['contact'] = update.message.contact
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Отлично\nТеперь отправьте свою локацию',
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton('Отправить локацию', request_location=True)]], 
            resize_keyboard=True, 
            one_time_keyboard=True
        )
    )
    return LOCATION


async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['location'] = update.message.location
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Вы успешно зарегистрировались!',
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Чем могу помочь Вам?',
        reply_markup=inline_button_helps(),
    )
    return ConversationHandler.END


async def callback_update_profile(update: Update, _: CallbackContext) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text='Введите ваше ФИО. Фамилия, имя и отчество введите через пробел'
    )
    return FMO_TYPING


async def stop(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    return ConversationHandler.END
