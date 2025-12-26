# 🚀 本番環境への展開ガイド

## ⚠️ ロリポップについて

ロリポップ（ロリポップ！レンタルサーバー）は主にPHP/WordPress向けのサービスで、**Pythonアプリケーションの実行には適していません**。

### ロリポップの制限

- ❌ Python 3.10以上が利用できない
- ❌ 大型パッケージ（torch、vision-agents等）がインストールできない
- ❌ 長時間実行プロセスに制限
- ❌ WebSocket/リアルタイム通信に制限

## ✅ 推奨される展開方法

### オプション1: VPSサーバー（最推奨）⭐⭐⭐

**推奨サービス:**
- **ConoHa VPS**: 月額500円〜 https://www.conoha.jp/
- **さくらのVPS**: 月額500円〜 https://vps.sakura.ad.jp/

**メリット:**
- ✅ 完全なrootアクセス
- ✅ すべての機能が動作
- ✅ コストパフォーマンスが良い
- ✅ 日本語サポート

**詳細**: `VPS_DEPLOYMENT.md` を参照

### オプション2: Railway（簡単）⭐⭐

**URL**: https://railway.app/

**メリット:**
- ✅ 無料プランあり
- ✅ 簡単にデプロイ可能
- ✅ 自動デプロイ

**デプロイ手順:**

1. GitHubにリポジトリをプッシュ
2. Railwayで「New Project」を選択
3. GitHubリポジトリを選択
4. 環境変数を設定:
   - `GEMINI_API_KEY`
   - `STREAM_API_KEY`
   - `STREAM_API_SECRET`
5. デプロイ

**URL**: `https://your-app.railway.app`

### オプション3: Render（簡単）⭐⭐

**URL**: https://render.com/

**デプロイ手順:**

1. GitHubにリポジトリをプッシュ
2. Renderで「New Web Service」を選択
3. リポジトリを選択
4. 設定:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python gym_dashboard.py`
5. 環境変数を設定
6. デプロイ

**URL**: `https://your-app.onrender.com`

## 🎯 具体的な展開手順（VPS推奨）

### ステップ1: VPSサーバーを準備

1. ConoHaまたはさくらのVPSでサーバーを作成
2. OS: **Ubuntu 22.04 LTS** を選択
3. プラン: **1GB RAM以上**を推奨（2GB推奨）

### ステップ2: サーバーに接続

```bash
ssh root@your-server-ip
```

### ステップ3: 自動セットアップスクリプトを実行

サーバーで以下を実行：

```bash
# システム更新
apt update && apt upgrade -y

# 必要なパッケージをインストール
apt install -y python3.11 python3.11-venv python3-pip git build-essential

# ファイアウォール設定
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 5000/tcp
ufw enable
```

### ステップ4: プロジェクトをアップロード

#### 方法A: 展開スクリプトを使用（推奨）

ローカルマシンで実行：
```bash
cd /Users/hikarunejikane/Downloads/STLINE-AI-Trainer
./deploy_to_vps.sh your-server-ip
```

#### 方法B: 手動でアップロード

ローカルマシンで実行：
```bash
cd /Users/hikarunejikane/Downloads/STLINE-AI-Trainer
scp -r . root@your-server-ip:/var/www/stline-ai-trainer/
```

### ステップ5: サーバーでセットアップ

サーバーにSSH接続して：

```bash
cd /var/www/stline-ai-trainer

# 仮想環境を作成
python3.11 -m venv venv
source venv/bin/activate

# 依存関係をインストール
pip install --upgrade pip
pip install -r requirements.txt

# .envファイルを作成
nano .env
```

`.env`ファイルに以下を入力：
```bash
GEMINI_API_KEY=あなたのGemini_APIキー
STREAM_API_KEY=あなたのStream_APIキー
STREAM_API_SECRET=あなたのStream_API_Secret
DEBUG=false
LOG_LEVEL=INFO
```

### ステップ6: systemdサービスとして設定

```bash
# サービスファイルをコピー
cp systemd_service_template.service /etc/systemd/system/stline-dashboard.service

# パスを修正（必要に応じて）
nano /etc/systemd/system/stline-dashboard.service

# サービスを有効化
systemctl daemon-reload
systemctl enable stline-dashboard
systemctl start stline-dashboard

# ステータス確認
systemctl status stline-dashboard
```

### ステップ7: アクセス確認

ブラウザで以下にアクセス：
```
http://your-server-ip:5000
```

## 🌐 ドメインとHTTPS化（オプション）

### Nginx + Let's Encrypt

```bash
# Nginxをインストール
apt install -y nginx

# 設定ファイルを作成
nano /etc/nginx/sites-available/stline-ai-trainer
```

以下を入力：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

有効化とSSL設定：
```bash
ln -s /etc/nginx/sites-available/stline-ai-trainer /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# SSL証明書を取得
apt install -y certbot python3-certbot-nginx
certbot --nginx -d your-domain.com
```

これで `https://your-domain.com` でアクセスできます。

## 📊 コスト比較

| サービス | 月額料金 | 特徴 |
|---------|---------|------|
| **ConoHa VPS** | 500円〜 | ⭐⭐⭐ 完全制御、推奨 |
| **さくらのVPS** | 500円〜 | ⭐⭐⭐ 安定性高い |
| **Railway** | 無料〜 | ⭐⭐ 簡単デプロイ |
| **Render** | 無料〜 | ⭐⭐ 簡単デプロイ |
| **ロリポップ** | 250円〜 | ⚠️ Python非対応 |

## 🎯 推奨展開方法

### 最も簡単: Railway

1. GitHubにプッシュ
2. Railwayで接続
3. 環境変数を設定
4. デプロイ完了

**URL**: `https://your-app.railway.app`

### 最も柔軟: VPS（ConoHa/さくら）

1. VPSサーバーを作成
2. 展開スクリプトを実行
3. systemdサービスを設定
4. 完了

**URL**: `http://your-server-ip:5000` または `https://your-domain.com`

## 📝 まとめ

**ロリポップは使用不可** → **VPSまたはPaaSを推奨**

1. **簡単に始める**: Railway / Render
2. **完全な制御**: ConoHa VPS / さくらのVPS
3. **コスト重視**: ConoHa VPS（月額500円〜）

詳細は各ガイドを参照：
- `VPS_DEPLOYMENT.md` - VPS展開の詳細
- `DEPLOYMENT_GUIDE.md` - 全般的な展開ガイド

