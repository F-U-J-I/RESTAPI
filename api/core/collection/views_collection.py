from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response

from .models_collection import Profile, Collection, ProfileCollection
from .serializers_collection import DetailCollectionSerializer, CollectionSerializer, WindowDetailCollectionSerializer, \
    GradeCollectionSerializer, MiniCollectionSerializer
from ..course.models_course import ProfileCourseCollection
from ..utils import HelperFilter, HelperPaginatorValue, HelperPaginator


# #########################################
#        ######## GET ########
# #########################################


class CollectionView(viewsets.ModelViewSet):
    """VIEW. Коллекция"""
    lookup_field = 'slug'
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = HelperFilter.COLLECTION_FILTER_FIELDS
    search_fields = HelperFilter.COLLECTION_SEARCH_FIELDS
    ordering_fields = HelperFilter.COLLECTION_ORDERING_FIELDS

    pagination_max_page = HelperPaginatorValue.COLLECTION_MAX_PAGE

    def exists_course_path(self, path):
        """Существует ли такой путь к курсу"""
        return len(self.queryset.filter(path=path)) != 0

    @staticmethod
    def exists_profile_path(path):
        """Существует ли такой путь к профилю"""
        return len(Profile.objects.filter(path=path)) != 0

    def swap_filters_field(self, type_filter):
        """Смена типа фильтраций"""
        (self.filter_fields, self.search_fields, self.ordering_fields) = HelperFilter.get_filters_collection_field(
            type_filter)

    def get_frame_pagination(self, request, queryset, max_page=None):
        """Вернет каркас пагинации"""
        if max_page is None:
            max_page = self.pagination_max_page
        pagination = HelperPaginator(request=request, queryset=queryset, max_page=max_page)
        return {
            "count": pagination.get_count(),
            "pages": pagination.get_num_pages(),
            "next": pagination.get_link_next_page(),
            "previous": pagination.get_link_previous_page(),
            "results": pagination.page_obj
        }

    @action(detail=False, methods=['get'])
    def get_collections(self, request, *args, **kwargs):
        """GET. Вернет все подборки"""
        queryset = self.filter_queryset(self.queryset)
        frame_pagination = self.get_frame_pagination(request, queryset)

        auth = Profile.objects.get(user=self.request.user)
        serializer = CollectionSerializer(frame_pagination.get('results'), many=True, context={'profile': auth})

        frame_pagination['results'] = serializer.data
        return Response(frame_pagination, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_mini_collections(self, request, *args, **kwargs):
        """GET. Вернет все подборки в мини-формах"""
        auth = Profile.objects.get(user=self.request.user)
        queryset = self.filter_queryset(self.queryset)
        frame_pagination = self.get_frame_pagination(request, queryset, HelperPaginatorValue.MINI_COLLECTION_MAX_PAGE)
        serializer = MiniCollectionSerializer(frame_pagination.get('results'), many=True, context={'profile': auth})
        frame_pagination['results'] = serializer.data
        return Response(frame_pagination, status=status.HTTP_200_OK)

    @staticmethod
    def get_not_profile_collections(profile):
        """GET. Вернет все подборки, которые пользователь не добавлял себе и не создавал. Также не возвращает пустые"""
        data = dict()
        for item in ProfileCollection.objects.all():
            collection = item.collection
            if data.get(collection, None) is None:
                data[collection] = list()
            data[collection].append(item.profile)

        collection_list = list()
        queryset_course = ProfileCourseCollection.objects.all()
        for key, value in data.items():
            if (profile not in value) and (len(queryset_course.filter(collection=key)) != 0):
                collection_list.append(key)

        return ProfileCollection.objects.filter(collection__in=collection_list)

    @action(detail=False, methods=['get'])
    def get_catalog_collections(self, request, *args, **kwargs):
        """GET. Подборки которые неизвестны пользователю по path"""
        auth = Profile.objects.get(user=self.request.user)

        self.swap_filters_field(HelperFilter.PROFILE_COLLECTION_TYPE)
        queryset = self.filter_queryset(self.get_not_profile_collections(profile=auth))
        self.swap_filters_field(HelperFilter.COLLECTION_TYPE)

        frame_pagination = self.get_frame_pagination(request, queryset)
        serializer_list = list()
        for profile_collection in frame_pagination.get('results'):
            serializer_list.append(CollectionSerializer(profile_collection.collection, context={'profile': auth}).data)

        frame_pagination['results'] = serializer_list
        return Response(frame_pagination, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_all_profile_collections(self, request, path, *args, **kwargs):
        """GET. Добавленные и созданные подборки пользователем по path"""
        if not self.exists_profile_path(path):
            return Response({'error': "Такого пользователя не существует"}, status=status.HTTP_404_NOT_FOUND)
        profile = Profile.objects.get(path=path)
        auth = Profile.objects.get(user=self.request.user)

        self.swap_filters_field(HelperFilter.PROFILE_COLLECTION_TYPE)
        queryset = self.filter_queryset(ProfileCollection.objects.filter(profile=profile))
        self.swap_filters_field(HelperFilter.COLLECTION_TYPE)

        frame_pagination = self.get_frame_pagination(request, queryset, HelperPaginatorValue.MINI_COLLECTION_MAX_PAGE)
        serializer_list = list()
        for profile_collection in frame_pagination.get('results'):
            serializer_list.append(
                MiniCollectionSerializer(profile_collection.collection, context={'profile': auth}).data)

        frame_pagination['results'] = serializer_list
        return Response(frame_pagination, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_added_collections(self, request, path, *args, **kwargs):
        """GET. Добавленные подборки пользователем по path"""
        if not self.exists_profile_path(path):
            return Response({'error': "Такого пользователя не существует"}, status=status.HTTP_404_NOT_FOUND)
        profile = Profile.objects.get(path=path)
        auth = Profile.objects.get(user=self.request.user)

        self.swap_filters_field(HelperFilter.PROFILE_COLLECTION_TYPE)
        added_queryset = self.filter_queryset(ProfileCollection.objects.filter(profile=profile))
        self.swap_filters_field(HelperFilter.COLLECTION_TYPE)

        # Исключаем созданные подборки
        queryset = list()
        for item in added_queryset:
            if item.collection.profile != profile:
                queryset.append(item.collection)

        frame_pagination = self.get_frame_pagination(request, queryset, HelperPaginatorValue.MINI_COLLECTION_MAX_PAGE)
        serializer = MiniCollectionSerializer(frame_pagination.get('results'), many=True, context={'profile': auth})

        frame_pagination['results'] = serializer.data
        return Response(frame_pagination, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_created_collections(self, request, path, *args, **kwargs):
        """GET. Созданные подборки пользователем по path"""
        if not self.exists_profile_path(path):
            return Response({'error': "Такого пользователя не существует"}, status=status.HTTP_404_NOT_FOUND)

        profile = Profile.objects.get(path=path)
        auth = Profile.objects.get(user=self.request.user)

        queryset = self.filter_queryset(self.queryset.filter(profile=profile))
        frame_pagination = self.get_frame_pagination(request, queryset, HelperPaginatorValue.MINI_COLLECTION_MAX_PAGE)
        serializer = MiniCollectionSerializer(frame_pagination.get('results'), many=True, context={'profile': auth})
        frame_pagination['results'] = serializer.data
        return Response(frame_pagination, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_detail_collection(self, request, path=None, *args, **kwargs):
        """GET. Детальная страница подборки"""
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
    """VIEW. Действия над подборками"""
    lookup_field = 'slug'
    queryset = Collection.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def exists_path(self, path):
        """Существует ли такой путь"""
        return len(self.queryset.filter(path=path)) != 0

    @action(detail=False, methods=['post'])
    def create_collection(self, request):
        """POST. Создание подборки"""
        profile = Profile.objects.get(user=self.request.user)
        number_new_collection = len(ProfileCollection.objects.filter(profile=profile)) + 1
        serializer = WindowDetailCollectionSerializer(data={'title': f"Подборка #{number_new_collection}"},
                                                      context={'profile': profile})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'title': serializer.data['title'],
            'path': serializer.data['path'],
            'image_url': serializer.data['image_url'],
            "message": "Подборка успешно создана",
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_update_info(self, request, path=None, *args, **kwargs):
        """GET. Вернет информацию для обновления данных в подборке"""
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
        """PUT. Обновление информации о подборке"""
        if not self.exists_path(path):
            return Response({'error': "Такой подборки не существует"}, status=status.HTTP_404_NOT_FOUND)

        collection = self.queryset.get(path=path)
        profile = Profile.objects.get(user=request.user)
        if collection.profile != profile:
            return Response({"error": "У вас нет доступа для изменения подборки от имени этого аккаунта"},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = WindowDetailCollectionSerializer(data=request.data, instance=collection)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except ValueError as ex:
            return Response({'error': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def delete_collection(self, request, path):
        """DELETE. Удаление подборки"""
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
    """VIEW. Действия между профилем и подборками"""
    lookup_field = 'slug'
    queryset = Collection.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def exists_path(self, path):
        """Существует ли такой путь"""
        return len(self.queryset.filter(path=path)) != 0

    @action(detail=False, methods=['post'])
    def added_collections(self, request, path):
        """POST. Добавить подборку"""
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
        """DELETE. Удалить подборку из своей коллекции подборок"""
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
    """VIEW. Оценка подборки"""
    lookup_field = 'slug'
    queryset = Collection.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def exists_path(self, path):
        """Существует ли такой путь"""
        return len(self.queryset.filter(path=path)) != 0

    @action(detail=False, methods=['post'])
    def set_grade(self, request, path):
        """POST. Установить оценку"""
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
        """PUT. Обновление оценки"""
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
        """DELETE. Убрать оценку"""
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
