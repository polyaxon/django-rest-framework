import copy

import django
import pytest
from django.test import TestCase

from rest_framework import status
from rest_framework.compat import async_to_sync
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.settings import APISettings, api_settings
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

factory = APIRequestFactory()

JSON_ERROR = 'JSON parse error - Expecting value:'


class BasicView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'method': 'GET'})

    def post(self, request, *args, **kwargs):
        return Response({'method': 'POST', 'data': request.data})


class BasicAsyncView(APIView):
    async def get(self, request, *args, **kwargs):
        return Response({'method': 'GET'})

    async def post(self, request, *args, **kwargs):
        return Response({'method': 'POST', 'data': request.data})


@api_view(['GET', 'POST', 'PUT', 'PATCH'])
def basic_view(request):
    if request.method == 'GET':
        return Response({'method': 'GET'})
    elif request.method == 'POST':
        return Response({'method': 'POST', 'data': request.data})
    elif request.method == 'PUT':
        return Response({'method': 'PUT', 'data': request.data})
    elif request.method == 'PATCH':
        return Response({'method': 'PATCH', 'data': request.data})


@api_view(['GET', 'POST', 'PUT', 'PATCH'])
async def basic_async_view(request):
    if request.method == 'GET':
        return Response({'method': 'GET'})
    elif request.method == 'POST':
        return Response({'method': 'POST', 'data': request.data})
    elif request.method == 'PUT':
        return Response({'method': 'PUT', 'data': request.data})
    elif request.method == 'PATCH':
        return Response({'method': 'PATCH', 'data': request.data})


class ErrorView(APIView):
    def get(self, request, *args, **kwargs):
        raise Exception


def custom_handler(exc, context):
    if isinstance(exc, SyntaxError):
        return Response({'error': 'SyntaxError'}, status=400)
    return Response({'error': 'UnknownError'}, status=500)


class OverridenSettingsView(APIView):
    settings = APISettings({'EXCEPTION_HANDLER': custom_handler})

    def get(self, request, *args, **kwargs):
        raise SyntaxError('request is invalid syntax')


@api_view(['GET'])
def error_view(request):
    raise Exception


def sanitise_json_error(error_dict):
    """
    Exact contents of JSON error messages depend on the installed version
    of json.
    """
    ret = copy.copy(error_dict)
    chop = len(JSON_ERROR)
    ret['detail'] = ret['detail'][:chop]
    return ret


class ClassBasedViewIntegrationTests(TestCase):
    def setUp(self):
        self.view = BasicView.as_view()

    def test_get_succeeds(self):
        request = factory.get('/')
        response = self.view(request)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {'method': 'GET'}

    def test_post_succeeds(self):
        request = factory.post('/', {'test': 'foo'})
        response = self.view(request)
        expected = {
            'method': 'POST',
            'data': {'test': ['foo']}
        }
        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected

    def test_400_parse_error(self):
        request = factory.post('/', 'f00bar', content_type='application/json')
        response = self.view(request)
        expected = {
            'detail': JSON_ERROR
        }
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert sanitise_json_error(response.data) == expected


class FunctionBasedViewIntegrationTests(TestCase):
    def setUp(self):
        self.view = basic_view

    def test_get_succeeds(self):
        request = factory.get('/')
        response = self.view(request)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {'method': 'GET'}

    def test_post_succeeds(self):
        request = factory.post('/', {'test': 'foo'})
        response = self.view(request)
        expected = {
            'method': 'POST',
            'data': {'test': ['foo']}
        }
        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected

    def test_400_parse_error(self):
        request = factory.post('/', 'f00bar', content_type='application/json')
        response = self.view(request)
        expected = {
            'detail': JSON_ERROR
        }
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert sanitise_json_error(response.data) == expected


@pytest.mark.skipif(
    django.VERSION < (4, 1),
    reason="Async view support requires Django 4.1 or higher",
)
class ClassBasedAsyncViewIntegrationTests(TestCase):
    def setUp(self):
        self.view = BasicAsyncView.as_view()

    def test_get_succeeds(self):
        request = factory.get('/')
        response = async_to_sync(self.view)(request)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {'method': 'GET'}

    def test_post_succeeds(self):
        request = factory.post('/', {'test': 'foo'})
        response = async_to_sync(self.view)(request)
        expected = {
            'method': 'POST',
            'data': {'test': ['foo']}
        }
        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected

    def test_400_parse_error(self):
        request = factory.post('/', 'f00bar', content_type='application/json')
        response = async_to_sync(self.view)(request)
        expected = {
            'detail': JSON_ERROR
        }
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert sanitise_json_error(response.data) == expected


@pytest.mark.skipif(
    django.VERSION < (4, 1),
    reason="Async view support requires Django 4.1 or higher",
)
class FunctionBasedAsyncViewIntegrationTests(TestCase):
    def setUp(self):
        self.view = basic_async_view

    def test_get_succeeds(self):
        request = factory.get('/')
        response = async_to_sync(self.view)(request)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {'method': 'GET'}

    def test_post_succeeds(self):
        request = factory.post('/', {'test': 'foo'})
        response = async_to_sync(self.view)(request)
        expected = {
            'method': 'POST',
            'data': {'test': ['foo']}
        }
        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected

    def test_400_parse_error(self):
        request = factory.post('/', 'f00bar', content_type='application/json')
        response = async_to_sync(self.view)(request)
        expected = {
            'detail': JSON_ERROR
        }
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert sanitise_json_error(response.data) == expected


class TestCustomExceptionHandler(TestCase):
    def setUp(self):
        self.DEFAULT_HANDLER = api_settings.EXCEPTION_HANDLER

        def exception_handler(exc, request):
            return Response('Error!', status=status.HTTP_400_BAD_REQUEST)

        api_settings.EXCEPTION_HANDLER = exception_handler

    def tearDown(self):
        api_settings.EXCEPTION_HANDLER = self.DEFAULT_HANDLER

    def test_class_based_view_exception_handler(self):
        view = ErrorView.as_view()

        request = factory.get('/', content_type='application/json')
        response = view(request)
        expected = 'Error!'
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == expected

    def test_function_based_view_exception_handler(self):
        view = error_view

        request = factory.get('/', content_type='application/json')
        response = view(request)
        expected = 'Error!'
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == expected


class TestCustomSettings(TestCase):
    def setUp(self):
        self.view = OverridenSettingsView.as_view()

    def test_get_exception_handler(self):
        request = factory.get('/', content_type='application/json')
        response = self.view(request)
        assert response.status_code == 400
        assert response.data == {'error': 'SyntaxError'}
