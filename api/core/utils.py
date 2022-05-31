from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework import status
from rest_framework.utils.urls import replace_query_param
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse


class Util:
    PROFILE_COURSE_STATUS_SEE_NAME = 'Наблюдающий'
    PROFILE_COURSE_STATUS_STUDIED_NAME = 'Завершен'
    PROFILE_COURSE_STATUS_STUDYING_NAME = 'Изучается'

    PROFILE_COURSE_ROLE_ADMIN_NAME = 'Admin'
    PROFILE_COURSE_ROLE_USER_NAME = 'User'

    COURSE_STATUS_DEV_NAME = 'В разработке'
    COURSE_STATUS_RELEASE_NAME = 'Опубликован'

    PROTOCOL = 'http'

    @staticmethod
    def get_absolute_url(request, token=None, to=None):
        return f"{Util.PROTOCOL}://{get_current_site(request).domain}"

    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            to=[data['to_email']],
            from_email=data['from_email'],
        )
        email.send()

    @staticmethod
    def get_absolute_url_token(request, to, user):
        token = RefreshToken.for_user(user).access_token
        relative_link = reverse(to)
        return f"{Util.get_absolute_url(request)}{relative_link}?token={token}"

    @staticmethod
    def get_object_or_error(model, status_error=None, text=None, *args, **kwargs):
        try:
            return model.objects.get(*args, **kwargs)
        except Exception:
            raise ValueError(text, status_error)

class HelperFilter:
    # COLLECTION

    COLLECTION_TYPE = 1
    COLLECTION_FILTER_FIELDS = ('title', 'profile__user__username')
    COLLECTION_SEARCH_FIELDS = ('title', 'profile__user__username')
    COLLECTION_ORDERING_FIELDS = ('rating', 'title')

    PROFILE_COLLECTION_TYPE = 2
    PROFILE_COLLECTION_FILTER_FIELDS = ('collection__title', 'collection__profile__user__username')
    PROFILE_COLLECTION_SEARCH_FIELDS = ('collection__title', 'collection__profile__user__username')
    PROFILE_COLLECTION_ORDERING_FIELDS = ('collection__rating', 'collection__title')

    # COURSE

    COURSE_TYPE = 3
    COURSE_FILTER_FIELDS = ('title', 'profile__user__username')
    COURSE_SEARCH_FIELDS = ('title', 'profile__user__username')
    COURSE_ORDERING_FIELDS = ('rating', 'title')

    PROFILE_COURSE_TYPE = 4
    PROFILE_COURSE_FILTER_FIELDS = ('course__title', 'course__profile__user__username')
    PROFILE_COURSE_SEARCH_FIELDS = ('course__title', 'course__profile__user__username')
    PROFILE_COURSE_ORDERING_FIELDS = ('course__rating', 'course__title')

    @staticmethod
    def get_filters_collection_field(type_filter):
        if type_filter == HelperFilter.COLLECTION_TYPE:
            filter_fields = HelperFilter.COLLECTION_FILTER_FIELDS
            search_fields = HelperFilter.COLLECTION_SEARCH_FIELDS
            ordering_fields = HelperFilter.COLLECTION_ORDERING_FIELDS
            return filter_fields, search_fields, ordering_fields
        elif type_filter == HelperFilter.PROFILE_COLLECTION_TYPE:
            filter_fields = HelperFilter.PROFILE_COLLECTION_FILTER_FIELDS
            search_fields = HelperFilter.PROFILE_COLLECTION_SEARCH_FIELDS
            ordering_fields = HelperFilter.PROFILE_COLLECTION_ORDERING_FIELDS
            return filter_fields, search_fields, ordering_fields

    @staticmethod
    def get_filters_course_field(type_filter):
        if type_filter == HelperFilter.COURSE_TYPE:
            filter_fields = HelperFilter.COURSE_FILTER_FIELDS
            search_fields = HelperFilter.COURSE_SEARCH_FIELDS
            ordering_fields = HelperFilter.COURSE_ORDERING_FIELDS
            return filter_fields, search_fields, ordering_fields
        elif type_filter == HelperFilter.PROFILE_COURSE_TYPE:
            filter_fields = HelperFilter.PROFILE_COURSE_FILTER_FIELDS
            search_fields = HelperFilter.PROFILE_COURSE_SEARCH_FIELDS
            ordering_fields = HelperFilter.PROFILE_COURSE_ORDERING_FIELDS
            return filter_fields, search_fields, ordering_fields


class HelperPaginatorValue:
    COLLECTION_MAX_PAGE = 10
    MINI_COLLECTION_PAGE = 40

    COURSE_MAX_PAGE = 20
    MINI_COURSE_PAGE = 40

    PAGE_QUERY_PARAM = 'page'


class HelperPaginator:

    def __init__(self, request, queryset, max_page):
        self.paginator = Paginator(queryset, max_page)
        self.link = request.build_absolute_uri()
        self.current_page_num = self.get_current_page_num(request=request)
        self.page_obj = self.get_page()

    @staticmethod
    def get_current_page_num(request):
        return request.GET.get('page', 1)

    def get_page(self):
        """Вернет страницу"""
        try:
            return self.paginator.page(self.current_page_num)
        except PageNotAnInteger:
            return self.paginator.page(1)
        except EmptyPage:
            return self.paginator.page(self.paginator.num_pages)

    def get_num_pages(self):
        """Вернет количество страниц"""
        return self.paginator.num_pages

    def get_count(self):
        """Количество записей"""
        return self.paginator.count

    def get_link_next_page(self):
        """Следующая страница"""
        if not self.page_obj.has_next():
            return None

        page_number = self.page_obj.next_page_number()
        return replace_query_param(self.link, HelperPaginatorValue.PAGE_QUERY_PARAM, page_number)

    def get_link_previous_page(self):
        """Предыдущая страница"""
        if not self.page_obj.has_previous():
            return None

        page_number = self.page_obj.previous_page_number()
        return replace_query_param(self.link, HelperPaginatorValue.PAGE_QUERY_PARAM, page_number)
