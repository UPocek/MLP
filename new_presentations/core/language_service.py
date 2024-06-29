from googletrans import Translator

translator = Translator()

all_languages = {}

with open('static/core/extras/lang.txt', 'r') as language_file:
    for row in language_file:
        name, code = row.split(',')
        all_languages[name] = code.strip()


def get_language(name):
    return all_languages.get(name)


def get_all_languages():
    return list(all_languages.keys())


def translate_text(texts, language):
    lang = get_language(language)

    if lang != 'en':
        texts = do_translation(texts, lang)

    return texts


def do_translation(texts, dest_lang):
    new_texts = {}

    for key in texts:
        translated_key = translator.translate(
            key, dest=dest_lang, src='en').text
        new_texts[translated_key] = {}
        for sub_key in texts[key]:
            translated_sub_key = translator.translate(
                sub_key, dest=dest_lang, src='en').text
            new_texts[translated_key][translated_sub_key] = translator.translate(texts[key][sub_key], dest=dest_lang,
                                                                                 src='en').text
    return new_texts
