import os
import sys
from pathlib import Path

if __name__ == "__main__":
    # 将项目根目录添加到模块搜索路径
    os.environ["NO_PROXY"] = "*"  # 禁用所有代理
    os.environ["HTTP_PROXY"] = ""
    os.environ["HTTPS_PROXY"] = ""
    sys.path.insert(0, str(Path(__file__).parent))
    os.system('python3 -m MCP_Client.main')  # 关键变化：使用模块方式运行

