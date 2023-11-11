#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.


Usage:

```python
python echobot.py
```

Press Ctrl-C on the command line to stop the bot.

"""

import logging

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from keys import TELEGRAM_KEY
import openai
from openai import OpenAI
from keys import OPENAI_KEY
import json





# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Grabs an image of a sailboat and analzyes it.

    Args:
        update (Update): The update object from Telegram.
    """
    #photo_file = await update.message.photo[-1].get_file()
    #openai.api_key = OPENAI_KEY

    photo_file = await update.message.photo[-1].get_file()
    photo_path = photo_file.file_path
    
    client = OpenAI(api_key=OPENAI_KEY)
    
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": """ **Prompt for ChatGPT:**

Hello ChatGPT, I need information about a specific boat. Please provide the following details based on the image or description provided:
                    (don't use \n, this is going to be displayed in a telegram message, so format it accordingly)

1. **Type of Boat:**
   - Description/Name: [Enter Description or Name of the Boat Here]

2. **Hull Length:**
   - Please estimate or provide the length of the hull.

3. **Year of Construction:**
   - Determine or estimate the year the boat was constructed. """},
                    {
                        #type of image is the local image file in photo_file
                        "type": "image",
                        "image_url": {
                            "url": photo_path,
                        },
                    },
                ],
            }
        ],
        max_tokens = 300,
    )

    # ...
    print(response.choices[0])
    # Extract the 'message' from the 'Choice' object and convert it to a JSON string
    message = json.dumps(response.choices[0].message.content)
    # Respond with the JSON string
    await update.message.reply_text(message)




def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_KEY).build()

    ## Add a handler for an Image, and have it run a new function photo()
    application.add_handler(MessageHandler(filters.PHOTO, photo))

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()