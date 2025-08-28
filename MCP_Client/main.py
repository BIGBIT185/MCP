import asyncio
import json
from typing import List, Dict, Any
import httpx
from openai import OpenAI
from MCP_Client.config import deep_seek_api_key

class ChatGptTool:
    def __init__(self):
        self.__openai_api_key_4_0_2 = deep_seek_api_key
        self.__tool_server_url = "http://localhost:5000"  # Flask 服务器地址

        # 一个全局 httpx.Client，会自动保存 Cookie（关键！）
        self.__http_client = httpx.AsyncClient()

        self.__client = OpenAI(
            api_key=self.__openai_api_key_4_0_2,
            base_url="https://api.deepseek.com",
        )
        self.__message: list[dict] = [
            {
                "role": "system",
                "content": (
                    "你是一名文件助手，可以帮助用户进行一些文件操作。"
                    "回答问题时尽量简短，减少函数调用次数，"
                    "已知的答案不要再进行函数调用。"
                ),
            }
        ]
        self.tools: List[Dict] = []  # 缓存工具定义

    async def login(self, username: str = "Alice") -> bool:
        """调用服务端登录接口，建立会话"""
        try:
            resp = await self.__http_client.post(
                f"{self.__tool_server_url}/auth/login",
                data={"username": username},
                follow_redirects=True,  # 避免 Flask 重定向丢失 Cookie
            )
            if resp.status_code == 200:
                print(f"登录成功，Cookie: {self.__http_client.cookies}")
                return True
            else:
                print(f"登录失败: {resp.status_code}, {resp.text}")
                return False
        except Exception as e:
            print(f"登录请求失败: {e}")
            return False

    async def refresh_tools(self) -> None:
        """主动刷新工具定义"""
        try:
            response = await self.__http_client.get(
                f"{self.__tool_server_url}/tools/get_tools_schemas"
            )
            if response.status_code == 200:
                self.tools = response.json().get("tools_schemas", [])
            else:
                print(f"获取工具失败: {response.status_code} {response.json().get('error')}")
                self.tools = []
        except Exception as e:
            print(f"连接工具服务器失败: {e}")
            self.tools = []

    async def call_remote_tool(self, func_name: str, args: Dict[str, Any]) -> Any:
        """调用远程工具（通过统一的 /call_tool 接口）"""
        try:
            response = await self.__http_client.post(
                f"{self.__tool_server_url}/tools/call_tool",
                json={"name": func_name, "args": args},
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"工具调用失败: {response.status_code} - {response.text}"}
        except Exception as e:
            return {"error": f"调用远程工具失败: {e}"}

    async def chat(self, user_input: str, max_iterations=5):
        # 如果工具列表还没有加载过，初始化时获取一次
        if not self.tools:
            await self.refresh_tools()
        if not self.tools:
            return "无法获取工具定义，请检查服务器是否运行"

        self.__message.append({"role": "user", "content": user_input})

        for _ in range(max_iterations):
            response = self.__client.chat.completions.create(
                model="deepseek-chat",
                messages=self.__message,
                tools=self.tools,
            )
            message = response.choices[0].message

            # 如果没有工具调用，返回最终结果
            if not hasattr(message, "tool_calls") or not message.tool_calls:
                self.__message.append({"role": "assistant", "content": message.content})
                return message.content

            # 处理工具调用
            self.__message.append({
                "role": "assistant",
                "content": "",
                "tool_calls": message.tool_calls,
            })

            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                # 调用远程工具（统一接口）
                result = await self.call_remote_tool(func_name, args)

                self.__message.append({
                    "role": "tool",
                    "content": str(result),
                    "tool_call_id": tool_call.id,
                })

        return "已达到最大处理轮数，请简化请求。"


if __name__ == "__main__":
    chat_tool = ChatGptTool()

    async def run():
        # 先登录（必须，否则没有 Cookie 会被拒绝）
        ok = await chat_tool.login(username="Alice")
        if not ok:
            return

        # 启动时就刷新工具定义，避免每次对话都请求
        await chat_tool.refresh_tools()
        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                break
            answer = await chat_tool.chat(user_input)
            print(f"AI: {answer}")

    asyncio.run(run())
