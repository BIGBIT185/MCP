from flask import Blueprint
from flask import request
from flask import session
bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/login", methods=["POST"])
def login():
    user = request.form["username"]
    session["user"] = user
    session.permanent = True
    return f"欢迎 {user}"

# 登出接口
@bp.route("/logout")
def logout():
    session.clear()   # 清除 session
    return "已登出"

