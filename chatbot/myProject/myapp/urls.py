#urls.py

from django.urls import path
from . import views
from .views import chat, python_editor_view, run_python_code


urlpatterns = [
    path('', views.index, name='index'),
    path('chat/', chat, name='chat'),
    path('', python_editor_view, name='index'),
    path('run_python_code/', run_python_code, name='run_python_code'),
]