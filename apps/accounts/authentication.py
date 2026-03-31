from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings


class LSLAPIKeyAuthentication(BaseAuthentication):
    """
    Custom authentication for LSL objects using API key in header.
    Objects send X-API-Key header to authenticate.
    """

    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY', '')
        if not api_key:
            return None

        if api_key != settings.LSL_API_KEY:
            raise AuthenticationFailed('Invalid API key.')

        # Return None user but truthy auth — marks request as authenticated
        return (None, 'lsl-api-key')

    def authenticate_header(self, request):
        return 'X-API-Key'