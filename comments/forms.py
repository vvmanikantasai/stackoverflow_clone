from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Add a comment... (max 500 characters)',
                'maxlength': 500,
                'class': 'comment-input'
            }),
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) > 500:
            raise forms.ValidationError('Comment cannot exceed 500 characters.')
        if len(content) < 5:
            raise forms.ValidationError('Comment must be at least 5 characters.')
        return content
