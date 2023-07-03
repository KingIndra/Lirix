from django import forms
from .models import POST, Comment


class PostCreateForm(forms.ModelForm):
    class Meta:
        model = POST
        fields = ['content', 'picture']
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']