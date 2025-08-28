from pathlib import Path

base_dir = Path("./test")  # 确保路径正确

def list_file() -> list[str]:
    print("Listing files")
    file_list = []
    for item in base_dir.glob("*"):  # 使用 glob 方法
        if item.is_file():
            file_list.append(str(item.relative_to(base_dir)))
    return file_list

def read_file(name):
    print(f"Reading file: {name}")
    try:
        with open(base_dir / name, "r") as file:
            return file.read()
    except Exception as e:
        return f"An error occurred: {e}"

Tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather of an location, the user shoud supply a location first",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g. San Francisco, CA",
                            }
                        },
                        "required": ["location"]
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read the content of a specified file. Returns the content as a string or an error message if failed.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The name or relative path of the file, e.g., 'example.txt'."
                            }
                        },
                        "required": ["name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_file",
                    "description": "List all files in the current directory. Returns a list of file names.",
                    "parameters": {
                        "type": "object",
                        "properties": {}  # 无参数
                    }
                }
            }
        ]