import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import TOKEN
from wallets import generate_wallets, save_wallets_to_file
from sdd import recover_missing_word
import os

bot = telebot.TeleBot(TOKEN)

# 🛑 قناة التحقق من الاشتراك
CHANNEL_USERNAME = "@KeywordsChecker"  # استبدل باسم قناتك

# 🛑 تخزين الطلبات
user_requests = {}

# 🔥 الحد الأقصى لإنشاء المحافظ
MAX_WALLETS = 500  

# ✅ دالة التحقق من الاشتراك
def is_subscribed(user_id):
    try:
        chat_member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# 🟢 دالة إرسال زر الاشتراك
def send_subscription_message(chat_id):
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton("🔔 اشترك الآن", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")
    markup.add(button)
    bot.send_message(chat_id, f"🚨 يجب عليك الاشتراك في القناة لاستخدام البوت:\n{CHANNEL_USERNAME}", reply_markup=markup)

# 🟢 دالة بدء التشغيل
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not is_subscribed(message.from_user.id):
        send_subscription_message(message.chat.id)
        return
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🛠 إنشاء محفظة 12 كلمة", callback_data="wallet_12"))
    markup.add(InlineKeyboardButton("🛠 إنشاء محفظة 24 كلمة", callback_data="wallet_24"))
    markup.add(InlineKeyboardButton("🔑 استعادة كلمة مفقودة", callback_data="recover_word"))
    
    bot.send_message(message.chat.id,
                     "👋 مرحبًا بك في بوت إنشاء المحافظ واستعادة الكلمات المفقودة!\n\n"
                     "اختر من الأزرار أدناه 👇", reply_markup=markup)

# 🟢 دالة عرض المساعدة
@bot.message_handler(commands=['help'])
def send_help(message):
    if not is_subscribed(message.from_user.id):
        send_subscription_message(message.chat.id)
        return
    
    bot.reply_to(message,
                 "📝 قائمة الميزات:\n\n"
                 "• إنشاء محفظة 12 أو 24 كلمة\n"
                 "• استعادة كلمة مفقودة من العبارة السرية\n"
                 "• استخدام الأزرار بدلاً من الأوامر التقليدية")

# 🟢 دالة التعامل مع ضغط الأزرار
@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    chat_id = call.message.chat.id
    if not is_subscribed(call.from_user.id):
        send_subscription_message(chat_id)
        return

    if call.data == "wallet_12":
        user_requests[chat_id] = {"mode": "generate", "words": 12}
        bot.send_message(chat_id, f"✅ أدخل عدد المحافظ التي تريد إنشائها (بحد أقصى {MAX_WALLETS}):")
    elif call.data == "wallet_24":
        user_requests[chat_id] = {"mode": "generate", "words": 24}
        bot.send_message(chat_id, f"✅ أدخل عدد المحافظ التي تريد إنشائها (بحد أقصى {MAX_WALLETS}):")
    elif call.data == "recover_word":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔄 استعادة 12 كلمة", callback_data="sdd_12"))
        markup.add(InlineKeyboardButton("🔄 استعادة 24 كلمة", callback_data="sdd_24"))
        bot.send_message(chat_id, "🔑 اختر نوع الاستعادة:", reply_markup=markup)
    elif call.data.startswith("sdd_"):
        total_words = int(call.data.split("_")[1])
        user_requests[chat_id] = {"mode": "sdd", "total": total_words}
        bot.send_message(chat_id, 
                         f"✅ أنت في وضع استعادة الكلمة المفقودة لعبارة من {total_words} كلمة.\n"
                         "🔹 الرجاء إرسال عبارة seed الخاصة بك مع وضع `123` مكان الكلمة المفقودة.")

# 🟢 دالة استقبال عدد المحافظ المطلوبة
@bot.message_handler(func=lambda message: message.text.strip().isdigit() and 
                     message.chat.id in user_requests and user_requests[message.chat.id].get("mode") == "generate")
def handle_wallet_count(message):
    chat_id = message.chat.id
    count = int(message.text.strip())

    if not is_subscribed(message.from_user.id):
        send_subscription_message(chat_id)
        return
    
    if count <= 0:
        bot.reply_to(message, "❌ يجب أن يكون عدد المحافظ أكبر من صفر.")
        return
    elif count > MAX_WALLETS:
        bot.reply_to(message, f"⚠️ الحد الأقصى لإنشاء المحافظ هو {MAX_WALLETS} فقط.")
        return
    
    bot.send_message(chat_id, "✅ يتم الآن إنشاء المحافظ... انتظر قليلًا.")
    
    word_count = user_requests[chat_id]["words"]
    wallets = generate_wallets(word_count, count)
    file_path = save_wallets_to_file(wallets, chat_id)
    
    with open(file_path, 'rb') as file:
        bot.send_document(chat_id, file, caption="✅ تم إنشاء المحافظ بنجاح!")
    
    os.remove(file_path)
    del user_requests[chat_id]

# 🟢 دالة استقبال عبارات الاستعادة
@bot.message_handler(func=lambda message: message.chat.id in user_requests and 
                     user_requests[message.chat.id].get("mode") == "sdd")
def handle_sdd_input(message):
    chat_id = message.chat.id
    seed_input = message.text.strip()
    total_words = user_requests[chat_id]["total"]

    if not is_subscribed(message.from_user.id):
        send_subscription_message(chat_id)
        return
    
    words = seed_input.split()
    
    if len(words) != total_words or "123" not in words:
        bot.reply_to(message, f"⚠️ يجب أن تحتوي العبارة على {total_words} كلمة مع `123` مكان الكلمة المفقودة.")
        return
    
    valid_candidates, result_message = recover_missing_word(seed_input, total_words)
    
    if valid_candidates is None:
        bot.reply_to(message, result_message)
        del user_requests[chat_id]
        return
    
    file_path = save_wallets_to_file(valid_candidates, chat_id)
    
    with open(file_path, 'rb') as file:
        bot.send_document(chat_id, file, caption=result_message)
    
    os.remove(file_path)
    del user_requests[chat_id]

print("✅ البوت يعمل الآن...")
bot.polling(none_stop=True)