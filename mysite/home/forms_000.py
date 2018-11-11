from django import forms

class PostForm(forms.Form):
    author = forms.CharField(max_length=32)
    title = forms.CharField(max_length=200)
    content = forms.TextField(max_length=1000)
    isNsfw = forms.BooleanField()
    isSpoiler = forms.BooleanField()
