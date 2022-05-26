from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import serializers_collection as serializers
from .models_collection import Profile, Collection, ProfileCollection


class CollectionView(viewsets.ModelViewSet):
    """Коллекция"""
    lookup_field = 'slug'
    queryset = Collection.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def exists_path(self, path):
        return len(self.queryset.filter(path=path)) != 0

    def list(self, request, *args, **kwargs):
        serializer_collection_list = list()
        profile = Profile.objects.get(user=self.request.user)
        for collection in self.queryset:
            serializer_collection_list.append(
                serializers.CollectionSerializer(collection, context={'profile': profile}).data)
        return Response(serializer_collection_list)

    @action(detail=False, methods=['get'])
    def list_mini_collection(self, request, *args, **kwargs):
        serializer_collection_list = list()
        profile = Profile.objects.get(user=self.request.user)
        for collection in self.queryset:
            serializer_collection_list.append(
                serializers.CollectionSerializer(collection, context={'profile': profile}).data)
        return Response(serializer_collection_list)

    def get(self, request, path=None, *args, **kwargs):
        if not self.exists_path(path):
            return Response({'error': "Такой подборки не существует"}, status=status.HTTP_404_NOT_FOUND)

        collection = self.queryset.get(path=path)
        profile = Profile.objects.get(user=request.user)
        serializer = serializers.DetailCollectionSerializer(collection, context={'profile': profile})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def create_collection(self, request):
        profile = Profile.objects.get(user=self.request.user)
        number_new_collection = len(ProfileCollection.objects.filter(profile=profile)) + 1
        serializer = serializers.WindowDetailCollectionSerializer(data={'title': f"Подборка #{number_new_collection}"},
                                                                  context={'profile': profile})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'title': serializer.data['title'],
            'path': serializer.data['path']
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def get_update_info(self, request, path=None, *args, **kwargs):
        if not self.exists_path(path):
            return Response({'error': "Такой подборки не существует"}, status=status.HTTP_404_NOT_FOUND)
        collection = self.queryset.get(path=path)
        profile = Profile.objects.get(user=request.user)
        if collection.profile != profile:
            return Response({"error": "У вас нет доступа для изменения коллекции"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializers.WindowDetailCollectionSerializer(collection).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'])
    def update_info(self, request, path=None, *args, **kwargs):
        if not self.exists_path(path):
            return Response({'error': "Такой подборки не существует"}, status=status.HTTP_404_NOT_FOUND)

        collection = self.queryset.get(path=path)
        profile = Profile.objects.get(user=request.user)
        if collection.profile != profile:
            return Response({"error": "У вас нет доступа для изменения подборки от имени этого аккаунта"},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = serializers.WindowDetailCollectionSerializer(data=request.data, instance=collection)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def delete_collection(self, request, path):
        if not self.exists_path(path):
            return Response({'error': "Такой подборки не существует"}, status=status.HTTP_404_NOT_FOUND)

        collection = self.queryset.get(path=path)
        profile = Profile.objects.get(user=request.user)
        if collection.profile != profile:
            return Response({"error": "У вас нет доступа для удаления подборки от имени этого аккаунта"},
                            status=status.HTTP_400_BAD_REQUEST)

        collection_title = collection.title
        collection.delete()
        return Response({
            "title": collection_title,
            "path": path
        }, status=status.HTTP_200_OK)
