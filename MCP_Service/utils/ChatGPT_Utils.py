import json
from openai import OpenAI
from MCP_Service.others.config import deep_seek_api_key,chat_model
from MCP_Service.others.prompts import prompts
class ChatGptTool:
    def __init__(self):
        self.__client = OpenAI(
            api_key=deep_seek_api_key,
            base_url="https://api.deepseek.com",
        )
        self.model = chat_model  # DeepSeek的模型名称
        self.system_prompt=[]
        self.load_system_message()

    def load_system_message(self,):
        """
        加载系统消息
        """
        self.system_prompt.append(prompts["poet_prompt"])
    
    def chat_with_history(self, messages):
        """
        与AI进行对话,带有历史记录
        """
        try:
            messages=self.system_prompt+messages
            response = self.__client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False
            )
            ai_reply=response.choices[0].message.content
            return ai_reply
        except Exception as e:
            return f"错误: {str(e)}"
    
    def chat(self, message):
        """
        与AI进行对话
        """
        try:
            response = self.__client.chat.completions.create(
                model=self.model,
                messages=[
                    prompts["poet_prompt"],
                    {"role": "user", "content": message},
                    ],
                stream=False
            )
            ai_reply=response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": ai_reply})
            return ai_reply
        except Exception as e:
            return f"错误: {str(e)}"

chatgpt_tool = ChatGptTool()