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
        help_texts = {
            "text": "Напишите тут текст вашего поста",
            "group": "Выберите группу"
        }

    def clean_text(self):
        data = self.cleaned_data["text"]
        if data == "":
            raise forms.ValidationError("Текст поста должен быть заполнен")
        return data
