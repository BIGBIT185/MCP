from MCP_Service.py_tools.weather_tools import *
from MCP_Service.py_tools.file_tools import *
# ---------------- 工具注册表 ----------------
tools: Dict[str, Dict[str, Any]] = {
    "get_weather": {
        "schema": {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the weather of the day for a specific location.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location name (e.g., Beijing, Shanghai, or London)"
                        }
                    },
                    "required": ["location"]
                },
            },
        },
        "handler": get_weather_handler,
    },
    "list_file": {
        "schema": {
            "type": "function",
            "function": {
                "name": "list_file",
                "description": "List all files in the base directory.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        "handler": list_file_handler,
    },
    "read_file": {
        "schema": {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read the content of a specified file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "The file name or relative path."}
                    },
                    "required": ["name"],
                },
            },
        },
        "handler": read_file_handler,
    },
    "write_file": {
        "schema": {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write content to a specified file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "The file name or relative path."},
                        "content": {"type": "string", "description": "The content to write."},
                    },
                    "required": ["name", "content"],
                },
            },
        },
        "handler": write_file_handler,
    },
}