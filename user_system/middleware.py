from django.utils.deprecation import MiddlewareMixin
from django.middleware.csrf import get_token

class CSRFRefreshMiddleware(MiddlewareMixin):
    """
    中间件确保每个响应都包含一个新的CSRF令牌
    """
    
    def process_response(self, request, response):
        # 所有GET请求和提交表单后的重定向请求刷新CSRF令牌
        if request.method == 'GET' or (request.method == 'POST' and response.status_code == 302):
            get_token(request)
        return response
