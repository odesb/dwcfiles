from django.conf.urls import url

from .views import HomeView, UserFileView

urlpatterns = [
        url(r'^$', HomeView.as_view()),
        url(r'^(?P<id>[\w\d]+)$', UserFileView.as_view()),
        ]
