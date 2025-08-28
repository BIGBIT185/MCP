from typing import Callable, Dict, Any
from pathlib import Path

def get_base_dir():
    return Path("files_test/")

def list_file_handler(_: Dict[str, Any]):
    base_dir = get_base_dir()
    files = [str(item.relative_to(base_dir)) for item in base_dir.glob("*") if item.is_file()]
    return {"files": files}


def read_file_handler(args: Dict[str, Any]):
    name = args.get("name")
    if not name:
        return {"error": "File name parameter 'name' is required"}
    try:
        with open(get_base_dir() / name, "r", encoding="utf-8") as f:
            return {"content": f.read()}
    except Exception as e:
        return {"error": str(e)}


def write_file_handler(args: Dict[str, Any]):
    name = args.get("name")
    content = args.get("content")
    if not name:
        return {"error": "File name parameter 'name' is required"}
    if content is None:
        return {"error": "Content parameter 'content' is required"}
    try:
        with open(get_base_dir() / name, "w", encoding="utf-8") as f:
            f.write(content)
        return {"message": f"Successfully wrote to {name}"}
    except Exception as e:
        return {"error": str(e)}

