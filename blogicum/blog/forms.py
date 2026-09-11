from django import forms
from django.core.exceptions import ValidationError

from .models import Comment, Post
from .moderation import is_toxic

MODERATION_ERROR = (
    'Комментарий не проходит модерацию.'
    'Пожалуйста, сформулируйте мысль корректнее.'
)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title',
            'text',
            'pub_date',
            'location',
            'category',
            'image',
        ]
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                },
                format='%Y-%m-%dT%H:%M'
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):

        text = self.cleaned_data.get('text')
        if not text:
            return text
        is_bad = is_toxic(text)
        if is_bad:
            raise ValidationError(MODERATION_ERROR)
        return text
