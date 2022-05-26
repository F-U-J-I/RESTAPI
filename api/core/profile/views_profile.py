from rest_framework import permissions, generics
from rest_framework.response import Response

from .serializers_profile import ProfileSerializer, UserSerializer
from .models_profile import Profile


class ProfileView(generics.GenericAPIView):
    """Profile"""
    lookup_field = 'slug'
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get(self, request, path):
        profile = Profile.objects.get(path=path)
        return Response({
            'profile': ProfileSerializer(profile, context=self.get_serializer_context()).data,
            'user': UserSerializer(profile.user, context=self.get_serializer_context()).data,
        })
