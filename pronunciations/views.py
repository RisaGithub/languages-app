from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from typing import Dict, List, Optional
import requests

from bs4 import BeautifulSoup
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

BASE_URL = "https://dictionary.cambridge.org"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}


def fetch_html(word: str) -> Optional[str]:
    """Fetch the HTML page for a given English word from Cambridge Dictionary."""
    url = f"{BASE_URL}/pronunciation/english/{word}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Failed to fetch '{word}': {e}")
        return None


def extract_meaning(pron_block):
    """
    Extracts the meaning text from a pron_block, collecting all text between
    .header and the first .region-block. Text inside any '.gw' element (at any nested level)
    is lowercased.
    """
    header = pron_block.select_one(".header")
    first_region = pron_block.select_one(".region-block")
    if not header or not first_region:
        return ""

    def is_inside_gw(text_node):
        """Return True if text_node is inside any element with class 'gw'."""
        parent = text_node.parent
        while parent:
            if parent.has_attr("class") and "gw" in parent["class"]:
                return True
            parent = parent.parent
        return False

    parts = []
    for el in header.find_next_siblings():
        if el == first_region:
            break

        # iterate over all text nodes
        for text_node in el.descendants:
            if isinstance(text_node, str):
                text = text_node.strip()
                if text:
                    if is_inside_gw(text_node):
                        text = text.lower()
                    parts.append(text)

    meaning = " ".join(parts).strip()

    # Cleanup special characters
    if meaning.startswith("(") and meaning.endswith(")"):
        meaning = meaning[1:-1]
    meaning = meaning.replace("( ", "(").replace(" )", ")").replace(' , ', ', ')

    return meaning


def merge_same_keys(pronunciations):
    """
    Merge entries in `pronunciations` that have identical pronunciation data.
    """
    prons_to_keys = defaultdict(list)

    for key, prons in pronunciations.items():
        # Convert dict to a canonical, hashable form (JSON string)
        prons_key = json.dumps(prons, ensure_ascii=False)
        prons_to_keys[prons_key].append(key)

    merged = {}
    for prons_key, keys in prons_to_keys.items():
        # Build a human-friendly combined key
        if len(keys) == 1:
            combined_key = keys[0]
        else:
            combined_key = ", ".join(keys[:-1]) + f" and {keys[-1]}"

        # Deserialize back into a dict
        merged[combined_key] = json.loads(prons_key)

    return merged


def parse_pronunciations(html: str) -> Dict:
    """Parse the Cambridge Dictionary pronunciation page HTML into a structured dictionary."""
    soup = BeautifulSoup(html, "html.parser")
    page = soup.select_one(".page")
    if not page:
        return {}

    pronunciations = {}
    found_audios = {}

    for term_block in page.select(".term-block"):
        spelling = term_block.find("h2")
        if not spelling:
            continue
        spelling_text = spelling.text.strip()
        pronunciations[spelling_text] = {}

        for pron_block in term_block.select(".pron-block"):
            meaning = extract_meaning(pron_block)
            pronunciations[spelling_text][meaning] = {}

            for region_block in pron_block.select(".region-block"):
                region_name = _extract_region_name(region_block)
                if not region_name:
                    continue

                pronunciations[spelling_text][meaning][region_name] = {}

                for selector in [".pron-info", ".primary-pron"]:
                    for pron_info in region_block.select(selector):
                        transcription = pron_info.select_one(".ipa")
                        transcription_text = transcription.text.strip() if transcription else ""
                        audio = pron_info.select_one('[type="audio/mpeg"]')
                        audio_key = (region_name, transcription)
                        audio_url = BASE_URL + audio.get("src") if audio else found_audios.get(audio_key)

                        prons = pronunciations[spelling_text][meaning][region_name]
                        prons.setdefault(transcription_text, [])
                        if audio_url and audio_url not in prons[transcription_text]:
                            prons[transcription_text].append(audio_url)
                            found_audios[audio_key] = audio_url

            # merge meanings with same pronunciations
            pronunciations[spelling_text] = merge_same_keys(pronunciations[spelling_text])

    # merge spellings with same pronunciations
    return merge_same_keys(pronunciations)


def _extract_region_name(region_block) -> Optional[str]:
    """Extract the pronunciation region (US/UK/etc.) from a region block."""
    first_pron = region_block.select_one(".pron-info")
    if first_pron:
        region = first_pron.get("data-pron-region")
        if region:
            return region
        sound = first_pron.select_one(".soundfile span")
        if sound:
            return sound.text.strip()
    primary_pron = region_block.select_one(".primary-pron span")
    return primary_pron.text.strip() if primary_pron else None


def get_pronunciations(words: List[str], max_workers: int = 5) -> list:
    """Get pronunciations for multiple English words concurrently."""
    results = ['' for _ in words]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_word = {executor.submit(fetch_html, word): (i, word) for i, word in enumerate(words)}

        for future in as_completed(future_to_word):
            i, word = future_to_word[future]
            html = future.result()
            if html:
                pronunciations = parse_pronunciations(html)
                results[i] = pronunciations or {"error": "No pronunciations found"}
            else:
                results[i] = {"error": "Failed to fetch page"}

    return results


class Pronunciations(APIView):
    def get(self, request):
        word = request.query_params.get("word")

        if not word:
            return Response(
                {
                    "error": "Missing required parameter: word."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:

            return Response(
                get_pronunciations([word])[0],
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
