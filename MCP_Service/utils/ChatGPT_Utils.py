import json
from openai import OpenAI
from MCP_Service.others.config import deep_seek_api_key,chat_model
from MCP_Service.others.prompts import prompts
from MCP_Service.py_tools.schemas import tools
from MCP_Service.utils.database import *
from flask import session
class ChatGptTool:
    def __init__(self,scenario):
        self.__client = OpenAI(
            api_key=deep_seek_api_key,
            base_url="https://api.deepseek.com",
        )
        self.model = chat_model  # DeepSeek的模型名称
        self.system_prompt=[]
        self.scenario=scenario
        self.load_system_message(scenario)

    def load_system_message(self,scenario):
        """
        加载系统消息
        """
        self.system_prompt.append(prompts[scenario])
    
    # def chat_with_history(self, messages):
    #     """
    #     与AI进行对话,带有历史记录
    #     """
    #     try:
    #         messages=self.system_prompt+messages
    #         response = self.__client.chat.completions.create(
    #             model=self.model,
    #             messages=messages,
    #             stream=False
    #         )
    #         ai_reply=response.choices[0].message.content
    #         return ai_reply
    #     except Exception as e:
    #         return f"错误: {str(e)}"
    
    def chat(self, messages):
        """
        与AI进行对话
        """
        try:
            username=session.get("username")
            
            mytools=tools
            mytools.pop(self.scenario,None)
            total_messages = self.system_prompt + messages
            for _ in range(5):
                response = self.__client.chat.completions.create(
                    model=self.model,
                    messages=total_messages,
                    tools=tools,
                )
                message = response.choices[0].message

                # 如果没有工具调用，返回最终结果
                if not hasattr(message, "tool_calls") or not message.tool_calls:
                    databasetool.insert_history(username=username, agent=self.scenario, content=message.content,role="assistant")
                    return message.content
                databasetool.insert_history(username=username, agent=self.scenario,tool_calls=message.tool_calls,role="assistant")
                total_messages.append({
                    "role": "assistant",
                    "content": "",
                    "tool_calls": message.tool_calls,
                })
                for tool_call in message.tool_calls:
                    func_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)

                    # 调用远程工具（统一接口）
                    # 调用本地工具
                    result=None
                    # 查找本地工具
                    tool = tools.get(func_name)
                    if tool:
                        handler = tool["handler"]
                        try:
                            # 支持异步/同步 handler
                            result =  handler(**args)
                        except Exception as e:
                            result = {"error": str(e)}
                    else:
                        result = {"error": f"Tool {func_name} not found"}
                    databasetool.insert_history(username=username, agent=self.scenario,content=str(result),tool_call_id=tool_call.id,role="tool")
                    total_messages.append({
                        "role": "tool",
                        "content": str(result),
                        "tool_call_id": tool_call.id,
                    })
            return "已达到最大处理轮数，请简化请求。"
        except Exception as e:
            return f"错误: {str(e)}"

chat_with_poet_tool=ChatGptTool("chat_with_poet")

