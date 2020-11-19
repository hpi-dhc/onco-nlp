import spacy

def load_spacy(language):
    spacy_lang = __languages.get(language, language)
    return spacy.load(spacy_lang)

__languages = {
        'de' : 'de_core_news_sm',
        'en' : 'en_core_web_sm'
}