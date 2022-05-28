from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers_collection import DetailCollectionSerializer, CollectionSerializer, WindowDetailCollectionSerializer, \
    GradeCollectionSerializer
from .models_collection import Profile, Collection, ProfileCollection


# #########################################
#        ######## GET ########
# #########################################

class CollectionView(viewsets.ModelViewSet):
    """Коллекция"""
    lookup_field = 'slug'
    queryset = Collection.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def exists_course_path(self, path):
        return len(self.queryset.filter(path=path)) != 0

    @staticmethod
    def exists_profile_path(path):
        return len(Profile.objects.filter(path=path)) != 0

    def list(self, request, *args, **kwargs):
        serializer_collection_list = list()
        auth = Profile.objects.get(user=self.request.user)
        for collection in self.queryset:
            serializer_collection_list.append(
                CollectionSerializer(collection, context={'profile': auth}).data)
        return Response(serializer_collection_list)

    @action(detail=False, methods=['get'])
    def list_mini_collection(self, request, *args, **kwargs):
        serializer_collection_list = list()
        auth = Profile.objects.get(user=self.request.user)
        for collection in self.queryset:
            serializer_collection_list.append(
                CollectionSerializer(collection, context={'profile': auth}).data)
        return Response(serializer_collection_list)

    @action(detail=False, methods=['get'])
    def get_added_collections(self, request, path, *args, **kwargs):
        """Добавленные подборки пользователем по path"""
        if not self.exists_profile_path(path):
            return Response({'error': "Такого пользователя не существует"}, status=status.HTTP_404_NOT_FOUND)

        serializer_collection_list = list()
        profile = Profile.objects.get(path=path)
        auth = Profile.objects.get(user=self.request.user)
        for profile_collection in ProfileCollection.objects.filter(profile=profile):
            serializer_collection_list.append(
                CollectionSerializer(profile_collection.collection, context={'profile': auth}).data)
        return Response(serializer_collection_list)

    @action(detail=False, methods=['get'])
    def get_created_collections(self, request, path, *args, **kwargs):
        """Созданные подборки пользователем по path"""
        print(path)
        if not self.exists_profile_path(path):
            return Response({'error': "Такого пользователя не существует"}, status=status.HTTP_404_NOT_FOUND)

        serializer_collection_list = list()
        profile = Profile.objects.get(path=path)
        auth = Profile.objects.get(user=self.request.user)
        for collection in self.queryset.filter(profile=profile):
            serializer_collection_list.append(
                CollectionSerializer(collection, context={'profile': auth}).data)
        return Response(serializer_collection_list)

    @action(detail=False, methods=['get'])
    def get_detail_collection(self, request, path=None, *args, **kwargs):
        """Детальная страница подборки"""
        if not self.exists_course_path(path):
            return Response({'error': "Такой подборки не существует"}, status=status.HTTP_404_NOT_FOUND)

        collection = self.queryset.get(path=path)
        auth = Profile.objects.get(user=request.user)
        serializer = DetailCollectionSerializer(collection, context={'profile': auth})
        return Response(serializer.data, status=status.HTTP_200_OK)


# #########################################
#        ######## ACTIONS ########
# #########################################

