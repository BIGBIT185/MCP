from flask import Flask,jsonify
import argparse
from MCP_Service.others.config import flask_secret_api, flask_session_lifetime_minutes, flask_session_type
from datetime import timedelta
from flask_session import Session 
from MCP_Service.utils.ChatGPT_Utils import ChatGptTool
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

#初始化工具
tools=None
def init_chat_tools():
    from MCP_Service.py_tools.weather_tools import get_weather_handler
    from MCP_Service.py_tools.file_tools import list_file_handler,read_file_handler,write_file_handler
    from MCP_Service.py_tools.chatgpt_tools import chat_with_poet
    from MCP_Service.py_tools.schemas import tools_schema
    global tools
    tools = {
    "get_weather": {**tools_schema["get_weather"], "handler": get_weather_handler},
    "list_file": {**tools_schema["list_file"], "handler": list_file_handler},
    "read_file": {**tools_schema["read_file"], "handler": read_file_handler},
    "write_file": {**tools_schema["write_file"], "handler": write_file_handler},
    "chat_with_poet": {**tools_schema["chat_with_poet"], "handler": chat_with_poet},
    }
    chat_with_poet_tool=ChatGptTool("chat_with_poet",tools)
init_chat_tools()


def main():
    parser = argparse.ArgumentParser(description="File Manager Flask Server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", default=5000, type=int)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    get_base_dir().mkdir(exist_ok=True)

    register_blueprints(app)

    app.run(host=args.host, port=args.port, debug=True)


if __name__ == "__main__":
    main()