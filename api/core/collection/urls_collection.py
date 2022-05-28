from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_collection import CollectionView, GradeCollectionView, ActionCollectionView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    path('collections/', CollectionView.as_view({'get': 'list'})),
    path('mini-collections/', CollectionView.as_view({'get': 'list_mini_collection'}), name="mini-collections"),
    path('added-collections/', CollectionView.as_view({'get': 'get_added_collections'})),
    path('collections/<slug:path>/', CollectionView.as_view({'get': 'get'})),

    path('collections/create/grade/<slug:path>/', GradeCollectionView.as_view({'post': 'set_grade'})),
    path('collections/update/grade/<slug:path>/', GradeCollectionView.as_view({'put': 'update_grade'})),
    path('collections/delete/grade/<slug:path>/', GradeCollectionView.as_view({'delete': 'delete_grade'})),

    path('create/collection/', ActionCollectionView.as_view({'post': 'create_collection'})),
    path('get-update/collections/<slug:path>/', ActionCollectionView.as_view({'get': 'get_update_info'})),
    path('update/collections/<slug:path>/', ActionCollectionView.as_view({'put': 'update_info'})),
    path('delete/collections/<slug:path>/', ActionCollectionView.as_view({'delete': 'delete_collection'})),
]
