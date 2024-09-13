import telebot
import requests
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL")
client = MongoClient(MONGO_URL)
db = client.bdshortner
users = db.users

# Bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot_name = bot.get_me().first_name  # বটের প্রথম নাম নেওয়া
    bot.reply_to(message, f"Hi {message.from_user.first_name}, I am {bot_name}, the BDSHORTNER Bulk Link Converter BOT. I can convert links & post directly from your BDSHORTNER account☺️\n\n"
                          "🔰 Go To https://bdshortner.com/member/tools/api\n"
                          "🔰 Then Copy API Key\n"
                          "🔰 Then Type /api then give a single space and then paste your API Key\n\n"
                          "(See Example.👇)\n"
                          "Example: /api 04e8e1b5f12456a64c8f33195ac\n\n"
                          "💁‍♀️ Hit 👉 /help To get help")

# Add API command
@bot.message_handler(commands=['add_api'])
def add_api(message):
    api_key = message.text.split()[1]
    user_id = message.from_user.id
    users.update_one({"user_id": user_id}, {"$set": {"api_key": api_key}}, upsert=True)
    bot.reply_to(message, "API Key added successfully!")

# Add Channel command
@bot.message_handler(commands=['add_channel'])
def add_channel(message):
    user_id = message.from_user.id
    channel_id = message.text.split()[1]
    users.update_one({"user_id": user_id}, {"$set": {"channel_id": channel_id}}, upsert=True)
    bot.reply_to(message, f"Channel {channel_id} added successfully!")

# Remove Channel command
@bot.message_handler(commands=['remove_channel'])
def remove_channel(message):
    user_id = message.from_user.id
    users.update_one({"user_id": user_id}, {"$unset": {"channel_id": ""}})
    bot.reply_to(message, "Channel removed successfully!")

# Add Footer command
@bot.message_handler(commands=['add_footer'])
def add_footer(message):
    user_id = message.from_user.id
    footer_text = ' '.join(message.text.split()[1:])
    users.update_one({"user_id": user_id}, {"$set": {"footer": footer_text}}, upsert=True)
    bot.reply_to(message, "Footer added successfully!")

# Remove Footer command
@bot.message_handler(commands=['remove_footer'])
def remove_footer(message):
    user_id = message.from_user.id
    users.update_one({"user_id": user_id}, {"$unset": {"footer": ""}})
    bot.reply_to(message, "Footer removed successfully!")

# Enable Text command
@bot.message_handler(commands=['enable_text'])
def enable_text(message):
    user_id = message.from_user.id
    users.update_one({"user_id": user_id}, {"$set": {"text_enabled": True}}, upsert=True)
    bot.reply_to(message, "Text enabled for shortened links.")

# Disable Text command
@bot.message_handler(commands=['disable_text'])
def disable_text(message):
    user_id = message.from_user.id
    users.update_one({"user_id": user_id}, {"$set": {"text_enabled": False}}, upsert=True)
    bot.reply_to(message, "Text disabled for shortened links.")

# Enable Picture command
@bot.message_handler(commands=['enable_picture'])
def enable_picture(message):
    user_id = message.from_user.id
    users.update_one({"user_id": user_id}, {"$set": {"picture_enabled": True}}, upsert=True)
    bot.reply_to(message, "Picture/Video inclusion enabled.")

# Disable Picture command
@bot.message_handler(commands=['disable_picture'])
def disable_picture(message):
    user_id = message.from_user.id
    users.update_one({"user_id": user_id}, {"$set": {"picture_enabled": False}}, upsert=True)
    bot.reply_to(message, "Picture/Video inclusion disabled.")

# Change Language command
@bot.message_handler(commands=['change_language'])
def change_language(message):
    user_id = message.from_user.id
    language = message.text.split()[1]
    users.update_one({"user_id": user_id}, {"$set": {"language": language}}, upsert=True)
    bot.reply_to(message, f"Language changed to {language}.")

# Get My ID command
@bot.message_handler(commands=['getmyid'])
def get_my_id(message):
    bot.reply_to(message, f"Your Telegram ID is: {message.from_user.id}")

# Help command
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message, "Contact support at: support@bdshortner.com")

def main_convertor_handler(message, user, short_url, long_url):
    # Initialize reply text with the shortened URL
    reply_text = f"Shortened link: {short_url}"
    
    # Check if user wants text and footer
    if user.get("text_enabled", True):
        reply_text += f"\nOriginal URL: {long_url}"
    if "footer" in user:
        reply_text += f"\n{user['footer']}"
    
    bot.reply_to(message, reply_text)

# Shorten link function (automatic shortening)
@bot.message_handler(func=lambda message: True)
def shorten_link(message):
    user = users.find_one({"user_id": message.from_user.id})
    if user and "api_key" in user:
        api_key = user["api_key"]
        long_url = message.text
        response = requests.get(f"https://bdshortner.com/api?api={api_key}&url={long_url}")
        short_url = response.json().get('shortenedUrl')
        
        if short_url:
            main_convertor_handler(message, user, short_url, long_url)
        else:
            bot.reply_to(message, "Error shortening the link. Please try again.")
    else:
        bot.reply_to(message, "Please add your API key using /add_api command.")

# Run the bot
bot.polling()
