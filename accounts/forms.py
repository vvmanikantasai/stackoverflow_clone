from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
import re

from .models import Profile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Email address'}
        ),
    )
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Username'}
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Password'}
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Confirm password'}
        )
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise forms.ValidationError('Username can only contain letters, numbers, and underscores.')
        return username

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters.')
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[0-9]', password):
            raise forms.ValidationError('Password must contain at least one digit.')
        return password


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Username or Email'}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Password'}
        )
    )
    remember_me = forms.BooleanField(required=False)


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)

    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'website', 'github_url', 'x_url', 'location']
        labels = {
            'avatar': 'Profile image',
            'bio': 'About me',
            'x_url': 'X profile',
        }
        widgets = {
            'avatar': forms.ClearableFileInput(
                attrs={'accept': 'image/*'}
            ),
            'bio': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 8,
                    'placeholder': 'Tell the community about yourself. Markdown is supported.',
                    'id': 'profile-bio-editor',
                }
            ),
            'website': forms.URLInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'https://yourwebsite.com',
                }
            ),
            'github_url': forms.URLInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'https://github.com/username',
                }
            ),
            'x_url': forms.URLInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'https://x.com/username',
                }
            ),
            'location': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'City, Country'}
            ),
        }

    def clean_github_url(self):
        github_url = self.cleaned_data.get('github_url', '')
        if github_url and not github_url.lower().startswith(
            ('https://github.com/', 'http://github.com/')
        ):
            raise forms.ValidationError('Enter a valid github.com profile URL.')
        return github_url

    def clean_x_url(self):
        x_url = self.cleaned_data.get('x_url', '')
        if x_url and not x_url.lower().startswith(
            (
                'https://x.com/',
                'http://x.com/',
                'https://twitter.com/',
                'http://twitter.com/',
            )
        ):
            raise forms.ValidationError('Enter a valid x.com profile URL.')
        return x_url


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Current password'}
        )
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'New password'}
        )
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Confirm new password'}
        )
    )

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters.')
        return password

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password1')
        p2 = cleaned_data.get('new_password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data
