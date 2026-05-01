# GCP Insight Advisor LINE Bot

這是一個基於 **Google ADK (Agent Development Kit)** 開發的智能 GCP 顧問 LINE Bot。它利用 Gemini 2.0 Flash 模型，結合自定義的 **Google Skills** (雲端知識庫) 與 GCP 監控工具，為使用者提供專業的雲端架構建議與成本優化分析。

## 專案位置
- GitHub 倉庫: [kkdai/linebot-gcp-insight-advisor](https://github.com/kkdai/linebot-gcp-insight-advisor)

## 主要功能

本 Bot 扮演一位資深 GCP 顧問，具備以下核心能力：

1.  **成本優化建議 (Cost Optimization)**：
    - 自動查詢 Google Cloud Active Assist 的建議。
    - 識別閒置資源（如 Idle VM Instances），並估算可節省的金額。
2.  **資源狀態監控**：
    - 即時查詢 Cloud Run 服務的運行狀態與健康程度。
3.  **帳單摘要分析**：
    - 提供當月預估支出、最高消費服務以及費用趨勢分析。
4.  **專業雲端知識庫 (Google Skills Integration)**：
    - 整合了關於成本優化與 Cloud Run 最佳實踐的專業知識，能根據實務經驗回答複雜的架構問題。

> **安全說明**：本 Bot 僅具備「唯讀」權限，無法執行任何資源的建立、修改或刪除操作，確保您的生產環境安全無虞。

---

## 安裝與部署手冊

### 1. 準備工作
- 一個 **GCP 專案** 並開啟 Billing。
- 已安裝 **gcloud CLI** 並完成驗證。
- 一個 **LINE Developers** 帳號，並建立一個 Messaging API Channel。
- 取得 `LINE_CHANNEL_ACCESS_TOKEN` 與 `LINE_CHANNEL_SECRET`。

### 2. 本地開發環境設定
```bash
# 複製專案
git clone https://github.com/kkdai/linebot-gcp-insight-advisor.git
cd linebot-gcp-insight-advisor

# 安裝依賴
pip install -r requirements.txt
```

### 3. GCP 服務帳號設定
本專案需要適當的權限來讀取 GCP 資訊。
1. 在 IAM 管理介面建立一個服務帳號 (Service Account)。
2. 授予以下角色：
   - `Recommender Viewer` (讀取優化建議)
   - `Cloud Run Viewer` (查看服務狀態)
   - `Billing Viewer` (查看帳單摘要，若需實際串接 API)

### 4. 透過 Cloud Build 自動部署
本專案已包含 `cloudbuild.yaml` 與 `Dockerfile`，支援自動化部署。

1. **建立 Cloud Build 觸發器**：
   - 前往 GCP 控制台的 [Cloud Build 觸發器頁面](https://console.cloud.google.com/cloud-build/triggers)。
   - 連接您的 GitHub 倉庫 `kkdai/linebot-gcp-insight-advisor`。
   - 設定推送到 `main` 分支時自動執行。
   - 設定檔選擇 `cloudbuild.yaml`。
2. **部署至 Cloud Run**：
   - 第一次執行 Cloud Build 後，它會自動建立一個名為 `linebot-gcp-insight-advisor` 的 Cloud Run 服務。
   - 前往 Cloud Run 服務設定，加入環境變數：
     - `LINE_CHANNEL_ACCESS_TOKEN`: (您的 Token)
     - `LINE_CHANNEL_SECRET`: (您的 Secret)

### 5. 設定 LINE Webhook
1. 複製 Cloud Run 產生的服務 URL (例如 `https://linebot-gcp-xxx.a.run.app`)。
2. 在 LINE Developers Console 的 Messaging API 設定中，將 Webhook URL 設定為：`https://您的URL/callback`。
3. 點擊 "Verify" 驗證通過後，開啟 "Use webhook"。

---

## 運作流程說明

1.  **使用者傳送訊息**：使用者透過 LINE 詢問 GCP 相關問題（例如：「我有什麼可以省錢的建議嗎？」）。
2.  **Web 服務接收**：位於 Cloud Run 的 FastAPI 接收 LINE Webhook 請求。
3.  **ADK Agent 推理**：
    - `insight_agent` (基於 ADK) 接收到文字。
    - Agent 根據問題判斷是否需要呼叫 `tools.py` 中的工具（如 `get_optimization_recommendations`）。
    - 工具透過 `gcloud` 指令或 API 抓取 GCP 實體數據。
4.  **結合知識庫 (Skills)**：Agent 將抓取到的數據，結合 `skills/` 目錄下的知識文件，生成專業的分析回覆。
5.  **回傳 LINE**：分析結果經由 LINE Messaging API 回傳給使用者。
