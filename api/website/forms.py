from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.schemas import coreapi


class SigUpForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': "fields-item-input",
            'id': "name",
            'name': 'name'
        }),
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': "fields-item-input",
            'id': "email",
            'name': 'email'
        })
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': "fields-item-input",
            'id': "password",
            'name': 'password'
        }),
    )
    repeat_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': "fields-item-input",
            'id': "repeat-password",
            'name': 'repeat-password'
        }),
    )

    def clean(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['repeat_password']

        if password != confirm_password:
            raise forms.ValidationError(
                "Пароли не совпадают"
            )

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
        )
        user.save()
        auth = authenticate(**self.cleaned_data)
        return auth


class LoginForm(forms.Form):

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': "fields-item-input",
            'id': "email",
            'name': 'email',
            'placeholder': "fuji@yandex.ru",
        })
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': "fields-item-input",
            'id': "password",
            'name': 'password',
            'placeholder': "Пароль",
        }),
    )