class ActionCollectionView(viewsets.ModelViewSet):
    """Коллекция"""
    lookup_field = 'slug'
    queryset = Collection.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def exists_path(self, path):
        return len(self.queryset.filter(path=path)) != 0

    @action(detail=False, methods=['post'])
    def create_collection(self, request):
        profile = Profile.objects.get(user=self.request.user)
        number_new_collection = len(ProfileCollection.objects.filter(profile=profile)) + 1
        serializer = WindowDetailCollectionSerializer(data={'title': f"Подборка #{number_new_collection}"},
                                                      context={'profile': profile})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'title': serializer.data['title'],
            'path': serializer.data['path'],
            "message": "Подборка успешно создалась",
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_update_info(self, request, path=None, *args, **kwargs):
        if not self.exists_path(path):
            return Response({'error': "Такой подборки не существует"}, status=status.HTTP_404_NOT_FOUND)
        collection = self.queryset.get(path=path)
        profile = Profile.objects.get(user=request.user)
        if collection.profile != profile:
            return Response({"error": "У вас нет доступа для изменения коллекции"},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(WindowDetailCollectionSerializer(collection).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'])
    def update_info(self, request, path=None, *args, **kwargs):
        if not self.exists_path(path):
            return Response({'error': "Такой подборки не существует"}, status=status.HTTP_404_NOT_FOUND)

        collection = self.queryset.get(path=path)
        profile = Profile.objects.get(user=request.user)
        if collection.profile != profile:
            return Response({"error": "У вас нет доступа для изменения подборки от имени этого аккаунта"},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = WindowDetailCollectionSerializer(data=request.data, instance=collection)
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
            "path": path,
            "message": "Подборка успешно удалилась",
        }, status=status.HTTP_200_OK)


# #########################################
#    ######## ACTIONS PROFILE ########
# #########################################

class ActionProfileCollectionView(viewsets.ModelViewSet):
    """Коллекция"""
    lookup_field = 'slug'
    queryset = Collection.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def exists_path(self, path):
        return len(self.queryset.filter(path=path)) != 0

    @action(detail=False, methods=['post'])
    def added_collections(self, request, path):
        if not self.exists_path(path):
            return Response({'error': "Такой подборки не существует"}, status=status.HTTP_404_NOT_FOUND)

        profile = Profile.objects.get(user=self.request.user)
        collection = Collection.objects.get(path=path)
        profile_collection_list = ProfileCollection.objects.filter(profile=profile, collection=collection)
        if len(profile_collection_list) != 0:
            return Response({'error': "Вы уже добавили эту подборку"}, status=status.HTTP_404_NOT_FOUND)

        profile_collection = ProfileCollection.objects.create(profile=profile, collection=collection)
        profile_collection.save()

        return Response({
            'collection': collection.title,
            'message': "Подборка добавлена"
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def popped_collections(self, request, path):
        if not self.exists_path(path):
            return Response({'error': "Такой подборки не существует"}, status=status.HTTP_404_NOT_FOUND)

        profile = Profile.objects.get(user=self.request.user)
        collection = Collection.objects.get(path=path)
        profile_collection_list = ProfileCollection.objects.filter(profile=profile, collection=collection)
        if len(profile_collection_list) == 0:
            return Response({'error': "Вы уже удалили эту подборку"}, status=status.HTTP_404_NOT_FOUND)

        profile_collection = profile_collection_list[0]
        profile_collection.delete()

        return Response({
            'collection': collection.title,
            'message': "Подборка удалена"
        }, status=status.HTTP_200_OK)


# #########################################
#        ######## GRADE ########
# #########################################

class GradeCollectionView(viewsets.ModelViewSet):
    """Коллекция"""
    lookup_field = 'slug'
    queryset = Collection.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def exists_path(self, path):
        return len(self.queryset.filter(path=path)) != 0

    @action(detail=False, methods=['post'])
    def set_grade(self, request, path):
        if not self.exists_path(path):
            return Response({'error': "Такой подборки не существует"}, status=status.HTTP_404_NOT_FOUND)

        collection = self.queryset.get(path=path)
        profile = Profile.objects.get(user=self.request.user)
        serializer = GradeCollectionSerializer(data=request.data,
                                               context={'profile': profile, 'collection': collection})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'collection': collection.title,
            'path': collection.path,
            'grade': serializer.data['grade']
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'])
    def update_grade(self, request, path):
        if not self.exists_path(path):
            return Response({'error': "Такой подборки не существует"}, status=status.HTTP_404_NOT_FOUND)

        collection = self.queryset.get(path=path)
        profile = Profile.objects.get(user=self.request.user)
        profile_collection = ProfileCollection.objects.get(profile=profile, collection=collection)

        serializer = GradeCollectionSerializer(data=request.data, instance=profile_collection)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'collection': collection.title,
            'path': collection.path,
            'grade': serializer.data['grade']
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def delete_grade(self, request, path):
        if not self.exists_path(path):
            return Response({'error': "Такой подборки не существует"}, status=status.HTTP_404_NOT_FOUND)

        collection = self.queryset.get(path=path)
        profile = Profile.objects.get(user=self.request.user)

        if collection.profile != profile:
            return Response({"error": "У вас нет доступа для удаления оценки у подборки от имени этого аккаунта"},
                            status=status.HTTP_400_BAD_REQUEST)

        profile_collection = ProfileCollection.objects.get(profile=profile, collection=collection)
        serializer = GradeCollectionSerializer(context={'profile_collection': profile_collection})
        serializer.delete_grade()

        return Response({
            'collection': collection.title,
            'path': collection.path,
            'grade': serializer.data['grade']
        }, status=status.HTTP_200_OK)
