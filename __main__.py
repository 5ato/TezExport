from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton, 
    InlineKeyboardButton, InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder, Defaults, MessageHandler, filters,
    CommandHandler, ContextTypes, ConversationHandler, CallbackContext,
    CallbackQueryHandler,
)
from telegram.constants import ParseMode

from configuration import BotSettings
from other import validate_fmo

from datetime import timezone, timedelta


FMO_TYPING, CONTACT, LOCATION = range(3)


def inline_button_helps() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton('Изменить профиль', callback_data='change_profile')]]
    )


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


async def change_profile_callback(update: Update, _: CallbackContext) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text='Введите ваше ФИО. Фамилия, имя и отчество введите через пробел'
    )
    return FMO_TYPING


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return ConversationHandler.END


if __name__ == '__main__':
    defaults = Defaults(parse_mode=ParseMode.HTML, tzinfo=timezone(offset=timedelta(hours=5), name='UZ'))
    application = ApplicationBuilder().token(BotSettings.TOKEN).defaults(defaults).build()
    application.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler(['start'], callback=start), CallbackQueryHandler(change_profile_callback),
        ],
        states={
            FMO_TYPING: [MessageHandler(filters.ALL, callback=get_fmo)],
            CONTACT: [MessageHandler(filters.CONTACT, callback=get_contact)],
            LOCATION: [MessageHandler(filters.LOCATION, callback=get_location)],
        },
        fallbacks=[MessageHandler(filters.Text(['stop']), callback=stop)],
        per_message=False
    ))
    application.add_handler(CallbackQueryHandler(change_profile_callback))
    application.run_polling()
    