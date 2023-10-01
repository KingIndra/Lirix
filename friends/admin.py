from django.contrib import admin
from .models import FriendRequest, FriendList, Notification, Thread, Message

# Register your models here.
admin.site.register(FriendList)
admin.site.register(FriendRequest)
admin.site.register(Notification)
admin.site.register(Thread)
admin.site.register(Message)
