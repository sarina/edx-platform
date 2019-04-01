from django.conf.urls import include, url


app_name = 'common.djangoapps.course_modes.api'

urlpatterns = [
    url(r'^v1/', include('course_modes.api.v1.urls', namespace='v1')),
]
