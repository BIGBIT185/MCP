import os
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    os.system('python3 -m MCP_Service.main')  # 关键变化：使用模块方式运行

