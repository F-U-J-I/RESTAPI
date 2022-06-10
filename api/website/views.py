from django.shortcuts import render
from django.views import View


class SignUpView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'website/signup.html')
        # tests = Test.objects.all()
        # return render(request, 'moon_test_app/home.html', context={
        #     'tests': tests
        # })
