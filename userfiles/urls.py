# userfiles/urls.py
from django.urls import path

from .views import HomePageView, CreateFileView
from chat.views import generate_chatbot_response, get_chatbot_response
urlpatterns = [
    path("upload/", HomePageView.as_view(), name="file_upload"),
    path("files/", CreateFileView.as_view(), name="add_file"),
    
    path('get_chatbot_response/', get_chatbot_response, name='get_chatbot_response'),

    ]

