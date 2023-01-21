from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    author = 'about/author.html'


class AboutTechView(TemplateView):
    tech = 'about/tech.html'
