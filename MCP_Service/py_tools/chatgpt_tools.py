from MCP_Service.utils.ChatGPT_Utils import chat_with_poet_tool
from MCP_Service.utils.database import *
from flask import session
def chat_with_poet(user_content:str):
    """
    与诗人AI进行对话
    """
    try:
        username=session["username"]
        databasetool.insert_history(username=username,agent="poet_prompt",content=user_content,role="user")#插入用户输入的内容
        messages=databasetool.get_last_n_history(username,agent="poet_prompt",n=20)#获取最近n条历史记录
        ai_reply = chat_with_poet_tool.chat(messages)
        return {"ai_reply": ai_reply}
    except Exception as e:
        return {"error": str(e)}
