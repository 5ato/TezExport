from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton
)
from telegram.ext import (
    ContextTypes, ConversationHandler,
    CommandHandler, MessageHandler, CallbackQueryHandler,
    filters,
)

from other import validate_name, inline_button_helps


NAME_TYPING, CONTACT, ADDRESS, LOCATION = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if context.bot_data['fermer_service'].get(update.effective_user.id):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Как я вижу, вы уже зарегистрированы, чем могу помочь?',
            reply_markup=inline_button_helps()
        )
        return ConversationHandler.END
    context.user_data['fermer'] = {}
    context.user_data['fermer']['telegram_id'] = update.effective_user.id
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Здравствуйте, cначало нужно пройти регистрацию\n\nКак вас зовут?\n\n<b><em>Фамилия, имя и отчество<u>(Необязательно)</u> введите через пробел</em></b>'
    )
    return NAME_TYPING


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = validate_name(update.message.text.split())
    if not name:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Вы ввели некорректные данные\nПовторите написать свою фамилию, имя и отчество'
        )
        return NAME_TYPING
    reply_keyboard = [[KeyboardButton('Отправить контакт', request_contact=True)]]
    if context.user_data.get('update'):
        reply_keyboard.append([KeyboardButton('Отмена')])
    context.user_data['fermer']['name'] = update.message.text.capitalize()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Поделитесь своим контактом',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return CONTACT


async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['fermer']['phone'] = update.message.contact.phone_number
    context.user_data['fermer']['username'] = update.effective_user.username
    context.user_data['fermer']['isactive'] = True
    print(context.user_data)
    reply_keyboard= None
    if context.user_data.get('update'):
        reply_keyboard = ReplyKeyboardMarkup([[KeyboardButton('Отмена')]], resize_keyboard=True, one_time_keyboard=True)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Напишите свой адрес проживания',
        reply_markup=reply_keyboard
    )
    return ADDRESS


async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['fermer']['address'] = update.effective_message.text
    reply_keyboard = [[KeyboardButton('Скинуть локацию', request_location=True), KeyboardButton('Пропустить')]]
    if context.user_data.get('update'):
        reply_keyboard.append([KeyboardButton('Отмена')])
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Отлично\nТеперь отправьте свою локацию <em>(По желанию)</em>',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return LOCATION


async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['fermer']['location'] = f'lat={update.message.location.latitude} long={update.message.location.longitude}'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='<b>Вы успешно зарегистрировались!</b>\n\nЧем могу помочь Вам?',
        reply_markup=inline_button_helps(),
    )
    if context.user_data.get('update', None): context.bot_data['fermer_service'].update(update.effective_user.id, context.user_data['fermer'])
    else: context.bot_data['fermer_service'].create(context.user_data['fermer'])
    del context.user_data['fermer']
    return ConversationHandler.END


async def callback_update_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['fermer'] = {}
    context.user_data['update'] = True
    context.user_data['fermer']['telegram_id'] = update.effective_user.id
    await update.callback_query.answer()
    await update.callback_query.delete_message()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Введите ваше ФИО.\n<b><em>Фамилия, имя и отчество<u>(Необязательно)</u> введите через пробел</em></b>',
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Отмена')]], resize_keyboard=True, one_time_keyboard=True)
    )
    return NAME_TYPING


async def callback_update_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.delete_message()
    await context.bot.send_message(
        text='Пришлите нам локацию', 
        chat_id=update.effective_chat.id,
        reply_markup=ReplyKeyboardMarkup(
            [
                [KeyboardButton('Скинуть локацию', request_location=True), KeyboardButton('Отмена')]
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
        text='<b>Вы успешно изменили локацию!</b>\n\nЧем могу помочь Вам?',
        reply_markup=inline_button_helps(),
    )
    context.bot_data['fermer_service'].update(
        update.effective_user.id, 
        {
            'location': data,
        }
    )
    return ConversationHandler.END


async def skip_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='<b>Вы успешно зарегистрировались!</b>\n\nЧем могу помочь Вам?',
        reply_markup=inline_button_helps(),
    )
    if context.user_data.get('update', None): context.bot_data['fermer_service'].update(update.effective_user.id, context.user_data['fermer'])
    else: context.bot_data['fermer_service'].create(context.user_data['fermer'])
    del context.user_data['fermer']
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    del context.user_data['fermer']
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='<b>Вы отменили обновление пользователя</b>\n\nЧем могу помочь Вам?',
        reply_markup=inline_button_helps(),
    )
    return ConversationHandler.END


user_handlers = [
    ConversationHandler(
    entry_points=[
        CommandHandler(['start'], callback=start), CallbackQueryHandler(callback_update_profile, pattern='change_profile'),
    ],
    states={
        NAME_TYPING: [MessageHandler(filters.Text(['Отмена']), callback=cancel), MessageHandler(filters.TEXT, callback=get_name)],
        CONTACT: [MessageHandler(filters.Text(['Отмена']), callback=cancel), MessageHandler(filters.CONTACT, callback=get_contact)],
        ADDRESS: [MessageHandler(filters.Text(['Отмена']), callback=cancel), MessageHandler(filters.TEXT, callback=get_address)],
        LOCATION: [
            MessageHandler((filters.LOCATION & (~ filters.FORWARDED)), callback=get_location), 
            MessageHandler(filters.Text(['Пропустить']), skip_location),
            MessageHandler(filters.Text(['Отмена']), callback=cancel)
        ],
    },
    fallbacks=[MessageHandler(filters.Text(['Отмена']), callback=cancel)],
    per_message=False
    ),
    ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_update_location, pattern='change_location')],
        states={
            LOCATION: [MessageHandler((filters.LOCATION), callback=only_location), MessageHandler(filters.Text(['Отмена']), skip_location)]
        },
        fallbacks=[MessageHandler(filters.Text('Отмена'), callback=cancel)],
    ),
]
