from MCP_Service.utils.ChatGPT_Utils import chatgpt_tool
from MCP_Service.utils.database import *
def chat_with_poet(user_content:str):
    """
    与诗人AI进行对话
    """
    try:
        username=session["username"]
        insert_history(username=username,agent="poet_prompt",content=user_content,role="user")#插入用户输入的内容
        messages=get_last_n_history(username,agent="poet_prompt",n=20)#获取最近n条历史记录
        ai_reply = chatgpt_tool.chat_with_history(messages)
        return {"ai_reply": ai_reply}
    except Exception as e:
        return {"error": str(e)}
