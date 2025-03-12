from django.utils.deprecation import MiddlewareMixin
from django.middleware.csrf import get_token

class CSRFRefreshMiddleware(MiddlewareMixin):
    """
    中间件确保每个响应都包含一个新的CSRF令牌
    """
    
    def process_response(self, request, response):
        # 为所有GET请求刷新CSRF令牌
        if request.method == 'GET':
            # 只是获取令牌，不需要做任何事情，因为Django会自动设置它
            get_token(request)
        return response
