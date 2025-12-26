# STLINE AI Trainer - 展開可能な環境まとめ

## 🌍 展開可能な環境

### ✅ 完全対応

1. **ローカル環境**
   - macOS 11.0以上（✅ 現在の環境で動作確認済み）
   - Windows 10/11
   - Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+)

2. **クラウド環境**
   - AWS EC2
   - Google Cloud Platform (GCP)
   - Microsoft Azure
   - DigitalOcean

3. **コンテナ環境**
   - Docker
   - Docker Compose
   - Kubernetes

4. **PaaS環境**
   - Railway
   - Render
   - Heroku（制限あり）

## 📋 システム要件

### 最小要件
- OS: macOS 11+, Windows 10+, Ubuntu 20.04+
- CPU: Intel Core i5 / AMD Ryzen 5 以上
- RAM: 8GB以上
- ストレージ: 10GB以上
- Python: 3.10以上

### 推奨要件
- OS: macOS 13+, Windows 11, Ubuntu 22.04 LTS
- CPU: Intel Core i7 / AMD Ryzen 7 以上
- RAM: 16GB以上（32GB推奨）
- GPU: NVIDIA GPU（CUDA対応、RTX 3060以上推奨）
- ストレージ: 50GB以上（SSD推奨）
- Python: 3.11以上

## 🚀 展開方法

### 1. ローカル展開（現在の環境）

```bash
source venv/bin/activate
python gym_dashboard.py
```

### 2. Docker展開

```bash
docker build -t stline-ai-trainer .
docker run -p 5000:5000 --env-file .env stline-ai-trainer
```

### 3. Docker Compose展開

```bash
docker-compose up -d
```

### 4. クラウド展開

各クラウドプロバイダーのドキュメントを参照:
- AWS: `DEPLOYMENT_GUIDE.md`
- GCP: `DEPLOYMENT_GUIDE.md`
- Azure: `DEPLOYMENT_GUIDE.md`

## 📝 注意事項

- GPUはオプション（CPUでも動作可能）
- ビデオ通話機能には安定したネットワーク接続が必要
- 本番環境ではHTTPS化を推奨
