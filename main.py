import os
from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from agent import insight_agent

app = FastAPI()

# 取得環境變數中的 LINE credentials
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "YOUR_LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "YOUR_LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.get("/")
def root():
    return {"message": "GCP Insight Advisor Bot is running."}

@app.post("/callback")
async def callback(request: Request):
    # 獲取 LINE 簽名
    signature = request.headers.get("X-Line-Signature", "")
    
    # 獲取 request 內文
    body = await request.body()
    body_str = body.decode("utf-8")
    
    # 驗證簽章並處理訊息
    try:
        handler.handle(body_str, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature. Please check your channel access token/channel secret.")
    
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    
    # 調用 ADK Agent 進行推理與回覆 (若使用最新版的 google-adk，請參閱其 API 文件，這是一個基礎呼叫範例)
    try:
        # 這裡的寫法視 ADK 最終提供的介面而定，通常 agent.query() 或 app.query()
        # 這裡以簡易方式呈現
        response = insight_agent.query(user_text)
        reply_text = response.content
    except Exception as e:
        reply_text = f"分析過程中發生錯誤：{str(e)}"
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
