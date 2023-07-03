from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.humanize.templatetags import humanize


class POST(models.Model):

    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='post_pics', default=None, null=True, blank=True)

    def get_date(self):
        str = humanize.naturaltime(self.date_posted)
        str = str.replace('an ','1 ')
        str = str.replace('a ','1 ')
        str = str.replace('seconds','s')
        str = str.replace('second','s')
        str = str.replace('minutes','m')
        str = str.replace('minute','m')
        str = str.replace('hours','h')
        str = str.replace('hour','h')
        str = str.replace('days','d')
        str = str.replace('day','d')
        str = str.replace('weeks','w')
        str = str.replace('week','w')
        str = str.replace('months','mo')
        str = str.replace('month','mo')
        str = str.replace('years','y')
        str = str.replace('year','y')
        a = 0
        b = -3
        for i,s in enumerate(str):
            if s==',':
                a = i
        if a!=0:
            str = str[:a]+" "+str[b:]
        str = "".join(str.split())
        str = str.replace('ago','')
        return str
    
    def get_likes(self):
        return self.like_set.all().count()
    
    def liked_by_user(self, user_id):
        return self.like_set.filter(user_id=user_id) and True or False
    
    def get_comments(self):
        return self.comment_set.all().order_by('-date_posted')
    
    def get_latest_comment(self):
        return self.comment_set.all().latest("date_posted")
    
    def get_comments_count(self):
        return self.comment_set.all().count()

    def __str__(self):
        return self.content
    

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(POST, on_delete=models.CASCADE)


class Comment(models.Model):
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    post = models.ForeignKey(POST, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_date(self):
        str = humanize.naturaltime(self.date_posted)
        str = str.replace('an ','1 ')
        str = str.replace('a ','1 ')
        str = str.replace('seconds','s')
        str = str.replace('second','s')
        str = str.replace('minutes','m')
        str = str.replace('minute','m')
        str = str.replace('hours','h')
        str = str.replace('hour','h')
        str = str.replace('days','d')
        str = str.replace('day','d')
        str = str.replace('weeks','w')
        str = str.replace('week','w')
        str = str.replace('months','mo')
        str = str.replace('month','mo')
        str = str.replace('years','y')
        str = str.replace('year','y')
        a = 0
        b = -3
        for i,s in enumerate(str):
            if s==',':
                a = i
        if a!=0:
            str = str[:a]+" "+str[b:]
        str = "".join(str.split())
        str = str.replace('ago','')
        return str
    

class LikeComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Comment, on_delete=models.CASCADE)

class Helper:

    def __init__(self, post :POST, like: Like, comment: Comment):
        self.post = post
        self.like = like
        self.comment = comment

    def posts_likedlist_by_user(self, user_id):
        likes = []
        for post in self.post.objects.all():
            likes.append(post.liked_by_user(user_id))
        return likes



helper = Helper(POST, Like, Comment)
        



# class PHOTO(models.Model):
#     title = models.CharField(max_length=100)
#     content = models.CharField(max_length=400)
#     image = models.ImageField()
#     dislikes = models.IntegerField(default=0)
#     date_posted = models.DateTimeField(default=timezone.now)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)









