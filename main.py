import os
from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from agent import insight_agent
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

app = FastAPI()

# 取得環境變數中的 LINE credentials
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "YOUR_LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "YOUR_LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 初始化 ADK 組件
adk_app = App(name="GCP_Advisor_App", root_agent=insight_agent)
session_service = InMemorySessionService()

@app.get("/")
def root():
    return {"message": "GCP Insight Advisor Bot is running."}

@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    body_str = body.decode("utf-8")
    
    try:
        handler.handle(body_str, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature.")
    
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    import asyncio
    user_text = event.message.text
    user_id = event.source.user_id
    # LINE webhook 是同步呼叫，我們需要建立一個新的事件迴圈來跑非同步的 ADK
    
    async def get_adk_response():
        reply_parts = []
        async with Runner(app=adk_app, session_service=session_service) as runner:
            # 確保 Session 存在
            await session_service.create_session(app_name="GCP_Advisor_App", user_id=user_id, session_id=user_id)
            
            new_msg = types.Content(role="user", parts=[types.Part(text=user_text)])
            async for adk_event in runner.run_async(user_id=user_id, session_id=user_id, new_message=new_msg):
                if adk_event.content and adk_event.content.parts:
                    for part in adk_event.content.parts:
                        if part.text:
                            reply_parts.append(part.text)
        return "".join(reply_parts) if reply_parts else "Agent 沒有返回任何內容。"

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        reply_text = loop.run_until_complete(get_adk_response())
        loop.close()
    except Exception as e:
        reply_text = f"分析過程中發生錯誤：{str(e)}"
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
