from django.urls import path
from . import views

urlpatterns = [
    # 
    path("send_request/", views.send_request, name="send_request"),
    path("receive_request/", views.receive_request, name="receive_request"),
    path("unfriend_request/", views.unfriend_request, name="unfriend_request"),
    # 
    path("see_notifications/", views.see_notifications, name="see_notifications"),
    path("get_unseen_notifications_count/", views.get_unseen_notifications_count, name="get_unseen_notifications_count"),
    path("get_notifications/", views.get_notifications, name="get_notifications"),
    # 
    path("get_messages/", views.get_messages, name="get_messages"),
]
