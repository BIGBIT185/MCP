from flask import Blueprint
from flask import request
from flask import session
from MCP_Service.utils.database import *
bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/login", methods=["POST"])
def login():
    try:
        username = request.form.get("username")
        password = request.form.get("password")

        if not has_user(name) :
            return jsonify({"error": "用户不存在，请先注册。"}), 401  # 状态码400表示请求有误
        elif not is_legal_user(name,password):
            return jsonify({"error": "用户名或密码错误，请重新输入。"}), 400
        # 登录成功
        session["username"] = username
        session.permanent = True
        return jsonify({"message": f"欢迎 {username}"}), 200
    except Exception as e:
        return jsonify({"error": "登录失败: {str(e)}"}), 500



# 注册接口
@bp.route("/register", methods=["POST"])
def register():
    try:
        username = request.form.get("username")
        password = request.form.get("password")
        if has_user(username):
            return jsonify({"error": "用户已存在，请直接登录。"}), 400
        insert_user(username, password)
        return jsonify({"message": f"用户 {username} 注册成功，请登录。"}), 200
    except Exception as e:
        return jsonify({"error": f"注册失败: {str(e)}"}), 500



# 登出接口
@bp.route("/logout")
def logout():
    session.clear()   # 清除 session
    return "已登出"

