from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers_profile import ProfileSerializer, UserSerializer, MiniProfileSerializer
from .models_profile import Profile


class ProfileView(viewsets.ModelViewSet):
    """Profile"""
    lookup_field = 'slug'
    queryset = Profile.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def exists_path(self, path):
        return len(self.queryset.filter(path=path)) != 0

    @action(methods=['get'], detail=False)
    def get_list_profile(self, request):
        serializer_profile_list = list()
        auth = Profile.objects.get(user=self.request.user)
        for profile in self.queryset:
            serializer_profile_list.append(ProfileSerializer(profile, context={'auth': auth}).data)
        return Response(serializer_profile_list, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_list_mini_profile(self, request):
        serializer_profile_list = list()
        for profile in self.queryset:
            serializer_profile_list.append(MiniProfileSerializer(profile).data)
        return Response(serializer_profile_list, status=status.HTTP_200_OK)
