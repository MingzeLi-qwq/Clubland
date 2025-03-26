from django.utils.deprecation import MiddlewareMixin
from django.middleware.csrf import get_token

class CSRFRefreshMiddleware(MiddlewareMixin):
    """
    Middleware to ensure every response includes a refreshed CSRF token
    """
    
    def process_response(self, request, response):
        # Refresh the CSRF token for all GET requests and POST requests followed by a redirect
        if request.method == 'GET' or (request.method == 'POST' and response.status_code == 302):
            get_token(request)
        return response
