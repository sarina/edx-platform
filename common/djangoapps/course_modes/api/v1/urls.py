from django.conf import settings
from django.conf.urls import url

from course_modes.api.v1 import views


app_name = 'v1'

urlpatterns = [
    url(
        r'^courses/{course_id}/$'.format(course_id=settings.COURSE_ID_PATTERN),
        views.CourseModesView.as_view(),
        name='course_modes'
    ),
    url(
        r'^courses/{course_id}/(?P<mode_slug>.*)$'.format(course_id=settings.COURSE_ID_PATTERN),
        views.CourseModesDetailView.as_view(),
        name='course_modes_detail'
    ),
]
