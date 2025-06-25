from django.http import HttpResponse
from django.template import loader


def available_routes_view(request):
    base_url = request.build_absolute_uri("/")[:-1]  # removes trailing slash
    routes = [
        {
            "name": "Админка",
            "route_example": f"{base_url}/admin",
        },
        {
            "name": "Получить анонимный ID",
            "method": "POST",
            "route_template": "/api/users/create-anonymous/",
            "route_example": f"{base_url}/api/users/create-anonymous/",
        },
        {
            "name": "Перевод слова",
            "method": "GET",
            "route_template": "/api/words/translate-for-user/?user_uuid=...&word=...&source_language=...&target_language=...",
            "route_example": f"{base_url}/api/words/translate-for-user/?user_uuid=742c7560-9079-4f35-8c10-43dd1996b312&word=hello&source_language=en&target_language=ru",
        },
        {
            "name": "Получить слова, добавленные юзером",
            "method": "GET",
            "route_template": "/api/users/user-translations-by-uuid/...",
            "route_example": f"{base_url}/api/users/user-translations-by-uuid/742c7560-9079-4f35-8c10-43dd1996b312/",
        },
        {
            "name": "Получить добавленные юзером в его словарь переводы для определенного слова",
            "method": "GET",
            "route_template": "/api/users/user-translations-by-uuid-for-word/?uuid=...&word=...&source_language=...&target_language=...",
            "route_example": f"{base_url}/api/users/user-translations-by-uuid-for-word/?uuid=742c7560-9079-4f35-8c10-43dd1996b312&word=hello&source_language=en&target_language=ru",
        },
        {
            "name": "Добавить перевод в словарь юзера",
            "method": "POST",
            "route_template": "/api/users/add-translation/?uuid=...&word_text=...&translation_text=...&source_language=...&target_language=...",
            "route_example": f"{base_url}/api/users/add-translation/?uuid=742c7560-9079-4f35-8c10-43dd1996b312&word_text=hello&translation_text=привет&source_language=en&target_language=ru",
        },
        {
            "name": "Удалить перевод из словаря юзера",
            "method": "POST",
            "route_template": "/api/users/delete-translation/?uuid=...&word_text=...&translation_text=...&source_language=...&target_language=...",
            "route_example": f"{base_url}/api/users/delete-translation/?uuid=742c7560-9079-4f35-8c10-43dd1996b312&word_text=hello&translation_text=привет&source_language=en&target_language=ru",
        },
    ]

    template = loader.get_template("languages_app/available_routes.html")
    return HttpResponse(
        template.render({"routes": routes, "base_url": base_url}, request)
    )
