#!/bin/bash
# STLINE AI Trainer - 依存関係インストールスクリプト

echo "============================================================"
echo "STLINE AI Trainer - 依存関係のインストール"
echo "============================================================"
echo ""

# pipのアップグレード
echo "📦 pipをアップグレード中..."
python3 -m pip install --upgrade pip --quiet

# 依存関係のインストール
echo "📦 依存関係をインストール中..."
echo "   （これには数分かかる場合があります）"
echo ""

python3 -m pip install -r requirements.txt

echo ""
echo "============================================================"
if [ $? -eq 0 ]; then
    echo "✅ 依存関係のインストールが完了しました！"
    echo "============================================================"
    echo ""
    echo "次のステップ:"
    echo "  1. python3 setup_api_keys.py  # APIキーを設定（まだの場合）"
    echo "  2. python3 test_setup.py     # セットアップ確認"
    echo "  3. python3 demo.py create-data  # デモデータ作成（オプション）"
    echo "  4. python3 gym_dashboard.py  # Webダッシュボード起動"
else
    echo "❌ インストール中にエラーが発生しました"
    echo "============================================================"
    exit 1
fi

