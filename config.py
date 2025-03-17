import os
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env
load_dotenv()

# قراءة توكن البوت من متغير بيئة
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("❌ لم يتم العثور على توكن البوت! تأكد من إضافته إلى ملف .env")