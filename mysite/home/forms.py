from django import forms

class PostForm(forms.Form):
    title = forms.CharField(max_length=200)
    content = forms.CharField(max_length=1000)
