import os
from zipfile import ZipFile
from werkzeug.utils import secure_filename
from datetime import datetime

import os

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')


# Create the downloads directory
os.makedirs('downloads', exist_ok=True)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup, \
    KeyboardButton
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackContext, \
    CallbackQueryHandler

# define all car
car_dict = {'Ibishu 200BX': 'coupe',
            'ETK 800 Series': 'etk800',
            'ETK K-Series': 'etkc',
            'ETK I-Series': 'etki',
            'Ibishu Pessima OLD': 'pessima',
            'Ibishu Pessima NEW': 'midsize',
            'Ibishu Covet': 'covet',
            'Hirochi SBR4': 'sbr',
            'Bruckell Bastion': 'bastion',
            'Gavril Grand Marshal': 'fullsize',
            'Civetta Scintilla': 'scintilla',
            'Autobello Piccolina': 'autobello',
            'Bruckell LeGran': 'legran',
            'Bruckell Moonhawk': 'moonhawk',
            'Burnside Special': 'burnside',
            'Cherrier Vivace/Tograc': 'vivace',
            'Gavril Barstow': 'barstow',
            'Gavril Bluebuck': 'bluebuck',
            'Gavril D-Series': 'pickup',
            'Gavril H-Series': 'van',
            'Gavril Roamer': 'roamer',
            'Gavril T-Series': 'semi',
            'Hirochi Sunburst': 'sunburst',
            'Ibishu Hopper': 'hopper',
            'Ibishu Miramar': 'miramar',
            'Ibishu Pigeon': 'pigeon',
            'Ibishu Wigeon': 'wigeon',
            'Soliad Wendover': 'wendover',
            'Civetta Bolide': 'bolide',
            'Wentward DT40L': 'citybus'}

# Define conversation states
MODE, CAR_NAME, FILE, FILE_NAME = range(4)


def make_jbeam(name, current_car):
    jbeam_path = current_car + '.jbeam'
    if name:
        with open('template/template.jbeam', 'r') as file:
            repl = file.read().replace('RAD', 'This skin make by computer, the future is near')
            repl = repl.replace('AUT', 'Program by fylhtq7779')
            repl = repl.replace('NAME', name)
            repl = repl.replace('GNAM', name)
            repl = repl.replace('CARSS', current_car)
        with open(jbeam_path, 'w') as file:
            file.writelines(repl)


def make_json(name, current_car):
    json_path = 'materials.json'
    if name:
        with open('template/' + current_car + '.json', 'r') as file:
            repl = file.read().replace('SKINNAME', name)
        with open(json_path, 'w') as file:
            file.writelines(repl)


def start(update, context):
    """Show a menu with mode options."""
    keyboard = [
        [KeyboardButton('Сделать скин / Make Skin')],
        #[KeyboardButton('Make Application')]
    ]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,  # This option will make the buttons smaller or larger to fit the screen.
        one_time_keyboard=True,  # This option will hide the keyboard after the user selects a button.
        selective=True  # This option will show the keyboard only to users that have interacted with the bot.
    )
    update.message.reply_text(
        'Please select a mode:',
        reply_markup=reply_markup
    )
    return MODE


def mode_selected(update, context):
    """Save the selected mode and show a submenu with car options."""
    user = update.message.from_user
    selected_mode = update.message.text
    context.user_data['mode'] = selected_mode

    # Create the car options as inline buttons
    car_names = list(car_dict.keys())

    # keyboard list
    keyboard = []

    # loop over car names and add each car as a new button
    for car_name in car_names:
        keyboard.append([InlineKeyboardButton(car_name, callback_data=car_name)])
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Выберите машину' + '\n' + 'Select a car:', reply_markup=reply_markup)

    return CAR_NAME


def car_options_selected(update, context):
    query = update.callback_query
    print(query.data)
    context.user_data['car_name'] = query.data
    query.message.reply_text(
        'Введите имя скина, только английские символы, без пробелов' + '\n' + 'Enter a name for the file (English characters only, no spaces):')
    return FILE_NAME


# def car_name_selected(update: Update, context: CallbackContext) -> int:
#     # Save the selected car name
#     query = update.callback_query
#     query.answer()
#     selected_car = query.data
#     context.user_data['car_name'] = selected_car
#     current_car = car_dict.get(update.message.text)
#
#     # Ask the user for a name for the file
#     update.message.reply_text(current_car)
#     update.message.reply_text('Please enter a name for the file (English characters only, no spaces):')
#
#
#     # Go to the next state
#     return FILE_NAME


