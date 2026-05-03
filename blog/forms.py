from django import forms
from django.contrib.auth.models import User
from .models import Comment, Profile

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
        widgets = {
            'body': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your comment...'}),
        }

class UserForm(forms.ModelForm):
    """Form to edit user's account info (username, name, email)"""
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class ProfileForm(forms.ModelForm):
    """Form to edit profile fields (bio, location, avatar, etc.)"""
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'gender', 'avatar', 'website', 'twitter', 'github']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell something about yourself...'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://...'}),
            'twitter': forms.TextInput(attrs={'placeholder': '@username'}),
            'github': forms.TextInput(attrs={'placeholder': 'github.com/username'}),
            'gender': forms.Select(choices=Profile.GENDER_CHOICES),
        }