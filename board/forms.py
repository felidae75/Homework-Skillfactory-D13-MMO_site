from django.forms import ModelForm
from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import *


# Создаём модельную форму
class CreatePostForm(ModelForm):
    text = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = Post
        widgets = {'title': forms.TextInput(attrs={'size': '95'})}
        fields = ('category', 'title', 'text',)

    def __init__(self, *args, **kwargs):
        super(CreatePostForm, self).__init__(*args, **kwargs)
        self.fields['category'].label = "Category:"
        self.fields['title'].label = "Title"
        self.fields['text'].label = "If you need text...:"


class CommentForm(forms.ModelForm):
    class Meta:
        model = CommentPost
        fields = ('text',)

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['text'].label = "Do you want comment?"


class CommentFilterForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(CommentFilterForm, self).__init__(*args, **kwargs)
        self.fields['title'] = forms.ModelChoiceField(
            label='Advert',
            queryset=Post.objects.filter(user=user).order_by('-dateCreation').values_list('title', flat=True),
            empty_label="All",
            required=False
        )


class EditProfile(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class AuthCodeForm(forms.Form):
    code = forms.IntegerField(label="Code")


