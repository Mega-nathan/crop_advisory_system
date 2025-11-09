# from langdetect import detect, DetectorFactory
# from deep_translator import GoogleTranslator

# DetectorFactory.seed = 0  # For consistent results

# def detect_language(text):
#     """
#     Detect the language of the input text.
#     Returns the ISO 639-1 language code (e.g., 'en', 'hi').
#     """
#     try:
#         lang = detect(text)
#     except:
#         lang = "en"  # default to English if detection fails
#     print(f"Detected language: {lang}")
#     return lang

# def translate_to_english(text, src_lang):
#     """
#     Translate text from src_lang to English.
#     If already English, returns the text as is.
#     """
#     if src_lang == 'en':
#         return text
#     try:
#         translated = GoogleTranslator(source='auto', target='en').translate(text)
#         return translated
#     except Exception as e:
#         print("Translation to English error:", e)
#         return text

#     def translate_to_user_language(text, target_lang):
#         """
#         Translate English text to the target language (user's language).
#         If target language is English, returns the text as is.
#         """
#         if target_lang == 'en':
#             return text
#         try:
#             translated = GoogleTranslator(source='en', target=target_lang).translate(text)
#             return translated
#         except Exception as e:
#             print("Translation to user language error:", e)
#             return text






# '''from langdetect import detect, DetectorFactory
# DetectorFactory.seed = 0  # For consistent results
# from googletrans import Translator
# translator = Translator()


# def detect_language(text):
#     try:
#         lang = detect(text)
#     except:
#         lang = "en"  # default to English if detection fails
#     print(lang)
#     return lang

# def translate_to_english(text, src_lang):
#     """
#     Translate text from src_lang to English.
#     If already English, returns the text as is.
#     """
#     if src_lang == 'en':
#         return text
#     try:
#         translated = translator.translate(text, src='auto', dest='en')
#         return translated.text
#     except:
#         return text
    
# def translate_to_user_language(text, target_lang):
#     """
#     Translate English text to the target language (user's language).
#     If target language is English, returns the text as is.
#     """
#     if target_lang == 'en':
#         return text
#     try:
#         translated = translator.translate(text, src='en', dest=target_lang)
#         return translated.text
#     except Exception as e:
#         print("Translation error:", e)
#         return text'''
