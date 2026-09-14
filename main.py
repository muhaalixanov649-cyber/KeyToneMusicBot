import os
import telebot
from telebot import types
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    phone_button = types.KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)
    markup.add(phone_button)
    
    bot.send_message(
        message.chat.id, 
        "Salom! Botdan foydalanish uchun telefon raqamingizni yuboring:", 
        reply_markup=markup
    )

@bot.message_handler(content_types=['contact'])
def get_contact(message):
    if message.contact is not None:
        first_name = message.contact.first_name
        
        menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("🔍 Musiqa qidirish")
        btn2 = types.KeyboardButton("🔥 Top qo'shiqlar")
        menu.add(btn1, btn2)
        
        bot.send_message(
            message.chat.id, 
            f"Rahmat, {first_name}! Musiqa nomini yozib yuboring:",
            reply_markup=menu
        )

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == "🔍 Musiqa qidirish":
        bot.send_message(message.chat.id, "Musiqa nomini yoki ijrochini yozib yuboring:")
    elif message.text == "🔥 Top qo'shiqlar":
        bot.send_message(message.chat.id, "Hozircha Top qo'shiqlar ro'yxati bo'sh.")
    else:
        query = message.text
        status_msg = bot.send_message(message.chat.id, f"🔎 '{query}' bo'yicha musiqa izlanmoqda va yuklanmoqda...")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'default_search': 'ytsearch1:',
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch1:{query}", download=True)
                if 'entries' in info and len(info['entries']) > 0:
                    video_info = info['entries'][0]
                    title = video_info.get('title', 'musiqa')
                    filename = ydl.prepare_filename(video_info)
                    mp3_filename = os.path.splitext(filename)[0] + ".mp3"

                    if os.path.exists(mp3_filename):
                        with open(mp3_filename, 'rb') as audio:
                            bot.send_audio(message.chat.id, audio, caption=f"🎵 {title}\n\n🤖 @KeyToneMusicBot")
                        os.remove(mp3_filename)
                        bot.delete_message(message.chat.id, status_msg.message_id)
                    else:
                        bot.edit_message_text("❌ Audio faylni saqlashda xatolik yuz berdi.", message.chat.id, status_msg.message_id)
                else:
                    bot.edit_message_text("❌ Hech narsa topilmadi.", message.chat.id, status_msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Xatolik yuz berdi: {str(e)}", message.chat.id, status_msg.message_id)

bot.infinity_polling()
