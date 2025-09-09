from MCP_Service.utils.database import *
from flask import session
from typing import Callable, Dict, Any

def chat_with_poet(args: Dict[str, Any]):
    """
    与诗人AI进行对话
    """
    try:
        username=session["username"]
        user_content = args.get('user_content')
        if not user_content:
            return ValueError("Missing 'user_content' parameter")
        print(user_content)
        databasetool.insert_history(user_name=username,agent_name="poet_prompt",content=user_content,role="user")#插入用户输入的内容
        messages=databasetool.get_last_n_history(user_name=username,agent_name="poet_prompt",n=20)#获取最近n条历史记录
        from MCP_Service.main import chat_with_poet_tool
        ai_reply = chat_with_poet_tool.chat(messages)
        print(1111)
        return {"ai_reply": ai_reply}
    except Exception as e:
        print(f"chat_with_poet错误: {str(e)}")
        return {"error": str(e)}
