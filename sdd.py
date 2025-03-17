# sdd.py
from mnemonic import Mnemonic

# دالة لاستعادة الكلمة المفقودة
def recover_missing_word(seed_input, total_words):
    mnemo = Mnemonic("english")
    words = seed_input.split()
    
    if len(words) != total_words:
        return None, "❌ عدد الكلمات المدخلة لا يتطابق مع العدد المطلوب."
    
    missing_indices = [i for i, word in enumerate(words) if word == "123"]
    
    if len(missing_indices) == 0:
        return None, "ℹ️ لا توجد كلمات مفقودة."
    elif len(missing_indices) > 1:
        return None, "❌ الدعم الحالي لاستعادة الكلمة المفقودة يدعم كلمة مفقودة واحدة فقط."
    
    missing_index = missing_indices[0]
    valid_candidates = []
    
    for candidate in mnemo.wordlist:
        temp_words = words.copy()
        temp_words[missing_index] = candidate
        candidate_phrase = " ".join(temp_words)
        if mnemo.check(candidate_phrase):
            valid_candidates.append(candidate_phrase)
    
    if not valid_candidates:
        return None, "❌ لا يوجد حل صحيح لاستعادة الكلمة المفقودة."
    
    return valid_candidates, "✅ تم استعادة الكلمة المفقودة بنجاح!"