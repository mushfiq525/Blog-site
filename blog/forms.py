from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content"]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = get_user_model()
        fields = ["username", "email", "password1", "password2"]

