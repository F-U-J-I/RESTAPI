from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_collection import CollectionView, GradeCollectionView, ActionCollectionView, ActionProfileCollectionView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    path('collections/', CollectionView.as_view({'get': 'get_collections'})),
    path('mini-collections/', CollectionView.as_view({'get': 'get_mini_collections'}), name="mini-collections"),
    path('collections/catalog/', CollectionView.as_view({'get': 'get_catalog_collections'})),
    path('collections/all/<slug:path>/', CollectionView.as_view({'get': 'get_all_profile_collections'})),
    path('collections/added/<slug:path>/', CollectionView.as_view({'get': 'get_added_collections'})),
    path('collections/created/<slug:path>/', CollectionView.as_view({'get': 'get_created_collections'})),
    path('collections/get/<slug:path>/', CollectionView.as_view({'get': 'get_detail_collection'})),

    path('collections/create/grade/<slug:path>/', GradeCollectionView.as_view({'post': 'set_grade'})),
    path('collections/update/grade/<slug:path>/', GradeCollectionView.as_view({'put': 'update_grade'})),
    path('collections/delete/grade/<slug:path>/', GradeCollectionView.as_view({'delete': 'delete_grade'})),

    path('collections/create/', ActionCollectionView.as_view({'post': 'create_collection'})),
    path('collections/get-update/<slug:path>/', ActionCollectionView.as_view({'get': 'get_update_info'})),
    path('collections/update/<slug:path>/', ActionCollectionView.as_view({'put': 'update_info'})),
    path('collections/delete/<slug:path>/', ActionCollectionView.as_view({'delete': 'delete_collection'})),

    path('collections/add/<slug:path>/', ActionProfileCollectionView.as_view({'post': 'added_collections'})),
    path('collections/pop/<slug:path>/', ActionProfileCollectionView.as_view({'delete': 'popped_collections'})),
]
