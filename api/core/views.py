from rest_framework.response import Response
from rest_framework import permissions, generics

from .serializers import RegisterSerializer, ProfileSerializer


# Create your views here.
class RegisterView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        return Response({
            'profile': ProfileSerializer(profile, context=self.get_serializer_context()).data,
            'message': "Пользователь успешно создан"
        })