import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from collections import defaultdict
import concurrent.futures
import logging

logging.basicConfig(
    level=logging.DEBUG, format="[%(levelname)s] %(message)s"  # or INFO, WARNING, ERROR
)
logger = logging.getLogger(__name__)

PARTS_OF_SPEECH = {
    "noun",
    "pronoun",
    "verb",
    "adjective",
    "adverb",
    "preposition",
    "conjunction",
    "interjection",
    "article",
    "determiner",
    "numeral",
    "particle",
    "modal verb",
    "auxiliary verb",
    "gerund",
    "infinitive",
    "past participle",
    "present participle",
    "adposition",
    "cardinal number",
    "ordinal number",
    "participle",
    "prefix",
}


def parse_sentence(p, word):
    text = ""
    word_start = 0
    word_end = 0
    for elem in p.contents:
        elem_text = ""
        highlight = False
        if isinstance(elem, NavigableString):
            elem_text = elem.strip()
        elif isinstance(elem, Tag) and elem.name == "strong":
            elem_text = elem.get_text(strip=True)
            highlight = True
        if (
            text
            and text[-1] not in "\"'<({[`#@"
            and elem_text
            and elem_text[0] not in "\"'>)}]`!.:;,?$%"
        ):
            text += " "
        if highlight:
            word_start = len(text)
            word_end = word_start + len(elem_text)
        text += elem_text
    index = text.find(word)
    if not word_end and index != -1:
        word_start = index
        word_end = word_start + len(word)
    return {"text": text, "word_start_index": word_start, "word_end_index": word_end}


def fetch_url(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logger.error(f"Error fetching '{url}': {e}")
        return None


def get_glosbe_translations(
    word: str, source_language: str, target_language: str
) -> dict | None:
    if not word.strip():
        logger.warning("Empty word passed to get_glosbe_translations")
        return None

    logger.info(f"Processing word: {word}")
    base_url = f"https://glosbe.com/{source_language}/{target_language}/{word}"
    urls = [
        base_url,
        f"{base_url}/fragment/lessFrequentTranslations?phraseTranslationsIndex=0",
    ]

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = list(executor.map(fetch_url, urls))

    translations = defaultdict(list)

    popularity = 0
    for response in futures:
        if not response:
            continue

        soup = BeautifulSoup(response.content, "html.parser")

        for li in soup.select('li[data-element="translation"]'):
            phrase = li.select_one(".translation__item__pharse")
            if not phrase:
                continue

            translation_text = phrase.text.strip()
            popularity += 1

            translation_entry = {
                "translation": translation_text,
                "popularity": popularity,
            }

            example = li.select_one("div.translation__example")
            if example:
                ps = example.select("p")
                if len(ps) == 2:
                    examples = (
                        ["source_example_sentence", "translated_example_sentence"],
                        [word, translation_text],
                        ps,
                    )
                    for key, word_text, p in zip(*examples):
                        translation_entry[key] = parse_sentence(p, word_text)

            found_pos = False
            poses = li.select(".inline-block.dir-aware-pr-1")
            for pos_tag in poses:
                part_of_speech = pos_tag.text.strip().lower()
                if part_of_speech in PARTS_OF_SPEECH:
                    translations[part_of_speech].append(translation_entry)
                    found_pos = True
                elif part_of_speech.split()[0] in PARTS_OF_SPEECH:
                    translations[part_of_speech].append(translation_entry)
                    found_pos = True

            if not found_pos:
                translations["other"].append(translation_entry)

    return dict(translations) if translations else None
