from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import POST, Like, Comment
from .forms import PostCreateForm, CommentForm


@login_required
def poetry(request):
    posts = POST.objects.all().order_by('-date_posted')
    likes = []
    for post in posts:
        likes.append(post.liked_by_user(request.user.id))
    ziplist = zip(posts, likes)
    data = {
        "lists" : ziplist
    }
    return render(request, 'blog/poetry.html', context=data)


@login_required
def poetry_detail(request, post_id):
    context = {}
    post = POST.objects.get(id=post_id)
    context['post'] = post
    liked = post.liked_by_user(user_id=request.user.id)
    context['liked'] = liked
    return render(request, 'blog/poetry_detail.html', context)


@login_required
def poetry_create(request):
    context = {}
    if request.method=="POST":
        print(request.POST)
        form = PostCreateForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            ziplist = zip([obj,], [obj.liked_by_user(request.user.id),])
            context['lists'] = ziplist
            return render(request, "blog/poetry.html", context)
    else:
        form = PostCreateForm()
    data = {
        'form':form
    }
    return render(request, 'blog/poetry_create.html', context=data)


# @login_required
# def poetry_update(request, post_id):
#     context ={} 
#     obj = get_object_or_404(POST, id=post_id)
#     form = PostCreateForm(request.POST or None, request.FILES, instance = obj)
#     if form.is_valid():
#         obj = form.save()
#         context['post'] = obj
#         return render(request, "blog/poetry_detail.html", context)
#     context["form"] = form
#     context["post_id"] = post_id
#     return render(request, "blog/poetry_update.html", context)
@login_required
def poetry_update(request, post_id):
    context ={} 
    obj = get_object_or_404(POST, id=post_id)
    form = PostCreateForm(instance = obj)
    if request.method=="POST":
        if obj.user == request.user:
            form = PostCreateForm(request.POST or None, request.FILES, instance = obj)
            if form.is_valid():
                obj = form.save()
                context['post'] = obj
                return render(request, "blog/post_detail.html", context)
        else:
            context['message'] = "invalid credentials"
    context["form"] = form
    context["post_id"] = post_id
    return render(request, "blog/poetry_update.html", context)


@login_required
def poetry_delete(request, post_id):
    context = {}
    obj = get_object_or_404(POST, id=post_id)
    if obj.user == request.user:
        obj.delete()
        context['message'] = "deleted"
    else:
        context['message'] = "invaled credentials"
    return JsonResponse(context)

@login_required
def poetry_like(request, post_id, not_read=True):
    context = {}
    post = POST.objects.get(id=post_id)
    if not_read:
        new_like, created = Like.objects.get_or_create(user=request.user, post_id=post_id)
        if created:
            new_like.save()
        else:
            new_like.delete()
    liked = post.liked_by_user(user_id=request.user.id)
    context['liked'] = liked
    context['likes'] = post.get_likes()
    context['comments'] = post.get_comments_count()
    return JsonResponse(context)


@login_required
def likes_comments(request, post_id):
    context = {}
    post = POST.objects.get(id=post_id)
    liked = post.liked_by_user(user_id=request.user.id)
    context['liked'] = liked
    context['likes'] = post.get_likes()
    context['comments'] = post.get_comments_count()
    return JsonResponse(context)


@login_required
def poetry_comment_create(request, post_id):
    context = {}
    post = POST.objects.get(id=post_id)
    # context['post'] = post
    if request.method == "POST":
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.post = post
            obj.save()
            context['comment'] = post.get_latest_comment()
            return render(request, 'blog/comment_detail.html', context)
    else:
        form = CommentForm()
    context['form'] = form
    return render(request, 'blog/comment.html', context)


@login_required
def poetry_comment_update(request, comment_id):
    context ={} 
    obj = get_object_or_404(Comment, id=comment_id)
    form = CommentForm(request.POST or None, instance = obj)
    if form.is_valid():
        obj = form.save().post
        context['post'] = obj
        return render(request, "blog/poetry_detail.html", context)
    context["form"] = form
    context["comment_id"] = comment_id
    return render(request, "blog/comment_update.html", context)


@login_required
def poetry_comment_delete(request, comment_id):
    context = {}
    comment = Comment.objects.get(id=comment_id)
    post = comment.post
    context['post']=post
    comment.delete()
    return render(request, 'blog/poetry_detail.html', context)

@login_required
def photography(request):
    return render(request, 'blog/photography.html')