#!/bin/bash
# STLINE AI Trainer - 起動スクリプト

cd "$(dirname "$0")"

# 仮想環境を有効化
if [ ! -d "venv" ]; then
    echo "❌ 仮想環境が見つかりません"
    echo "   まずセットアップを完了してください"
    exit 1
fi

source venv/bin/activate

echo "============================================================"
echo "STLINE AI Trainer - 起動"
echo "============================================================"
echo ""

# オプションを確認
if [ "$1" = "dashboard" ]; then
    echo "🌐 Webダッシュボードを起動します..."
    echo "   ブラウザで http://localhost:5000 にアクセスしてください"
    echo ""
    python gym_dashboard.py
elif [ "$1" = "trainer" ]; then
    echo "🤖 AIトレーナーを起動します..."
    echo ""
    python personal_gym_trainer.py
elif [ "$1" = "demo" ]; then
    echo "📊 デモデータを作成します..."
    echo ""
    python demo.py create-data
else
    echo "使用方法:"
    echo "  ./START.sh dashboard  # Webダッシュボードを起動"
    echo "  ./START.sh trainer    # AIトレーナーを起動"
    echo "  ./START.sh demo       # デモデータを作成"
    echo ""
    echo "または、仮想環境を有効化して直接実行:"
    echo "  source venv/bin/activate"
    echo "  python gym_dashboard.py"
fi

