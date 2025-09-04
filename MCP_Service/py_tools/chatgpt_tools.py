from MCP_Service.utils.ChatGPT_Utils import chatgpt_tool
def chat_with_poet(user_content:str):
    """
    与诗人AI进行对话
    """
    try:
        username=session["username"]
        messages=get_last_n_history(username,n=20)+[{"role":"user","content":user_content}]#获取最近n条历史记录
        ai_reply = chatgpt_tool.chat_with_history(messages)
        messages.append({"role": "assistant", "content": ai_reply})
        insert_history(username,None,text,is_ai)
    except Exception as e:
        return {"error": str(e)}
