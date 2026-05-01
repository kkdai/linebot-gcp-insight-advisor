import asyncio
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from agent import insight_agent

async def main():
    app = App(name="GCP_Advisor_App", root_agent=insight_agent)
    session_service = InMemorySessionService()
    
    async with Runner(app=app, session_service=session_service) as runner:
        await session_service.create_session(app_name="GCP_Advisor_App", user_id="user1", session_id="session1")
        new_msg = types.Content(role="user", parts=[types.Part(text="hi")])
        async for event in runner.run_async(user_id="user1", session_id="session1", new_message=new_msg):
            # 檢查 event 的屬性來提取文字
            # 根據 ADK 代碼，它會產出各種 Event
            # 這裡我們試著找看看有沒有 text 屬性
            if hasattr(event, "text"):
                print(f"TEXT: {event.text}")
            elif hasattr(event, "content") and hasattr(event.content, "parts"):
                for part in event.content.parts:
                    if hasattr(part, "text"):
                        print(f"PART_TEXT: {part.text}")

if __name__ == "__main__":
    asyncio.run(main())
