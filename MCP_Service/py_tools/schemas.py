# ---------------- 工具注册表 ----------------
tools_schema = {
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
        }
    },
    "list_file": {
        "schema": {
            "type": "function",
            "function": {
                "name": "list_file",
                "description": "List all files in the base directory.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        }
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
        }
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
        }
    },
    "chat_with_poet": {
        "schema": {
            "type": "function",
            "function": {
                "name": "chat_with_poet",
                "description": "与诗人AI进行对话，基于历史会话生成诗意的回答。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_content": {
                            "type": "string",
                            "description": "用户输入的文本，例如一个问题、主题或提示语。"
                        }
                    },
                    "required": ["user_content"],
                },
            },
        }
    }
}
tools_schema2=[t["schema"] for t in tools_schema.values()]