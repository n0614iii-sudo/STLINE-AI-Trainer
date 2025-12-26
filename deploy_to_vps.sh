#!/bin/bash
# VPSサーバーへの展開スクリプト

set -e

echo "============================================================"
echo "STLINE AI Trainer - VPS展開スクリプト"
echo "============================================================"
echo ""

# 設定
SERVER_IP="${1:-}"
SERVER_USER="${2:-root}"
PROJECT_DIR="/var/www/stline-ai-trainer"

if [ -z "$SERVER_IP" ]; then
    echo "使用方法:"
    echo "  ./deploy_to_vps.sh <server-ip> [user]"
    echo ""
    echo "例:"
    echo "  ./deploy_to_vps.sh 123.456.789.0"
    echo "  ./deploy_to_vps.sh 123.456.789.0 ubuntu"
    exit 1
fi

echo "サーバー: $SERVER_USER@$SERVER_IP"
echo "プロジェクトディレクトリ: $PROJECT_DIR"
echo ""

# 確認
read -p "このサーバーに展開しますか？ (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "キャンセルされました。"
    exit 0
fi

echo ""
echo "展開を開始します..."
echo ""

# 1. プロジェクトをアップロード
echo "📦 プロジェクトをアップロード中..."
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' \
    --exclude '.git' --exclude '*.log' --exclude 'data/*.json' \
    ./ $SERVER_USER@$SERVER_IP:$PROJECT_DIR/

echo "✅ アップロード完了"
echo ""

# 2. サーバーでセットアップスクリプトを実行
echo "🔧 サーバーでセットアップ中..."
ssh $SERVER_USER@$SERVER_IP << EOF
set -e

cd $PROJECT_DIR

# 仮想環境を作成（存在しない場合）
if [ ! -d "venv" ]; then
    python3.11 -m venv venv
fi

# 仮想環境を有効化して依存関係をインストール
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# .envファイルが存在しない場合、テンプレートを作成
if [ ! -f ".env" ]; then
    echo "⚠️  .envファイルが見つかりません"
    echo "   サーバーで手動で作成してください:"
    echo "   nano $PROJECT_DIR/.env"
fi

echo "✅ セットアップ完了"
EOF

echo ""
echo "============================================================"
echo "✅ 展開が完了しました！"
echo "============================================================"
echo ""
echo "次のステップ:"
echo "  1. サーバーにSSH接続:"
echo "     ssh $SERVER_USER@$SERVER_IP"
echo ""
echo "  2. .envファイルを設定:"
echo "     nano $PROJECT_DIR/.env"
echo ""
echo "  3. systemdサービスを設定:"
echo "     sudo nano /etc/systemd/system/stline-dashboard.service"
echo ""
echo "  4. サービスを起動:"
echo "     sudo systemctl start stline-dashboard"
echo ""
echo "  5. ブラウザでアクセス:"
echo "     http://$SERVER_IP:5000"
echo ""

