import requests
from bs4 import BeautifulSoup

TRANSLATIONS = {
    "record": {
        "запись": {"part_of_speech": "noun", "gender": "feminine"},
        "рекорд": {"part_of_speech": "noun", "gender": "masculine"},
        "записывать": {"part_of_speech": "verb", "aspect": "imperfective"},
    },
    "book": {
        "книга": {"part_of_speech": "noun", "gender": "feminine"},
        "бронировать": {"part_of_speech": "verb", "aspect": "imperfective"},
    },
}


def get_glosbe_translations(word, source_language, target_language):
    #url = f"https://glosbe.com/{source_language}/{target_language}/{word}"
    #response = requests.get(url)
    #soup = BeautifulSoup(response.content, "lxml")

    translations = {}

    return TRANSLATIONS
