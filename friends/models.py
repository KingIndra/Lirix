from django.db import models
from django.contrib.auth.models import User

from datetime import datetime, timedelta
from django.db.models.functions import Now

# code

# 
class FriendList(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='user')
    friends = models.ManyToManyField(User, blank=True, related_name='friends')

    def __str__(self) -> str:
        return self.user.username

    def add_friend(self, account):
        if not account in self.friends.all():
            self.friends.add(account)
            self.save()

    def remove_friend(self, account):
        if account in self.friends.all():
            self.friends.remove(account)
            self.save()

    def unfriend(self, removee):
        self.remove_friend(removee)
        friends_list = FriendList.objects.get(user=removee)
        friends_list.remove_friend(self.user)
    
    def is_mutual_friend(self, friend):
        if friend in self.friends.all():
            return True
        return False


# 
class FriendRequest(models.Model):

    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='reciver')
    is_active = models.BooleanField(null=True, blank=True, default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.sender.username} to {self.receiver.username}'
    
    def accept(self):
        receiver_friend_list = FriendList.objects.get(user=self.receiver)
        if receiver_friend_list:
            receiver_friend_list.add_friend(self.sender)
            sender_friend_list = FriendList.objects.get(user=self.sender)
            if sender_friend_list:
                sender_friend_list.add_friend(self.receiver)
                self.is_active = False
                self.save()

    def decline(self):
        self.is_active = False
        self.save()

    def cancel(self):
        self.is_active = False
        self.save()

    def toggle_status(self, flag):
        self.is_active = flag
        self.save()


# 
class Notification(models.Model):

    receiver = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='received_by')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='sendt_by')
    message = models.TextField(null=True, blank=True)
    seen = models.BooleanField(null=True, blank=True, default=False)
    category = models.CharField(max_length=100, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def get_or_create(receiver, sender, message, category):
        # 
        receiver = User.objects.get(username=receiver)
        sender = User.objects.get(username=sender)
        # 
        return Notification.objects.get_or_create(
            receiver=receiver, sender=sender, message=message, category=category
        )
    
    @staticmethod
    def clear_notifications():
        Notification.objects.filter(
            seen = True,
            timestamp__lt = Now() - timedelta(days=1)
        ).delete()

    @staticmethod
    def see_notifications(user):
        Notification.objects.filter(
            receiver = user,
            seen = False
        ).update(seen = True)

    @staticmethod
    def unseen_notifications_count(user):
        count = Notification.objects.filter(
            receiver = user,
            seen = False
        ).count()
        return count
    
    @staticmethod
    def get_notifications(user):
        notifications = Notification.objects.filter(
            receiver = user,
        )
        return notifications

    def see(self):
        self.seen = True
        self.save()

    def __str__(self) -> str:
        return f'{self.sender.username} notifying {self.receiver.username}'
    

# chatting models

class Thread(models.Model):

    thread_name = models.CharField(max_length=100, null=True, blank=True)
    users = models.ManyToManyField(User)

    @staticmethod
    def get_or_create(username1, username2):
        # 
        user1 = User.objects.get(username=username1)
        user2 = User.objects.get(username=username2)
        # 
        if not FriendList.objects.get(user=user1).is_mutual_friend(user2):
            return
        # 
        thread_name = Thread.name(username1, username2)
        thread, created = Thread.objects.get_or_create(thread_name=thread_name)
        if created:
            thread.users.add(user1, user2)
        # 
        return thread, created

    @staticmethod
    def name(username1, username2):
        if username1 > username2:
            return f"thread_{username1}_{username2}"
        return f"thread_{username2}_{username1}"

    def __str__(self) -> str:
        return self.thread_name


class Message(models.Model):

    text = models.TextField(null=True, blank=True, default="")
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    @staticmethod
    def get_messages(username1, username2):
        thread_name = Thread.name(username1, username2)
        Message.objects.filter(thread__thread_name = thread_name)

    @staticmethod
    def create(text, thread_name, user):
        thread = Thread.objects.get(thread_name = thread_name)
        message = Message.objects.create(text=text, thread=thread, user=user)
        return message

    def __str__(self) -> str:
        return f"{self.text} from {self.user.username} at {self.thread.thread_name}"
    