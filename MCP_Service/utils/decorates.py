from flask import session
from flask import jsonify 
def login_required(func):
    """简单的登录验证装饰器"""
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if "username" not in session:  # 检查是否已登录
            return jsonify({"error": "Unauthorized, please login first"}), 401
        return func(*args, **kwargs)
    return wrapper