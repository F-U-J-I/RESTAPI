import urllib

import requests
import urllib3
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from rest_framework.schemas.coreapi import coreapi
from rest_framework_simplejwt.tokens import RefreshToken

from .forms import SigUpForm, LoginForm


class SignUpView(View):
    def get(self, request, *args, **kwargs):
        form = SigUpForm()
        # client = coreapi.Client()
        # data = client.get('http://dmakger.beget.tech/api/collections/get/1/')
        # print(data)
        # response = request.get('http://dmakger.beget.tech/api/collections/get/1/')
        # print(response.content)
        return render(request, 'website/signup.html', context={
            'form': form,
        })

    def post(self, request, *args, **kwargs):
        form = SigUpForm(request.POST)
        if form.is_valid():
            print(form)
            client = coreapi.Client()
            request.get('http://dmakger.beget.tech/api/collections/get/1/')

            data = client.post('http://dmakger.beget.tech/api/register/')
            # user = form.save()
            # if user is not None:
            #     login(request, user)
            #     return HttpResponseRedirect('/')
        return render(request, 'myblog/signup.html', context={
            'form': form,
        })


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, 'website/login.html', context={
            'form': form,
        })

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            data = {
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password'],
            }
            print(data)
            # result = urllib3.connection_from_url('http://example.com', urllib.urlencode(data))
            # print(result)
            # content = result.read()
            # print(content)
            response = requests.post('http://localhost:8000/api/token/', data=data)
            print(type(response.text), response.text)
            content = response.content
            print(type(content), content)
            print(type(response.json()), response.json())
            login()
            return HttpResponseRedirect('/')


class MainView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'website/index.html')
