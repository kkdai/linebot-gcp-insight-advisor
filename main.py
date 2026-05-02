import os
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    AsyncApiClient,
    AsyncMessagingApi,
    ReplyMessageRequest,
    TextMessage as LineTextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from agent import insight_agent
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

app = FastAPI()

# 取得環境變數中的 LINE credentials
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "YOUR_LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "YOUR_LINE_CHANNEL_SECRET")

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
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

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):
    # 因為 WebhookHandler.handle 是同步的，我們使用 BackgroundTasks 或 asyncio.create_task 處理
    import asyncio
    asyncio.create_task(process_message_async(event))

async def process_message_async(event: MessageEvent):
    user_text = event.message.text
    user_id = event.source.user_id
    reply_token = event.reply_token

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
        reply_text = await get_adk_response()
    except Exception as e:
        reply_text = f"分析過程中發生錯誤：{str(e)}"
    
    async with AsyncApiClient(configuration) as api_client:
        line_bot_api = AsyncMessagingApi(api_client)
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[LineTextMessage(text=reply_text)]
            )
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
