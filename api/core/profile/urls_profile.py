from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views_profile import ProfileView, SubscriptionProfileView, CourseProfileView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    path('profiles/', ProfileView.as_view({'get': 'get_list_profile'})),
    path('mini-profiles/', ProfileView.as_view({'get': 'get_list_mini_profile'})),
    path('profiles/<slug:path>/header/', ProfileView.as_view({'get': 'get_header_profile'})),

    path('profiles/<slug:path>/studying/courses/', CourseProfileView.as_view({'get': 'get_studying_courses'})),
    path('profiles/<slug:path>/studied/courses/', CourseProfileView.as_view({'get': 'get_studied_courses'})),
    path('profiles/<slug:path>/study-percent/', CourseProfileView.as_view({'get': 'get_statistic_study_courses'})),

    path('profiles/<slug:path>/goals-subscription/',
         SubscriptionProfileView.as_view({'get': 'get_goals_subscription_profile'})),
    path('profiles/<slug:path>/subscribers/', SubscriptionProfileView.as_view({'get': 'get_subscribers_profile'})),
    path('profiles/<slug:path>/create/subscription/',
         SubscriptionProfileView.as_view({'post': 'create_goal_subscription'})),
    path('profiles/<slug:path>/delete/subscription/',
         SubscriptionProfileView.as_view({'delete': 'delete_goal_subscription'})),

    # path('profile/<slug:path>/', ProfileView.as_view()),
]
