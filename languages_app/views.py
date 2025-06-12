from django.http import HttpResponse
from django.template import loader
from django.urls import get_resolver

def available_routes_view(request):
	routes = []
	url_patterns = get_resolver().url_patterns

	for pattern in url_patterns:
		try:
			routes.append(str(pattern.pattern))
		except:
			pass

	base_url = request.build_absolute_uri('/')[:-1]  # removes trailing slash
	template = loader.get_template('languages_app/available_routes.html')
	return HttpResponse(template.render({'routes': routes, 'base_url': base_url}, request))
