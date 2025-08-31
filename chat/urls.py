from django.urls import path
from .views import chat_api, index, home, new_chat


urlpatterns = [
    path("", home, name="home"),            # homepage
    path("chat_app/", index, name="index"), # chat app
    path("chat/", chat_api, name="chat_api"),
    path("new_chat/", new_chat, name = "new_chat")
]
