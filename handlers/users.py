from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from telegram.ext import (
    ContextTypes, ConversationHandler,
    CommandHandler, MessageHandler, CallbackQueryHandler,
    filters,
)

from .message import localization
from other import inline_button_helps, validate_phone, get_inline_language


LANGUAGE, NAME_TYPING, CONTACT, ADDRESS, LOCATION = range(5)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = context.bot_data['fermer_service'].get(update.effective_user.id)
    if user:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=localization[user.language]['check_user_true'],
            reply_markup=inline_button_helps(user.language)
        )
        return ConversationHandler.END
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Здравствуйте, cначало нужно пройти регистрацию\n\n<b>Выберите язык</b>',
        reply_markup=get_inline_language(),
    )
    context.user_data['fermer'] = {}
    context.user_data['fermer']['telegram_id'] = update.effective_user.id
    return LANGUAGE


async def callback_get_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    context.user_data['fermer']['language'] = update.callback_query.data
    await update.callback_query.edit_message_text(
        text=localization[context.user_data['fermer']['language']]['name_typing']
    )
    return NAME_TYPING


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [[KeyboardButton(localization[context.user_data['fermer']['language']]['contact'], request_contact=True)]]
    if context.user_data.get('update'):
        reply_keyboard.append([KeyboardButton(localization[context.user_data['fermer']['language']]['cancel'])])
    context.user_data['fermer']['name'] = update.message.text.capitalize()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=localization[context.user_data['fermer']['language']]['get_contact'],
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return CONTACT


async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.contact: context.user_data['fermer']['phone'] = update.message.contact.phone_number
    else:
        phone = validate_phone(update.effective_message.text)
        if phone: context.user_data['fermer']['phone'] = phone
        else: 
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=localization[context.user_data['fermer']['language']]['wrong_phone']
            )
            return CONTACT
    context.user_data['fermer']['username'] = update.effective_user.username
    context.user_data['fermer']['isactive'] = True
    print(context.user_data)
    reply_keyboard= None
    if context.user_data.get('update'):
        reply_keyboard = ReplyKeyboardMarkup([[KeyboardButton(localization[context.user_data['fermer']['language']]['cancel'])]], resize_keyboard=True, one_time_keyboard=True)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=localization[context.user_data['fermer']['language']]['typing_address'],
        reply_markup=reply_keyboard
    )
    return ADDRESS


async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['fermer']['address'] = update.effective_message.text
    reply_keyboard = [
        [
            KeyboardButton(localization[context.user_data['fermer']['language']]['get_location'], request_location=True), 
            KeyboardButton(localization[context.user_data['fermer']['language']]['skip'])
        ]
    ]
    if context.user_data.get('update'):
        reply_keyboard.append([KeyboardButton(localization[context.user_data['fermer']['language']]['cancel'])])
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=localization[context.user_data['fermer']['language']]['send_location'],
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return LOCATION


async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['fermer']['location'] = f'lat={update.message.location.latitude} long={update.message.location.longitude}'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=localization[context.user_data['fermer']['language']]['reg_success'],
        reply_markup=ReplyKeyboardRemove(True),
    )
    context.user_data['language'] = context.user_data['fermer']['language']
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=localization[context.user_data['fermer']['language']]['home_menu'], 
        reply_markup=inline_button_helps(context.user_data['fermer']['language'])
    )
    if context.user_data.get('update', None): context.bot_data['fermer_service'].update(update.effective_user.id, context.user_data['fermer'])
    else: context.bot_data['fermer_service'].create(context.user_data['fermer'])
    del context.user_data['fermer']
    return ConversationHandler.END


async def callback_update_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['fermer'] = {}
    context.user_data['update'] = True
    context.user_data['fermer']['telegram_id'] = update.effective_user.id
    language = context.bot_data['fermer_service'].get_only_language(update.effective_user.id)
    await update.callback_query.answer()
    await update.callback_query.delete_message()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=localization[language]['choose_lang'],
        reply_markup=get_inline_language()
    )
    return LANGUAGE


