import wikipedia
import wikipediaapi
from core.language_service import get_language, translator


def find_url(title, language):
    wiki = wikipediaapi.Wikipedia('en')

    page = wiki.page(title)

    return page.fullurl, page.summary, page.sections, page.title


def results_for_title(title, language):
    results = []
    wikipedia.set_lang('en')

    lang = get_language(language)

    if lang != 'en':
        title = translator.translate(title, src=lang, dest='en').text

    try:
        results = wikipedia.search(title, results=5)
    except Exception:
        pass

    return results
