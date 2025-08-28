from flask import Flask,jsonify
import argparse
from MCP_Service.others.config import flask_secret_api, flask_session_lifetime_minutes, flask_session_type
from datetime import timedelta
from flask_session import Session 
from MCP_Service.py_tools.file_tools import get_base_dir
app = Flask(__name__)

# 设置 session 秘钥
app.secret_key = flask_secret_api
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=flask_session_lifetime_minutes)
app.config["SESSION_TYPE"] = flask_session_type
Session(app)

def register_blueprints(app):
    from MCP_Service.blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    from MCP_Service.blueprints.tools import bp as tools_bp
    app.register_blueprint(tools_bp)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="File Manager Flask Server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", default=5000, type=int)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    get_base_dir().mkdir(exist_ok=True)
    register_blueprints(app)
    app.run(host=args.host, port=args.port, debug=True)
