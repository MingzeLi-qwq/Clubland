from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.middleware.csrf import REASON_NO_CSRF_COOKIE, REASON_NO_REFERER, REASON_BAD_TOKEN

def csrf_failure(request, reason=""):
    """
    Custom CSRF failure handler to improve user experience
    - For AJAX requests, returns a JSON error
    - For regular requests, shows an alert and redirects back
    """
    # Provide a more meaningful error message
    error_message = "CSRF verification failed. This may happen if you switched users too quickly. Please wait a moment and try again."
    
    # Check if it is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'error',
            'message': error_message
        }, status=403)
    
    # For regular requests, return an HTML response with a popup and back navigation
    response = HttpResponse("""
    <html>
    <head><title>CSRF Verification Failed</title></head>
    <body>
        <script>
            alert("{}");
            history.back();
        </script>
    </body>
    </html>
    """.format(error_message))
    
    response.status_code = 403
    return response
