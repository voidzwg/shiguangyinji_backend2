from django.urls import path
from .views import AIChat

urlpatterns = [
    path('start/', AIChat.as_view()),
    path('ask/', AIChat.as_view()),
]