# 使用輕量級的 Python 3.11 映像檔
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 將需求清單複製到容器並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安裝 gcloud CLI (工具需要用到 gcloud 指令)
RUN apt-get update && apt-get install -y curl apt-transport-https ca-certificates gnupg \
    && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - \
    && apt-get update && apt-get install -y google-cloud-cli \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 將所有程式碼複製到容器
COPY . .

# 曝露 Cloud Run 使用的連接埠 (預設 8080)
EXPOSE 8080

# 啟動 FastAPI 服務
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
