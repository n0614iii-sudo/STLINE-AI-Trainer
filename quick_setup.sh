#!/bin/bash
# STLINE AI Trainer - クイックセットアップスクリプト

echo "============================================================"
echo "STLINE AI Trainer - クイックセットアップ"
echo "============================================================"
echo ""

# Pythonバージョンチェック
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo "現在のPythonバージョン: $PYTHON_VERSION"

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo ""
    echo "⚠️  Python 3.10以上が必要です"
    echo ""
    echo "Python 3.11をインストールしますか？ (y/n)"
    read -r response
    
    if [ "$response" = "y" ]; then
        # Homebrewの確認
        if ! command -v brew &> /dev/null; then
            echo ""
            echo "Homebrewをインストールします..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        
        echo ""
        echo "Python 3.11をインストール中..."
        brew install python@3.11
        
        echo ""
        echo "✅ Python 3.11のインストールが完了しました"
        echo ""
        echo "次のコマンドを実行してください:"
        echo "  python3.11 -m venv venv"
        echo "  source venv/bin/activate"
        echo "  pip install -r requirements.txt"
    else
        echo ""
        echo "Python 3.10以上のインストールが必要です。"
        echo "詳細は SETUP_GUIDE.md を参照してください。"
        exit 1
    fi
else
    echo "✅ Pythonバージョンは問題ありません"
    echo ""
    
    # 仮想環境の確認
    if [ ! -d "venv" ]; then
        echo "仮想環境を作成中..."
        python3 -m venv venv
        echo "✅ 仮想環境を作成しました"
    fi
    
    echo ""
    echo "仮想環境を有効化してください:"
    echo "  source venv/bin/activate"
    echo ""
    echo "その後、依存関係をインストール:"
    echo "  pip install -r requirements.txt"
fi

