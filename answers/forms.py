from django import forms
from .models import Answer


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 10,
                'placeholder': 'Write your answer here. Be detailed and helpful.',
                'id': 'answer-editor'
            }),
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) < 20:
            raise forms.ValidationError('Answer must be at least 20 characters long.')
        return content
