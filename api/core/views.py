from rest_framework import permissions, generics
from rest_framework.response import Response

from .serializers import RegisterSerializer, ProfileSerializer, UserSerializer
from .models import Profile


# Create your views here.
class RegisterView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'user': UserSerializer(user, context=self.get_serializer_context()).data,
            'message': "Пользователь успешно создан"
        })


class ProfileView(generics.GenericAPIView):
    lookup_field = 'slug'
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get(self, request, path):
        profile = Profile.objects.get(path=path)
        return Response({
            'profile': ProfileSerializer(profile, context=self.get_serializer_context()).data,
            'user': UserSerializer(profile.user, context=self.get_serializer_context()).data,
        })
