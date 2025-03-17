from mnemonic import Mnemonic
import os
from concurrent.futures import ThreadPoolExecutor

# دالة مساعدة لتحديد مسار حفظ الملفات
def get_temp_file_path(chat_id, filename_prefix):
    temp_directory = "/storage/emulated/0/bot_wallets/"
    if not os.path.exists(temp_directory):
        os.makedirs(temp_directory)
    return os.path.join(temp_directory, f"{filename_prefix}_{chat_id}.txt")

# دالة لإنشاء محفظة واحدة
def generate_single_wallet(word_count):
    mnemo = Mnemonic("english")
    strength = 128 if word_count == 12 else 256
    return mnemo.generate(strength=strength)

# دالة لإنشاء المحافظ بسرعة باستخدام الـ ThreadPoolExecutor
def generate_wallets(word_count, count):
    with ThreadPoolExecutor() as executor:
        wallets = list(executor.map(lambda _: generate_single_wallet(word_count), range(count)))
    return wallets

# دالة لحفظ المحافظ في ملف
def save_wallets_to_file(wallets, chat_id):
    file_path = get_temp_file_path(chat_id, "wallets")
    with open(file_path, "w") as file:
        file.writelines(f"{wallet}\n\n" for wallet in wallets)
    return file_path