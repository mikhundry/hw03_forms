from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group")
        labels = {
            "text": "Текст поста",
            "group": "Группа"
        }


def clean_text(self):
    data = self.cleaned_data["text"]
    if data == "":
        raise forms.ValidationError("Текст поста должен быть заполнен")
    return data
