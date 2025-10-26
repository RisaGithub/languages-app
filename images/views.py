from ddgs import DDGS
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class ImageURLs(APIView):
    def get(self, request):
        query = request.query_params.get("query")
        max_results = int(request.query_params.get("max_results"))

        if not query:
            return Response(
                {
                    "error": "Missing required parameter: query."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with DDGS() as ddgs:
                img_urls = []
                for result in ddgs.images(
                        query=query,
                        max_results=max_results,
                        safesearch="Off",
                        region="wt-wt",
                        timelimit=None,
                ):
                    img_urls.append(result['image'])

            return Response(
                img_urls,
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
