from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views_profile import ProfileView, SubscriptionProfileView, CourseProfileView, ActionProfileView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    # GET
    path('profile/', ProfileView.as_view({'get': 'get_profile_data'})),
    path('profiles/', ProfileView.as_view({'get': 'get_list_profile'})),
    path('mini-profiles/', ProfileView.as_view({'get': 'get_list_mini_profile'})),
    path('profiles/<slug:path>/header/', ProfileView.as_view({'get': 'get_header_profile'})),

    # PROFILE to COURSE
    path('profiles/<slug:path>/studying/courses/', CourseProfileView.as_view({'get': 'get_studying_courses'})),
    path('profiles/<slug:path>/studied/courses/', CourseProfileView.as_view({'get': 'get_studied_courses'})),
    path('profiles/<slug:path>/study-percent/', CourseProfileView.as_view({'get': 'get_statistic_study_courses'})),

    # SUBSCRIPTION
    path('profiles/<slug:path>/goals-subscription/',
         SubscriptionProfileView.as_view({'get': 'get_goals_subscription_profile'})),
    path('profiles/<slug:path>/subscribers/', SubscriptionProfileView.as_view({'get': 'get_subscribers_profile'})),
    path('profiles/<slug:path>/create/subscription/',
         SubscriptionProfileView.as_view({'post': 'create_goal_subscription'})),
    path('profiles/<slug:path>/delete/subscription/',
         SubscriptionProfileView.as_view({'delete': 'delete_goal_subscription'})),

    # path('profile/<slug:path>/', ProfileView.as_view()),

    # PROFILE UPDATE
    path('profiles/<slug:path>/get/info/', ActionProfileView.as_view({'get': 'get_info'})),
    path('profiles/<slug:path>/update/info/', ActionProfileView.as_view({'put': 'update_info'})),
    path('profiles/<slug:path>/update/password/', ActionProfileView.as_view({'put': 'update_password'})),
]
