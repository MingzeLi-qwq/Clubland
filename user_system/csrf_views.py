from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.middleware.csrf import REASON_NO_CSRF_COOKIE, REASON_NO_REFERER, REASON_BAD_TOKEN

def csrf_failure(request, reason=""):
    """
    自定义CSRF错误处理视图，用于改善用户体验
    - 对于AJAX请求，返回JSON错误
    - 对于普通请求，显示弹窗并重定向回上一页
    """
    # 获取更有意义的错误信息
    error_message = "CSRF验证失败。可能是您切换用户太快，请等待片刻再试。"
    
    # 判断是否为AJAX请求
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'error',
            'message': error_message
        }, status=403)
    
    # 对于普通请求，返回带有弹窗和返回上一页的脚本的响应
    response = HttpResponse("""
    <html>
    <head><title>CSRF验证失败</title></head>
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
