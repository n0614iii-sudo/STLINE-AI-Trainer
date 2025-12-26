# VPSサーバーへの展開ガイド（ConoHa / さくらのVPS）

## 🚀 推奨VPSサービス

### ConoHa VPS（推奨）

- **URL**: https://www.conoha.jp/
- **価格**: 月額500円〜
- **特徴**: 
  - 完全なrootアクセス
  - Ubuntu/Debian対応
  - 簡単な管理画面

### さくらのVPS

- **URL**: https://vps.sakura.ad.jp/
- **価格**: 月額500円〜
- **特徴**:
  - 安定性が高い
  - 日本語サポート
  - 完全なrootアクセス

## 📋 展開手順

### ステップ1: VPSサーバーを準備

1. ConoHaまたはさくらのVPSでサーバーを作成
2. OS: Ubuntu 22.04 LTS を選択
3. プラン: 1GB RAM以上を推奨
4. SSHキーを設定

### ステップ2: サーバーに接続

```bash
ssh root@your-server-ip
```

### ステップ3: システムのセットアップ

```bash
# システム更新
apt update && apt upgrade -y

# 必要なパッケージをインストール
apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    git \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0

# ファイアウォール設定
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 5000/tcp  # アプリケーション
ufw enable
```

### ステップ4: プロジェクトをアップロード

#### 方法A: Gitを使用（推奨）

```bash
# プロジェクトディレクトリを作成
mkdir -p /var/www/stline-ai-trainer
cd /var/www/stline-ai-trainer

# Gitリポジトリからクローン（GitHubにプッシュしている場合）
git clone https://github.com/your-username/STLINE-AI-Trainer.git .

# または、ローカルからSCPでアップロード
# ローカルマシンで実行:
# scp -r /Users/hikarunejikane/Downloads/STLINE-AI-Trainer root@your-server-ip:/var/www/
```

#### 方法B: SCPでアップロード

ローカルマシンで実行：
```bash
cd /Users/hikarunejikane/Downloads
scp -r STLINE-AI-Trainer root@your-server-ip:/var/www/
```

### ステップ5: 仮想環境のセットアップ

```bash
cd /var/www/stline-ai-trainer

# 仮想環境を作成
python3.11 -m venv venv
source venv/bin/activate

# pipをアップグレード
pip install --upgrade pip

# 依存関係をインストール
pip install -r requirements.txt
```

### ステップ6: 環境変数の設定

```bash
# .envファイルを作成
nano .env
```

以下を入力：
```bash
GEMINI_API_KEY=あなたのGemini_APIキー
STREAM_API_KEY=あなたのStream_APIキー
STREAM_API_SECRET=あなたのStream_API_Secret
DEBUG=false
LOG_LEVEL=INFO
```

### ステップ7: systemdサービスとして設定

```bash
# サービスファイルを作成
nano /etc/systemd/system/stline-dashboard.service
```

以下を入力：
```ini
[Unit]
Description=STLINE AI Trainer Dashboard
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/stline-ai-trainer
Environment="PATH=/var/www/stline-ai-trainer/venv/bin"
ExecStart=/var/www/stline-ai-trainer/venv/bin/python gym_dashboard.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

サービスを有効化：
```bash
systemctl daemon-reload
systemctl enable stline-dashboard
systemctl start stline-dashboard
systemctl status stline-dashboard
```

### ステップ8: Nginxリバースプロキシの設定（オプション）

HTTPS化とドメイン設定：

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

有効化：
```bash
ln -s /etc/nginx/sites-available/stline-ai-trainer /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### ステップ9: SSL証明書の設定（Let's Encrypt）

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d your-domain.com
```

## 🔧 管理コマンド

### サービスの管理

```bash
# 起動
systemctl start stline-dashboard

# 停止
systemctl stop stline-dashboard

# 再起動
systemctl restart stline-dashboard

# ステータス確認
systemctl status stline-dashboard

# ログ確認
journalctl -u stline-dashboard -f
```

### ログの確認

```bash
# アプリケーションログ
tail -f /var/www/stline-ai-trainer/logs/stline_ai_trainer.log

# systemdログ
journalctl -u stline-dashboard -n 50
```

## 📊 リソース監視

```bash
# CPU/メモリ使用率
htop

# ディスク使用量
df -h

# ポートの確認
netstat -tlnp | grep 5000
```

## 🔒 セキュリティ設定

### 1. SSH鍵認証のみにする

```bash
nano /etc/ssh/sshd_config
# PasswordAuthentication no に設定
systemctl restart sshd
```

### 2. ファイアウォール設定

```bash
ufw status
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### 3. 定期的な更新

```bash
# 自動更新を設定
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

## 🎯 展開後の確認

1. **サービスが起動しているか確認**
   ```bash
   systemctl status stline-dashboard
   ```

2. **ブラウザでアクセス**
   ```
   http://your-server-ip:5000
   ```
   または
   ```
   https://your-domain.com
   ```

3. **ログを確認**
   ```bash
   journalctl -u stline-dashboard -n 100
   ```

## 💰 コスト目安

### ConoHa VPS
- **スタンダードプラン**: 月額500円（1GB RAM）
- **プレミアムプラン**: 月額1,000円（2GB RAM）← 推奨

### さくらのVPS
- **1Gプラン**: 月額500円
- **2Gプラン**: 月額1,000円← 推奨

## 📝 まとめ

1. **VPSサーバーを準備**（ConoHaまたはさくら）
2. **サーバーに接続**（SSH）
3. **システムをセットアップ**（Python、依存関係）
4. **プロジェクトをアップロード**（GitまたはSCP）
5. **systemdサービスとして設定**
6. **Nginxでリバースプロキシ**（オプション）
7. **SSL証明書を設定**（Let's Encrypt）

**これで本番環境として使用できます！**

