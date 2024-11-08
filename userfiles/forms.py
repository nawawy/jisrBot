from django import forms
from .models import userfiles

class PostForm(forms.ModelForm):

    class Meta:
        model = userfiles
        fields = ["title", "file_data"]