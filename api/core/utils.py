import os

from django.contrib.sites.shortcuts import get_current_site
from django.core.files.images import ImageFile
# from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse
from rest_framework.utils.urls import replace_query_param
from rest_framework_simplejwt.tokens import RefreshToken


class Util:
    PROFILE_COURSE_STATUS_SEE_NAME = 'Наблюдающий'
    PROFILE_COURSE_STATUS_STUDIED_NAME = 'Завершен'
    PROFILE_COURSE_STATUS_STUDYING_NAME = 'Изучается'

    PROFILE_COURSE_ROLE_ADMIN_NAME = 'Admin'
    PROFILE_COURSE_ROLE_USER_NAME = 'User'

    COURSE_STATUS_DEV_NAME = 'В разработке'
    COURSE_STATUS_RELEASE_NAME = 'Опубликован'

    DEFAULT_IMAGES = {
        'profile': "!default-profile.jpg",
        'collection': "!default-collection.png",
        'course': "!default-course.png",
        'theme': "!default-theme.png",
        'lesson': "!default-lesson.png",
    }

    PROTOCOL = 'http'

    @staticmethod
    def get_absolute_url(request):
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
        # send_mail(
        #     subject=data['email_subject'],
        #     message=data['email_body'],
        #     from_email=data['from_email'],
        #     recipient_list=[data['to_email']],
        #     fail_silently=False,
        # )

    @staticmethod
    def get_absolute_url_token(request, to, user):
        token = RefreshToken.for_user(user).access_token
        relative_link = reverse(to)
        return f"{Util.get_absolute_url(request)}{relative_link}?token={token}"

    @staticmethod
    def exists_path(model, validated_data):
        return len(model.objects.filter(**validated_data)) != 0

    @staticmethod
    def get_image(old, new, default):
        try:
            if new is None or len(new) == 0:
                path_image = "\\".join(old.path.split('\\')[:-1]) + "\\" + str(default)
                new = ImageFile(open(path_image, "rb"))
        except FileNotFoundError:
            path_image = "\\".join(old.path.split('\\')[:-1]) + "\\" + str(default)
            new = ImageFile(open(path_image, "rb"))
        return new

    @staticmethod
    def get_update_image(old, new):
        if old.path != new.name:
            try:
                if (old is not None) and (old.name not in Util.DEFAULT_IMAGES.values()):
                    os.remove(old.path)
            except ValueError:
                pass
            return new
        return old

    @staticmethod
    def get_update_path(new_path):
        return "-".join(new_path.split())

    @staticmethod
    def get_new_path(new_path, old_path, model):
        if new_path is not None:
            if len(new_path) == 0:
                raise ValueError("path не может быть пустым")
            all_path = model.objects.filter(path=new_path)
            if (len(all_path) == 0) or (len(all_path) == 1 and new_path == old_path):
                return new_path
            else:
                raise ValueError("Такой path уже существует")
        return old_path

    @staticmethod
    def get_max_path(queryset):
        max_path = 0
        for item in queryset:
            if (type(item.path) == int) and (item.path > max_path):
                max_path = item.path
        return max_path


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

    # PROFILE

    PROFILE_TYPE = 5
    PROFILE_FILTER_FIELDS = ('path', 'user__username')
    PROFILE_SEARCH_FIELDS = ('path', 'user__username')
    PROFILE_ORDERING_FIELDS = ('path', 'user__username')

    # GOAL Subscription

    GOAL_TYPE = 6
    GOAL_FILTER_FIELDS = ('goal__path', 'goal__user__username')
    GOAL_SEARCH_FIELDS = ('goal__path', 'goal__user__username')
    GOAL_ORDERING_FIELDS = ('goal__path', 'goal__user__username')

    # SUBSCRIBER

    SUBSCRIBER_TYPE = 7
    SUBSCRIBER_FILTER_FIELDS = ('subscriber__path', 'subscriber__user__username')
    SUBSCRIBER_SEARCH_FIELDS = ('subscriber__path', 'subscriber__user__username')
    SUBSCRIBER_ORDERING_FIELDS = ('subscriber__path', 'subscriber__user__username')

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

    @staticmethod
    def get_filters_profile_field(type_filter):
        if type_filter == HelperFilter.PROFILE_TYPE:
            filter_fields = HelperFilter.PROFILE_FILTER_FIELDS
            search_fields = HelperFilter.PROFILE_SEARCH_FIELDS
            ordering_fields = HelperFilter.PROFILE_ORDERING_FIELDS
            return filter_fields, search_fields, ordering_fields

    @staticmethod
    def get_filters_subscription_field(type_filter):
        if type_filter == HelperFilter.GOAL_TYPE:
            filter_fields = HelperFilter.GOAL_FILTER_FIELDS
            search_fields = HelperFilter.GOAL_SEARCH_FIELDS
            ordering_fields = HelperFilter.GOAL_ORDERING_FIELDS
            return filter_fields, search_fields, ordering_fields
        elif type_filter == HelperFilter.SUBSCRIBER_TYPE:
            filter_fields = HelperFilter.SUBSCRIBER_FILTER_FIELDS
            search_fields = HelperFilter.SUBSCRIBER_SEARCH_FIELDS
            ordering_fields = HelperFilter.SUBSCRIBER_ORDERING_FIELDS
            return filter_fields, search_fields, ordering_fields


class HelperPaginatorValue:
    COLLECTION_MAX_PAGE = 10
    MINI_COLLECTION_MAX_PAGE = 40

    COURSE_MAX_PAGE = 20
    MINI_COURSE_MAX_PAGE = 40

    PROFILE_MAX_PAGE = 20
    MINI_PROFILE_MAX_PAGE = 40

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