async def callback_update_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.delete_message()
    language = context.bot_data['fermer_service'].get_only_language(update.effective_user.id)
    context.user_data['language'] = language
    await context.bot.send_message(
        text=localization[language]['update_location'], 
        chat_id=update.effective_chat.id,
        reply_markup=ReplyKeyboardMarkup(
            [
                [
                    KeyboardButton(localization[context.user_data['language']]['get_location'], request_location=True), 
                    KeyboardButton(localization[context.user_data['language']]['cancel'])]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    return LOCATION


async def only_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    data = f'lat={update.message.location.latitude} long={update.message.location.longitude}'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=localization[context.user_data['language']]['location_success'],
        reply_markup=ReplyKeyboardRemove(True),
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=localization[context.user_data['language']]['home_menu'], 
        reply_markup=inline_button_helps(context.user_data['language'])
    )
    context.bot_data['fermer_service'].update(
        update.effective_user.id, 
        {
            'location': data,
        }
    )
    del context.user_data['language']
    return ConversationHandler.END


async def skip_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=localization[context.user_data['fermer']['language']]['update_success'],
        reply_markup=ReplyKeyboardRemove(True),
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=localization[context.user_data['fermer']['language']]['home_menu'], 
        reply_markup=inline_button_helps(context.user_data['fermer']['language'])
    )
    if context.user_data.get('update', None): context.bot_data['fermer_service'].update(update.effective_user.id, context.user_data['fermer'])
    else: context.bot_data['fermer_service'].create(context.user_data['fermer'])
    del context.user_data['fermer']
    return ConversationHandler.END


async def cancel_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=localization[context.user_data['language']]['cancel_location'],
        reply_markup=ReplyKeyboardRemove(True),
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=localization[context.user_data['language']]['home_menu'], 
        reply_markup=inline_button_helps(context.user_data['language'])
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    del context.user_data['fermer']
    language = context.bot_data['fermer_service'].get_only_language(update.effective_user.id)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=localization[language]['cancel_update'],
        reply_markup=ReplyKeyboardRemove(True),
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=localization[language]['home_menu'], 
        reply_markup=inline_button_helps(language)
    )
    return ConversationHandler.END


user_handlers = [
    ConversationHandler(
    entry_points=[
        CommandHandler(['start'], callback=start), CallbackQueryHandler(callback_update_profile, pattern='change_profile'),
    ],
    states={
        LANGUAGE: [MessageHandler(filters.Text(['Отмена', 'Bekor qilish', 'Cancel']), callback=cancel), CallbackQueryHandler(callback_get_language)],
        NAME_TYPING: [MessageHandler(filters.Text(['Отмена', 'Bekor qilish', 'Cancel']), callback=cancel), MessageHandler(filters.TEXT, callback=get_name)],
        CONTACT: [
            MessageHandler(filters.Text(['Отмена', 'Bekor qilish', 'Cancel']), callback=cancel),
            MessageHandler(filters.TEXT, callback=get_contact),
            MessageHandler(filters.CONTACT, callback=get_contact), 
        ],
        ADDRESS: [MessageHandler(filters.Text(['Отмена', 'Bekor qilish', 'Cancel']), callback=cancel), MessageHandler(filters.TEXT, callback=get_address)],
        LOCATION: [
            MessageHandler((filters.LOCATION & (~ filters.FORWARDED)), callback=get_location), 
            MessageHandler(filters.Text(['Пропустить', "O'tkazib yuborish", 'Skip']), skip_location),
            MessageHandler(filters.Text(['Отмена', 'Bekor qilish', 'Cancel']), callback=cancel)
        ],
    },
    fallbacks=[MessageHandler(filters.Text(['Отмена', 'Bekor qilish', 'Cancel']), callback=cancel)],
    per_message=False
    ),
    ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_update_location, pattern='change_location')],
        states={
            LOCATION: [
                MessageHandler((filters.LOCATION), callback=only_location), 
                MessageHandler(filters.Text(['Отмена', 'Bekor qilish', 'Cancel']), cancel_location),
            ]
        },
        fallbacks=[MessageHandler(filters.Text(['Отмена', 'Bekor qilish', 'Cancel']), callback=cancel)],
    ),
]
