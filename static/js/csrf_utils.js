// CSRF令牌处理工具

// 从cookie获取CSRF令牌
function getCsrfToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 'csrftoken='.length) === 'csrftoken=') {
                cookieValue = decodeURIComponent(cookie.substring('csrftoken='.length));
                break;
            }
        }
    }
    return cookieValue;
}

// 刷新页面上的CSRF令牌
function refreshCsrfToken() {
    const token = getCsrfToken();
    const elements = document.querySelectorAll('input[name="csrfmiddlewaretoken"]');
    elements.forEach(element => {
        element.value = token;
    });
    return token;
}

// 在表单提交前刷新CSRF令牌
function setupCsrfRefresh() {
    document.addEventListener('DOMContentLoaded', function() {
        // 初始刷新
        refreshCsrfToken();
        
        // 为所有表单添加提交前刷新逻辑
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function() {
                refreshCsrfToken();
            });
        });
    });
}

// 立即执行函数
setupCsrfRefresh();
