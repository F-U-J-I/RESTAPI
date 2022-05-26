from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_collection import CollectionView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    path('collections/', CollectionView.as_view({'get': 'list'})),
    path('mini-collections/', CollectionView.as_view({'get': 'list_mini_collection'}), name="mini-collections"),
    path('collections/<slug:path>/', CollectionView.as_view({'get': 'get'})),
    path('create/collection/', CollectionView.as_view({'post': 'create_collection'})),
    path('get-update/collections/<slug:path>/', CollectionView.as_view({'get': 'get_update_info'})),
    path('update/collections/<slug:path>/', CollectionView.as_view({'put': 'update_info'})),
    path('delete/collections/<slug:path>/', CollectionView.as_view({'delete': 'delete_collection'})),
]
