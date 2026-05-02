import asyncio
from linebot.v3.messaging import (
    Configuration,
    AsyncApiClient,
    AsyncMessagingApi,
    ReplyMessageRequest,
    TextMessage as LineTextMessage
)
from agent import insight_agent
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

# 模擬配置
config = Configuration(access_token="test_token")
adk_app = App(name="Test_App", root_agent=insight_agent)
session_service = InMemorySessionService()

async def test_flow():
    user_id = "test_user"
    user_text = "hi"
    
    print("--- Starting ADK Test ---")
    reply_parts = []
    try:
        async with Runner(app=adk_app, session_service=session_service) as runner:
            await session_service.create_session(app_name="Test_App", user_id=user_id, session_id=user_id)
            new_msg = types.Content(role="user", parts=[types.Part(text=user_text)])
            async for adk_event in runner.run_async(user_id=user_id, session_id=user_id, new_message=new_msg):
                if adk_event.content and adk_event.content.parts:
                    for part in adk_event.content.parts:
                        if part.text:
                            reply_parts.append(part.text)
                            print(f"Got text: {part.text}")
    except Exception as e:
        print(f"ADK Error: {e}")
    
    print(f"Full reply: {''.join(reply_parts)}")

if __name__ == "__main__":
    asyncio.run(test_flow())
