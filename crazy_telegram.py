from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from functools import partial

# command functions
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to Fliespot Bot")
    # debugging
    print(f'User ({update.message.chat.id}) did /start')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Help is still being developed")

# handle responses
def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'hello' in processed:
        return "Hello there, Welcome to Fliespot Bot"
    
    else:
        return "I don't understand"
    
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE, BOT_USERNAME):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    # debugging
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    # private and group chat filter for separate behavior
    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    # debugging
    print('Bot:', response)

    await update.message.reply_text(response)

async def send_test_message(context):
    try:
        #chat = await context.bot.get_chat(username) # test getting chat id with username (failed)
        #chat_id = chat.id
        chat_id = "1172740201" # not using username, using chat id and it works
        await context.bot.send_message(chat_id=chat_id, text="test")
    except Exception as e:
        #print(f"Failed to send message to @{username}: {e}")
        print(e)

# error logging
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


def crazyTelegram(telegram_info):

    # we are using username at the moment which is not going great, we will resort to using chat id in the future
    startTelegramBot(telegram_info['bot_token'], telegram_info['username'], telegram_info['bot_username'])


def startTelegramBot(TOKEN, username, bot_username):

    # username not utilized here, using username is a failure for now
    print("Starting bot...")
    app = Application.builder().token(TOKEN).build()

    # commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))

    # messages
    partial_handle_message = partial(handle_message, BOT_USERNAME=bot_username)
    app.add_handler(MessageHandler(filters.TEXT, partial_handle_message))

    # error handler
    app.add_error_handler(error)

    # sending test messages to specific chat id (commented because annoying)
    #job_queue = app.job_queue
    #job_queue.run_repeating(send_test_message, interval=3, first=0)

    # check updates constantly if there is user message
    print("Polling...")
    app.run_polling(poll_interval=3) # poll_interval = how often to check for new updates (5 means check each 5 seconds)