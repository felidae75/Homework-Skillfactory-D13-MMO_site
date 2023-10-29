from ckeditor.widgets import CKEditorWidget
from django.forms import ModelForm
from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import *


# Создаём модельную форму
class CreatePostForm(ModelForm):
    class Meta:
        model = Post
        widgets = {'title': forms.TextInput(attrs={'size': '100'})}
        fields = ('category', 'title', 'text',)

    def __init__(self, *args, **kwargs):
        super(CreatePostForm, self).__init__(*args, **kwargs)
        self.fields['category'].label = "Category:"
        self.fields['title'].label = "Title"
        self.fields['text'].label = "If you need text...:"
