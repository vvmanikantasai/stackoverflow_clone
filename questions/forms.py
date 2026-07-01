from django import forms
from .models import Question

class QuestionForm(forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'e.g. python django javascript',
                'id': 'id_tags_input',
            }
        ),
        help_text='Enter tags separated by spaces',
    )

    class Meta:
        model = Question
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'What is your question? Be specific.',
                'class': 'form-control question-title-input',
                'autocomplete': 'off',
            }),
            'content': forms.Textarea(attrs={
                'rows': 12,
                'placeholder': 'Describe your problem in detail. Include what you tried and what happened.',
                'id': 'question-editor', 'class': 'form-control'
            }),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 15:
            raise forms.ValidationError('Title must be at least 15 characters long.')
        return title

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) < 30:
            raise forms.ValidationError('Content must be at least 30 characters long.')
        return content

    def clean_tags_input(self):
        tags_input = self.cleaned_data.get('tags_input', '')
        tag_names = [t.strip().lower() for t in tags_input.split() if t.strip()]
        if len(tag_names) > 5:
            raise forms.ValidationError('You can add at most 5 tags.')
        return tag_names
