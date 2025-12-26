# STLINE AI Trainer - 展開・デプロイガイド

## 🌍 展開可能な環境

### ローカル環境

#### macOS
- ✅ **完全対応**
- Python 3.10以上（現在: Python 3.14.2で動作確認済み）
- 推奨: macOS 11.0以上

#### Windows
- ✅ **対応可能**
- Python 3.10以上
- 推奨: Windows 10/11
- 注意: CUDA対応GPUがある場合、GPU加速が可能

#### Linux
- ✅ **完全対応**
- Python 3.10以上
- 推奨: Ubuntu 20.04 LTS / 22.04 LTS
- 推奨: Debian 11/12
- 推奨: CentOS 8 / Rocky Linux 8

### クラウド環境

#### AWS (Amazon Web Services)
- ✅ **対応可能**
- **推奨インスタンスタイプ:**
  - EC2: `g4dn.xlarge` 以上（GPU推奨）
  - EC2: `t3.medium` 以上（CPUのみ）
- **推奨AMI:** Ubuntu 22.04 LTS
- **ストレージ:** 20GB以上（モデルファイル用）

#### Google Cloud Platform (GCP)
- ✅ **対応可能**
- **推奨インスタンスタイプ:**
  - Compute Engine: `n1-standard-4` + GPU（NVIDIA T4推奨）
  - Compute Engine: `e2-standard-4`（CPUのみ）
- **推奨OS:** Ubuntu 22.04 LTS

#### Microsoft Azure
- ✅ **対応可能**
- **推奨VMサイズ:**
  - `Standard_NC6s_v3`（GPU推奨）
  - `Standard_D4s_v3`（CPUのみ）
- **推奨OS:** Ubuntu 22.04 LTS

#### Heroku
- ⚠️ **部分的対応**
- 制限: GPU非対応、メモリ制限あり
- 推奨: 開発・テスト環境のみ

#### Railway
- ✅ **対応可能**
- CPU環境で動作可能
- GPUは利用不可

#### Render
- ✅ **対応可能**
- CPU環境で動作可能
- GPUは利用不可

#### DigitalOcean
- ✅ **対応可能**
- **推奨ドロップレット:**
  - CPU Optimized: 4GB RAM以上
  - GPU Droplets（NVIDIA GPU利用可能）

### Docker環境

#### Docker
- ✅ **完全対応**
- Dockerfileを作成可能
- マルチステージビルド対応

#### Docker Compose
- ✅ **対応可能**
- Webダッシュボード + AIトレーナーの同時起動

#### Kubernetes
- ✅ **対応可能**
- マイクロサービスアーキテクチャで展開可能

### コンテナ環境

#### Docker
- ✅ **推奨**
- 環境の一貫性を保証
- 簡単なデプロイ

#### Podman
- ✅ **対応可能**
- Docker互換

## 📋 システム要件

### 最小要件

```
OS: macOS 11+, Windows 10+, Ubuntu 20.04+
CPU: Intel Core i5 / AMD Ryzen 5 以上
RAM: 8GB以上（推奨: 16GB）
ストレージ: 10GB以上の空き容量
Python: 3.10以上
```

### 推奨要件

```
OS: macOS 13+, Windows 11, Ubuntu 22.04 LTS
CPU: Intel Core i7 / AMD Ryzen 7 以上
RAM: 16GB以上（32GB推奨）
GPU: NVIDIA GPU（CUDA対応、RTX 3060以上推奨）
ストレージ: 50GB以上の空き容量（SSD推奨）
Python: 3.11以上
```

### GPU要件（オプション）

```
NVIDIA GPU: RTX 3060以上
VRAM: 6GB以上
CUDA: 11.8以上
cuDNN: 8.6以上
```

## 🐳 Docker展開

### Dockerfileの作成

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# システム依存関係のインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# ポート公開
EXPOSE 5000

# 起動コマンド
CMD ["python", "gym_dashboard.py"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  dashboard:
    build: .
    ports:
      - "5000:5000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - STREAM_API_KEY=${STREAM_API_KEY}
      - STREAM_API_SECRET=${STREAM_API_SECRET}
    volumes:
      - ./data:/app/data
    command: python gym_dashboard.py

  trainer:
    build: .
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - STREAM_API_KEY=${STREAM_API_KEY}
      - STREAM_API_SECRET=${STREAM_API_SECRET}
    volumes:
      - ./data:/app/data
    command: python personal_gym_trainer.py
```

## ☁️ クラウド展開例

### AWS EC2展開

```bash
# 1. EC2インスタンスを起動（Ubuntu 22.04 LTS）
# 2. SSH接続
ssh -i your-key.pem ubuntu@your-instance-ip

# 3. システム更新
sudo apt update && sudo apt upgrade -y

# 4. Python 3.11をインストール
sudo apt install python3.11 python3.11-venv python3-pip -y

# 5. プロジェクトをクローンまたはアップロード
git clone <repository-url>
cd STLINE-AI-Trainer

# 6. 仮想環境を作成
python3.11 -m venv venv
source venv/bin/activate

# 7. 依存関係をインストール
pip install -r requirements.txt

# 8. 環境変数を設定
nano .env

# 9. 起動
python gym_dashboard.py
```

### Google Cloud Run（サーバーレス）

```bash
# Cloud Run用のDockerfileを作成
# requirements.txtを最適化（軽量化）

# デプロイ
gcloud run deploy stline-ai-trainer \
  --source . \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated
```

## 🔒 セキュリティ考慮事項

### 本番環境での推奨設定

1. **HTTPS化**
   - Let's Encryptを使用したSSL証明書
   - Nginxリバースプロキシ

2. **環境変数の管理**
   - AWS Secrets Manager
   - Google Secret Manager
   - HashiCorp Vault

3. **ファイアウォール設定**
   - 必要なポートのみ開放
   - デフォルト: 5000（HTTP）、443（HTTPS）

4. **認証・認可**
   - 管理者認証の追加
   - APIキーの保護

## 📊 パフォーマンス最適化

### CPU環境

- FPSを下げる（`stline_config.py`で`default_fps: 3`）
- プロセッサ数を制限
- キャッシュを有効化

### GPU環境

- CUDAを有効化
- バッチサイズを調整
- 混合精度を使用

## 🌐 ネットワーク要件

### 必要なポート

- **5000**: Webダッシュボード（HTTP）
- **443**: HTTPS（本番環境）
- **WebRTC**: Stream API経由（動的ポート）

### 帯域幅

- **最小**: 1Mbps
- **推奨**: 10Mbps以上
- **ビデオ通話**: 5Mbps以上（ユーザーあたり）

## 📝 展開チェックリスト

### 展開前

- [ ] Python 3.10以上がインストールされている
- [ ] 必要なポートが開放されている
- [ ] APIキーが設定されている
- [ ] ストレージ容量が十分ある
- [ ] ネットワーク接続が安定している

### 展開後

- [ ] Webダッシュボードが起動する
- [ ] ブラウザでアクセスできる
- [ ] ユーザー登録ができる
- [ ] データが保存される
- [ ] ログが正常に出力される

## 🔗 展開先別の詳細ガイド

- **AWS展開**: `docs/deployment/aws.md`（作成予定）
- **GCP展開**: `docs/deployment/gcp.md`（作成予定）
- **Docker展開**: `docs/deployment/docker.md`（作成予定）
- **Kubernetes展開**: `docs/deployment/kubernetes.md`（作成予定）

