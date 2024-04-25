# rename.py

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import os
from thumbnail import generate_thumbnail

# Importing API credentials from boy.py
from bot import api_id, api_hash

# Initialize Pyrogram client
app = Client("my_bot", api_id=api_id, api_hash=api_hash)

# Define a command handler
@app.on_message(filters.command("rename") & filters.private)
async def start_rename(bot, message: Message):
    await message.reply_text(
        "Please select the type of file you want to rename:",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Document", callback_data="document"),
                InlineKeyboardButton("Video", callback_data="video")
            ]
        ])
    )

# Define a callback handler for document option
@app.on_callback_query(filters.regex("^document$"))
async def document_callback(bot, update):
    await update.answer()
    await update.message.edit_text("Please upload the document you want to rename.")

# Define a callback handler for video option
@app.on_callback_query(filters.regex("^video$"))
async def video_callback(bot, update):
    await update.answer()
    await update.message.edit_text("Please upload the video you want to rename.")

# Define a message handler for receiving documents
@app.on_message(filters.private & filters.document)
async def document_handler(bot, message):
    await rename_files(bot, message, "document")

# Define a message handler for receiving videos
@app.on_message(filters.private & filters.video)
async def video_handler(bot, message):
    await rename_files(bot, message, "video")

# Define the main function to handle renaming
async def rename_files(bot, message: Message, file_type: str):
    # Check if a thumbnail is attached
    if message.photo:
        thumbnail = message.photo[-1]  # Get the last photo in the message as the thumbnail
        new_name = message.text  # Get the new name from the message text

        # Download the file
        file_path = f'temp_{file_type}'
        await message.download(file_name=file_path)

        # Generate and download the thumbnail
        thumbnail_path = 'temp_thumbnail.jpg'
        await thumbnail.download(file_name=thumbnail_path)
        thumbnail_success = generate_thumbnail(thumbnail_path, thumbnail_path)

        if thumbnail_success:
            # Rename the file
            os.rename(file_path, new_name)

            # Send the renamed file with the custom thumbnail
            if file_type == "document":
                await bot.send_document(message.chat.id, document=new_name, thumb=thumbnail_path)
            elif file_type == "video":
                await bot.send_video(message.chat.id, video=new_name, thumb=thumbnail_path)

            # Remove the temporary files
            os.remove(new_name)
            os.remove(thumbnail_path)
        else:
            await bot.send_message(message.chat.id, "Error generating thumbnail.")
    else:
        await bot.send_message(message.chat.id, "Please attach a custom thumbnail.")

# Run the bot
app.run()
