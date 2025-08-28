from flask import Blueprint, request, jsonify, session
from MCP_Service.utils.decorates import login_required
from MCP_Service.py_tools.schemas import tools
bp = Blueprint("tools", __name__, url_prefix="/tools")

# ---------------- 路由 ----------------
@bp.route("/get_tools_schemas", methods=["GET"])
@login_required
def get_tools_schemas():
    """返回所有工具的 schema 列表"""
    return jsonify({"tools_schemas": [t["schema"] for t in tools.values()]})


@bp.route("/call_tool", methods=["POST"])
@login_required
def call_tool():
    """
    通用工具调用接口
    请求: {"name": "read_file", "args": {"name": "example.txt"}}
    响应: {"content": "..."}
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON payload is required"}), 400

    name = data.get("name")
    args = data.get("args", {})

    if name not in tools:
        return jsonify({"error": f"Unknown tool: {name}"}), 400

    try:
        result = tools[name]["handler"](args)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"})
