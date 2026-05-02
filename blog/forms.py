from django import forms
from .models import Comment
from .models import Profile

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
        widgets = {
            'body': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your comment...'}),
        }
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'avatar', 'website', 'twitter', 'github']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell something about yourself...'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://...'}),
            'twitter': forms.TextInput(attrs={'placeholder': '@username'}),
            'github': forms.TextInput(attrs={'placeholder': 'github.com/username'}),
        }
class ProfileForm(forms.ModelForm):
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