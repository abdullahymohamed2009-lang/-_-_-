import telebot
from telebot import types
import yt_dlp
import os

# --- الإعدادات الأساسية ---
API_TOKEN = '8223794583:AAGkZjYjLqfDCBBMx7VRlDW85XZgNk0U4dA'
bot = telebot.TeleBot(API_TOKEN)

links_db = {}

# --- دالة التحميل المخصصة للموبايل (بدون FFmpeg) ---
def download_media(url, mode):
    ydl_opts = {'quiet': True, 'no_warnings': True}
    if mode == 'audio':
        ydl_opts.update({
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': 'audio.m4a',
        })
        filename = 'audio.m4a'
    else:
        ydl_opts.update({
            'format': 'best[ext=mp4]/best',
            'outtmpl': 'video.mp4',
        })
        filename = 'video.mp4'

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return filename

# --- رسالة الترحيب المحدثة (الأمر /start) ---
@bot.message_handler(commands=['start'])
def welcome(message):
    # جلب بيانات المستخدم تلقائياً
    first_name = message.from_user.first_name
    username = f"@{message.from_user.username}" if message.from_user.username else "لا يوجد"
    user_id = message.from_user.id

    # نص الرسالة الجديد
    welcome_text = (
        f"أهلاً بك ي عزيزي : {first_name}\n\n"
        f"🌹اليوزر : {username}\n"
        f"🌸id : {user_id}\n\n"
        f"يمكنك التحميل من المنصات التالية:\n"
        f"يوتيوب\n"
        f"تيكتوك | إنستغرام\n"
        f"فيسبوك | جميع المواقع"
    )

    markup = types.InlineKeyboardMarkup(row_width=2)
    btns = [
        types.InlineKeyboardButton("يوتيوب 🎥", callback_data="p_yt"),
        types.InlineKeyboardButton("تيك توك 🎵", callback_data="p_tk"),
        types.InlineKeyboardButton("انستجرام 📸", callback_data="p_ig"),
        types.InlineKeyboardButton("فيس بوك 💙", callback_data="p_fb"),
        types.InlineKeyboardButton("جميع المواقع 🌍", callback_data="p_all")
    ]
    markup.add(*btns)
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

# الرد عند اختيار منصة
@bot.callback_query_handler(func=lambda call: call.data.startswith('p_'))
def platform_choice(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "تفضل بارسال الرابط وسوف يتم تنفيذ طلبك")

# استقبال الروابط
@bot.message_handler(func=lambda message: message.text.startswith('http'))
def handle_links(message):
    url = message.text
    link_id = str(message.message_id)
    links_db[link_id] = url
    
    markup = types.InlineKeyboardMarkup()
    btn_video = types.InlineKeyboardButton("تحميل فيديو 🎬", callback_data=f"dl_v_{link_id}")
    btn_audio = types.InlineKeyboardButton("تحميل أغنية 🎵", callback_data=f"dl_a_{link_id}")
    markup.add(btn_video, btn_audio)
    
    bot.reply_to(message, "كيف تريد تحميل هذا الرابط؟", reply_markup=markup)

# التحميل والإرسال
@bot.callback_query_handler(func=lambda call: call.data.startswith('dl_'))
def final_download(call):
    data = call.data.split('_')
    mode_code, link_id = data[1], data[2]
    url = links_db.get(link_id)
    
    if not url:
        bot.answer_callback_query(call.id, "انتهت صلاحية الرابط.")
        return

    mode = 'video' if mode_code == 'v' else 'audio'
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "جاري التحميل والمعالجة... ⏳")
    
    try:
        file_path = download_media(url, mode)
        with open(file_path, 'rb') as f:
            if mode == 'video':
                bot.send_video(call.message.chat.id, f, caption="تم التحميل بنجاح ✅")
            else:
                bot.send_audio(call.message.chat.id, f, caption="تم التحميل بنجاح ✅")
        
        if os.path.exists(file_path):
            os.remove(file_path)
        bot.delete_message(call.message.chat.id, msg.message_id)
        
    except Exception as e:
        bot.edit_message_text(f"حدث خطأ! تأكد من الرابط أو حاول لاحقاً.", call.message.chat.id, msg.message_id)

# تشغيل البوت
print("البوت يعمل الآن مع رسالة الترحيب الجديدة...")
bot.infinity_polling()
