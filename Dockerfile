# STLINE AI Trainer - Dockerfile
FROM python:3.11-slim

# メタデータ
LABEL maintainer="HIKARU NEJIKANE"
LABEL description="STLINE AI Personal Trainer System"
LABEL version="1.0.0"

# 作業ディレクトリ
WORKDIR /app

# システム依存関係のインストール（最小限）
# OpenCV headless版を使用するため、GUI関連のライブラリは不要
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係のインストール
# torchとtorchvisionをCPU版でインストール（サイズ削減）
# requirements.txtからtorchとtorchvisionを除外したバージョンを使用
COPY requirements.txt requirements-railway.txt* ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    (pip install --no-cache-dir -r requirements-railway.txt 2>/dev/null || pip install --no-cache-dir -r requirements.txt)

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

# 起動コマンド
CMD ["python", "gym_dashboard.py"]

