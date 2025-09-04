from django.views.generic import TemplateView

class IndexView(TemplateView):
    print('IndexView')
    template_name = 'index_demo.html'
