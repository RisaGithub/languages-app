from collections import defaultdict
import json
import re
import requests

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


def fetch_definitions(word: str):
    """Fetch definitions from DuckDuckGo dictionary and return JSON grouped by part of speech."""
    url = f"https://duckduckgo.com/js/spice/dictionary/definition/{word}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/141.0.0.0 Safari/537.36"
        ),
        "Accept": "*/*",
        "Referer": f"https://duckduckgo.com/?q={word}+definition",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Extract JSON from the JS function wrapper
    match = re.search(r"ddg_spice_dictionary_definition\((.*)\);?$", response.text, re.DOTALL)
    if not match:
        raise ValueError("Could not extract JSON payload from response")

    data = json.loads(match.group(1).strip())

    # Group definitions by part of speech
    grouped = defaultdict(list)
    for entry in data:
        part = entry.get("partOfSpeech", "unknown").lower()
        definition = entry.get("text", "").strip()
        if definition:
            grouped[part].append(definition)

    # Convert defaultdict to a normal dict for JSON serialization
    return dict(grouped)


class Definitions(APIView):
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

            definitions = fetch_definitions(word)

            return Response(
                definitions,
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