def file_name_selected(update: Update, context: CallbackContext) -> int:
    # Save the entered file name
    file_name = update.message.text

    # Check that the file name is valid
    if not file_name.isalnum():
        update.message.reply_text(
            'Неправильное имя, только англйиские буквы, без пробелов' + '\n' + 'Invalid file name. Please enter a name using English characters and no spaces.')
        return FILE_NAME

    # Save the file name in the user data
    current_car = car_dict.get(context.user_data['car_name'])
    make_jbeam(file_name, current_car)
    make_json(file_name, current_car)

    context.user_data['file_name'] = file_name

    # Go to the next state
    update.message.reply_text('Отправьте DDS файл' + '\n' + 'Upload the DDS file:')
    return FILE


def file_uploaded(update: Update, context: CallbackContext) -> int:
    # Initialize paths to None
    new_file_path, jbeam_path, json_path, archive_path = [None] * 4

    # Get the file from the message
    file = context.bot.get_file(update.message.document.file_id)

    # Download the file
    file_path = os.path.join('downloads', secure_filename(file.file_path))
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file.download(file_path)

    # Rename the file
    file_name = context.user_data['file_name']
    file_ext = os.path.splitext(file_path)[1]
    new_file_path = os.path.join('downloads', secure_filename(
        car_dict.get(context.user_data['car_name']) + "_skin_" + file_name + file_ext))
    os.rename(file_path, new_file_path)

    try:
        # Create the zip archive
        current_car = car_dict.get(context.user_data['car_name'])
        archive_name = file_name + '_skin.zip'
        archive_path = os.path.join(os.getcwd(), archive_name)

        jbeam_path = current_car + '.jbeam'
        json_path = 'materials.json'

        with ZipFile(archive_path, 'w') as zip:
            zip.write(new_file_path,
                      'vehicles/' + current_car + '/' + context.user_data['file_name'] + '/' + os.path.basename(
                          new_file_path))
            zip.write(jbeam_path,
                      'vehicles/' + current_car + '/' + context.user_data['file_name'] + '/' + os.path.basename(
                          jbeam_path))
            zip.write(json_path,
                      'vehicles/' + current_car + '/' + context.user_data['file_name'] + '/' + os.path.basename(
                          json_path))

        # Send the zip archive
        with open(archive_path, 'rb') as zip_file:
            update.message.reply_document(document=zip_file)
            write_log(update, context)  # Запись информации об успешной отправке в лог

    finally:
        # Delete files in a try block in case they don't exist
        try:
            if new_file_path:
                os.remove(new_file_path)
            if archive_path:
                os.remove(archive_path)
            if jbeam_path:
                if os.path.exists(jbeam_path):
                    os.remove(jbeam_path)
            if json_path:
                if os.path.exists(json_path):
                    os.remove(json_path)
        except Exception as e:
            print(f'Error occurred when trying to delete files: {e}')

    # Show a menu with mode options
    keyboard = [
        [KeyboardButton('Сделать скин / Make Skin')],
        [KeyboardButton('Make Application')]
    ]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,  # This option will make the buttons smaller or larger to fit the screen.
        one_time_keyboard=True,  # This option will hide the keyboard after the user selects a button.
        selective=True  # This option will show the keyboard only to users that have interacted with the bot.
    )
    update.message.reply_text(
        'Please select a mode:',
        reply_markup=reply_markup
    )
    return MODE

def write_log(update: Update, context: CallbackContext) -> None:
    """Записать логин и дату в формате, совместимом с Excel, в файл статистики."""
    user = update.message.from_user
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Форматирование даты и времени для Excel
    log_message = f"{user.username or user.first_name}, {current_time}\n"

    # Открываем файл на добавление новой строки
    with open('stats.txt', 'a') as log_file:
        log_file.write(log_message)


def back(update, context):
    """Go back to the previous menu."""
    reply_keyboard = [['Сделать скин / Make Skin', 'Make Application']]
    update.message.reply_text(
        'Please select a mode:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )

    return MODE


def cancel(update, context):
    """Cancel the conversation."""
    update.message.reply_text(
        'Conversation canceled.', reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main():
    # Create the updater and dispatcher
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Define the conversation handler with its states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), MessageHandler(Filters.all, start)],
        states={
            MODE: [MessageHandler(Filters.regex('^Сделать скин / Make Skin$|^Make Application$'), mode_selected)],
            CAR_NAME: [CallbackQueryHandler(car_options_selected)],
            FILE_NAME: [MessageHandler(Filters.text, file_name_selected)],
            FILE: [MessageHandler(Filters.document, file_uploaded)]
        },
        fallbacks=[
            CommandHandler('start', start),
            MessageHandler(Filters.all, start),
            # Additional fallback handler to handle any input that does not match any of the states or entry points
            MessageHandler(Filters.all, lambda update, context: start(update, context))
        ]
    )

    # Add the conversation handler to the dispatcher
    dispatcher.add_handler(conv_handler)

    # Start the bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()