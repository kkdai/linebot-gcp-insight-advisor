import os
import json
import subprocess

def get_optimization_recommendations() -> str:
    """
    獲取 Google Cloud Active Assist 的成本優化建議。
    特別是尋找閒置的資源 (Idle Resource)。
    
    Returns:
        str: JSON 格式的建議摘要字串。
    """
    try:
        # 使用 gcloud 指令查詢 (這裡建議在 Cloud Run 上綁定具備 recommender.viewer 的 SA)
        cmd = "gcloud recommender recommendations list --recommender=google.compute.instance.IdleResourceRecommender --format=json"
        result = subprocess.check_output(cmd, shell=True, text=True)
        recommendations = json.loads(result)
        
        if not recommendations:
            return "目前專案中沒有發現可以優化的閒置運算資源。"
        
        # 簡化回傳資料，只取前 3 個重要建議
        summary = []
        for rec in recommendations[:3]:
            desc = rec.get("description", "無描述")
            impact = rec.get("primaryImpact", {}).get("costProjection", {}).get("cost", {})
            units = impact.get("units", "0")
            currency = impact.get("currencyCode", "USD")
            summary.append(f"建議: {desc} (預計節省: {units} {currency})")
            
        return json.dumps(summary, ensure_ascii=False)
    except Exception as e:
        return f"無法獲取優化建議，可能權限不足或設定錯誤: {str(e)}"

def get_cloud_run_status() -> str:
    """
    獲取當前專案中 Cloud Run 服務的健康狀態與基本配置。
    
    Returns:
        str: JSON 格式的狀態字串。
    """
    try:
        cmd = "gcloud run services list --format=json"
        result = subprocess.check_output(cmd, shell=True, text=True)
        services = json.loads(result)
        
        if not services:
            return "目前沒有部署任何 Cloud Run 服務。"
            
        summary = []
        for svc in services:
            name = svc.get("metadata", {}).get("name", "Unknown")
            status = svc.get("status", {}).get("conditions", [])
            is_ready = next((c for c in status if c.get("type") == "Ready"), {}).get("status") == "True"
            summary.append({
                "service": name,
                "status": "Ready" if is_ready else "Not Ready"
            })
            
        return json.dumps(summary, ensure_ascii=False)
    except Exception as e:
        return f"無法獲取 Cloud Run 狀態: {str(e)}"

def get_billing_summary() -> str:
    """
    獲取近期的帳單總結資訊 (模擬函式，實際建議呼叫 Cloud Billing API)。
    
    Returns:
        str: 帳單資訊字串。
    """
    # 注意：這裡使用假資料展示。實務上應呼叫 google-cloud-billing API 或 BigQuery Billing Export
    return json.dumps({
        "current_month_cost": "150.25 USD",
        "top_spending_service": "Cloud SQL",
        "trend": "較上月增加 5%"
    }, ensure_ascii=False)
