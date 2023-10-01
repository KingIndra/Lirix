from django.contrib.auth.models import User

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from friends.models import FriendList, FriendRequest, Notification, Message, Thread
from chat.tasks import mail

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from celery.result import AsyncResult

from .models import Profile
from .serializers import ProfileSerializer
from utils.utils import generateOTP

from chat.tasks import add, mail, clear_otp
from chat.task import threading

from datetime import datetime, timedelta
from django.utils import timezone


# code

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request):
    data = request.data
    thread_name = Thread.name(request.user.username, data['username'])
    messages = Message.objects.filter(thread__thread_name = thread_name)
    def mapping(message):
        return {
            "text": message.text,
            "user": message.user.username
        }
    messages = list(map(mapping, messages))
    return Response(messages)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def see_notifications(request):
    context = {}
    Notification.see_notifications(request.user)
    context['message'] = 'See all Notficiations'
    return Response(context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unseen_notifications_count(request):
    context = {}
    unseen_notifications_count = Notification.unseen_notifications_count(request.user)
    context['unseen_notifications_count'] = unseen_notifications_count
    return Response(context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    context = {}
    notifications = Notification.see_notifications(request.user)
    context['notifications'] = notifications
    return Response(context)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def send_request(request):
    # 
    context = {}
    receiver = User.objects.get(username=request.data['username'])
    sender = request.user
    friend_request, created = FriendRequest.objects.get_or_create(
        sender=sender, receiver=receiver
    )
    if request.method == "GET":
        if not created: 
            friend_request.toggle_status(True)
        context['message'] = "Request Sent"

    if request.method == "PUT":
        friend_request.cancel()
        context['message'] = "Request Cancelled"

    return Response(context)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def receive_request(request):
    # 
    context = {}
    sender = User.objects.get(username=request.data['username'])
    receiver = request.user
    friend_request, _ = FriendRequest.objects.get_or_create(sender=sender, receiver=receiver)

    if request.method == "GET":
        friend_request.accept()
        context['message'] = "Request Accepted"

    elif request.method == "PUT":
        friend_request.decline()
        context['message'] = "Request Declined"

    return Response(context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unfriend_request(request):
    # 
    context = {}
    friend = User.objects.get(username = request.data['username'])
    my_friend_list = FriendList.objects.get(user = request.user)
    context['message'] = 'ERROR'

    if my_friend_list.is_mutual_friend(friend):
        my_friend_list.unfriend(friend)
        context['message'] = 'Friend Removed'
    
    return Response(context)



@api_view(['GET', 'POST', 'PUT'])
@permission_classes([IsAuthenticated])
def celery(request):
    
    profile = Profile.objects.get(user = request.user)
    context = {'email': profile.email}

    if request.method == "GET":
        a = request.data.get('a', 0)
        b = request.data.get('b', 0)
        c = request.data.get('c', 0)
        result = add.delay(a, b, c) 
        context["result"] = result.id

    elif request.method == "POST":
        task_id = request.data.get('task_id', '')
        result = AsyncResult(task_id)
        context['result'] = result.result

    elif request.method == "PUT":
        a = request.data.get('a', 0)
        b = request.data.get('b', 0)
        c = request.data.get('c', 0)
        result = threading.delay(a, b, c)
        context["result"] = result.id

    return Response(context)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def email(request):
    
    profile = Profile.objects.get(user = request.user)
    context = {'email': profile.email}
    context['username'] = profile.user.username

    def unverfiy():
        profile.email_verified = False
        profile.save()

    if request.method == 'POST':
        serializer = ProfileSerializer(instance=profile, data=request.data)
        if serializer.is_valid():
            context['email'] = serializer.save().email
            unverfiy()

    elif request.method == 'DELETE':
        profile.email = None
        profile.save()
        context['email'] = profile.email

    return Response(context)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def verify_email(request):

    profile = Profile.objects.get(user = request.user)
    context = {'email': profile.email}

    def del_otp(verified):
        profile.email_otp = None
        profile.email_verified = verified
        profile.save()

    if not profile.email:
        context['message'] = 'no email for this user'

    elif request.method == "GET":
        request.session['attempt'] = 0
        otp = generateOTP()
        profile.email_otp = otp
        profile.otp_time = datetime.now() + timedelta(minutes=5)
        profile.save()
        mail.delay("Verify Otp", f"{otp} valid for {300}s", [profile.email,])
        context['message'] = 'otp sent'
        
    elif request.method == "POST":
        request.session['attempt'] = request.session.get('attempt', 0) + 1
        context['attempt'] = request.session['attempt']

        otp = request.data.get('otp', False)
        condition = context['attempt'] < 4 and otp and profile.otp_time and profile.otp_time > timezone.now() and profile.email_otp == otp

        if condition:
            mail.delay("Confirmed", "Verified", [profile.email,])
            del_otp(True)
            context['message'] = 'otp verified'
        else:
            context['message'] = 'invalid things'

    return Response(context)


@api_view(['GET', 'POST'])
def reset_password(request):

    profile = Profile.objects.get(user = request.user)
    context = {'email': profile.email}

    def del_otp(verified):
        profile.email_otp = None
        profile.email_verified = verified
        profile.save()

    if not profile.email:
        context['message'] = 'no email for this user'

    elif request.method == "GET":
        request.session['attempt_pr'] = 0
        otp = generateOTP()
        profile.email_otp = otp
        profile.otp_time = datetime.now() + timedelta(minutes=5)
        profile.save()
        mail.delay("Reset Otp", f"{otp} valid for {300}s", [profile.email,])
        context['message'] = 'otp sent'
        
    elif request.method == "POST":
        request.session['attempt_pr'] = request.session.get('attempt_pr', 0) + 1
        context['attempt_pr'] = request.session['attempt_pr']

        otp = request.data.get('otp', False)
        new_password = request.data.get('new_password', False)

        print('otp', otp)
        print('otp_time', profile.otp_time, profile.otp_time > timezone.now())
        print('confirm otp', profile.email_otp == otp)

        condition = (
            context['attempt_pr'] < 4 and otp and 
            profile.otp_time and 
            profile.otp_time > timezone.now() and 
            profile.email_otp == otp
        )

        if condition:
            profile.user.set_password(new_password)
            profile.user.save()
            mail.delay("Confirmed", "password reseted", [profile.email,])
            del_otp(True)
            context['message'] = 'otp verified'
        else:
            context['message'] = 'invalid things'

    return Response(context)
