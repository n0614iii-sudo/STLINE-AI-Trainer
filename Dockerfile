# STLINE AI Trainer - Dockerfile
FROM python:3.11-slim

# メタデータ
LABEL maintainer="HIKARU NEJIKANE"
LABEL description="STLINE AI Personal Trainer System"
LABEL version="1.0.0"

# 作業ディレクトリ
WORKDIR /app

# システム依存関係のインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# データディレクトリの作成
RUN mkdir -p /app/data /app/logs

# 環境変数の設定
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=gym_dashboard.py
ENV FLASK_ENV=production

# ポート公開
EXPOSE 5000

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000')" || exit 1

# 起動コマンド
CMD ["python", "gym_dashboard.py"]

