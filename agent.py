import os
from google.adk.agents import Agent
from tools import get_optimization_recommendations, get_cloud_run_status, get_billing_summary

# 讀取本地載入的 Google Skills 檔案
def load_skill(filename: str) -> str:
    filepath = os.path.join(os.path.dirname(__file__), "skills", filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return ""

cost_optimization_skill = load_skill("cost-optimization.md")
cloud_run_skill = load_skill("cloud-run-basics.md")

# 初始化 GCP Insight Advisor Agent
insight_agent = Agent(
    name="GCP_Insight_Advisor",
    model="gemini-2.0-flash", # 使用具備高推論能力的模型
    instruction=f"""
    你是一位資深的 Google Cloud 雲端顧問 (GCP Insight Advisor)。你的職責是監控 GCP 資源狀態並提供優化建議。
    請嚴格遵守以下安全與行為準則：
    1. **唯讀權限：** 你只能執行唯讀操作，嚴禁建立、刪除或修改任何 GCP 資源。如果使用者提出此類要求，請回覆：『抱歉，為確保系統安全，我目前的權限僅限於顧問與監控，無法直接修改您的基礎設施。』
    2. **專業回覆：** 回答需簡潔專業，並優先考量「成本效益 (FinOps)」與「架構最佳實踐」。
    3. **利用技能：** 請參考以下的專家知識庫 (Google Skills) 來分析從工具獲取的數據並提供建議。
    
    --- 知識庫 1: 成本優化 (Cost Optimization) ---
    {cost_optimization_skill}
    
    --- 知識庫 2: Cloud Run 基礎 (Cloud Run Basics) ---
    {cloud_run_skill}
    """,
    tools=[get_optimization_recommendations, get_cloud_run_status, get_billing_summary]
)
