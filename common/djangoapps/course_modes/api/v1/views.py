"""
Defines the "ReSTful" API for course modes.
"""

import logging

from django.http import Http404
from django.shortcuts import get_object_or_404
from edx_rest_framework_extensions import permissions
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from edx_rest_framework_extensions.auth.session.authentication import SessionAuthenticationAllowInactiveUser
from opaque_keys.edx.keys import CourseKey
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from openedx.core.lib.api.authentication import OAuth2AuthenticationAllowInactiveUser
from openedx.core.lib.api.parsers import MergePatchParser

from course_modes.api.serializers import CourseModeSerializer
from course_modes.models import CourseMode

log = logging.getLogger(__name__)


class CourseModesMixin(object):
    authentication_classes = (
        JwtAuthentication,
        OAuth2AuthenticationAllowInactiveUser,
        SessionAuthenticationAllowInactiveUser,
    )
    permission_classes = (permissions.JWT_RESTRICTED_APPLICATION_OR_USER_ACCESS,)
    serializer_class = CourseModeSerializer
    pagination_class = None
    lookup_field = 'course_id'
    queryset = CourseMode.objects.all()


class CourseModesView(CourseModesMixin, ListCreateAPIView):
    """
    View to list and create course modes for a course.
    """
    pass


class CourseModesDetailView(CourseModesMixin, RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update, or delete a specific course mode for a course.

    If "application/merge-patch+json" is not the specified content type, a 415 "Unsupported Media Type" response is returned.
    """
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']
    parser_classes = (MergePatchParser,)
    multiple_lookup_fields = ('course_id', 'mode_slug')

    def get_object(self):
        queryset = self.get_queryset()
        query_filter = {}
        for field in self.multiple_lookup_fields:
            query_filter[field] = self.kwargs[field]

        query_filter['course_id'] = CourseKey.from_string(query_filter['course_id'])

        obj = get_object_or_404(queryset, **query_filter)
        self.check_object_permissions(self.request, obj)
        return obj

    def patch(self, request, *args, **kwargs):
        """
        Performs a partial update of a CourseMode instance.
        """
        course_mode = self.get_object()
        serializer = self.serializer_class(course_mode, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()  # can also raise ValidationError
            return Response(
                status=status.HTTP_204_NO_CONTENT,
                content_type='application/json',
            )
