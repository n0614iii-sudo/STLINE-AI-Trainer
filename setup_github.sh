#!/bin/bash
# GitHubへのプッシュを簡単にするスクリプト

set -e

echo "============================================================"
echo "GitHubへのプッシュ設定"
echo "============================================================"
echo ""

# Gitがインストールされているか確認
if ! command -v git &> /dev/null; then
    echo "❌ Gitがインストールされていません"
    echo "   macOSの場合: Xcode Command Line Toolsをインストールしてください"
    echo "   xcode-select --install"
    exit 1
fi

echo "✅ Gitがインストールされています"
echo ""

# Gitリポジトリを初期化
if [ ! -d ".git" ]; then
    echo "📦 Gitリポジトリを初期化中..."
    git init
    echo "✅ Gitリポジトリを初期化しました"
else
    echo "✅ Gitリポジトリは既に初期化されています"
fi
echo ""

# .gitignoreが存在するか確認
if [ ! -f ".gitignore" ]; then
    echo "⚠️  .gitignoreが存在しません"
    echo "   作成してください"
fi
echo ""

# ファイルを追加
echo "📝 ファイルを追加中..."
git add .
echo "✅ ファイルを追加しました"
echo ""

# コミット
echo "💾 コミット中..."
git commit -m "Initial commit: STLINE AI Trainer" || {
    echo "⚠️  コミットに失敗しました（既にコミット済みの可能性があります）"
}
echo ""

echo "============================================================"
echo "✅ ローカルの準備が完了しました！"
echo "============================================================"
echo ""
echo "次のステップ:"
echo ""
echo "1. GitHubでリポジトリを作成:"
echo "   https://github.com/new"
echo "   - リポジトリ名: STLINE-AI-Trainer"
echo "   - 「Initialize this repository with a README」のチェックを外す"
echo "   - 「Create repository」をクリック"
echo ""
echo "2. GitHubのリポジトリURLをコピー"
echo "   例: https://github.com/your-username/STLINE-AI-Trainer.git"
echo ""
echo "3. 以下のコマンドを実行（YOUR-USERNAMEを置き換えてください）:"
echo ""
echo "   git remote add origin https://github.com/YOUR-USERNAME/STLINE-AI-Trainer.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "または、このスクリプトを再実行してGitHubのURLを入力:"
echo "   ./setup_github.sh https://github.com/YOUR-USERNAME/STLINE-AI-Trainer.git"
echo ""

# GitHubのURLが引数として渡された場合
if [ -n "$1" ]; then
    GITHUB_URL="$1"
    echo "GitHub URLが指定されました: $GITHUB_URL"
    echo ""
    
    # リモートが既に設定されているか確認
    if git remote get-url origin &> /dev/null; then
        echo "⚠️  既にリモートが設定されています"
        read -p "上書きしますか？ (y/n): " confirm
        if [ "$confirm" = "y" ]; then
            git remote set-url origin "$GITHUB_URL"
        else
            echo "キャンセルされました"
            exit 0
        fi
    else
        git remote add origin "$GITHUB_URL"
    fi
    
    echo ""
    echo "🚀 GitHubにプッシュ中..."
    git branch -M main
    git push -u origin main
    
    echo ""
    echo "============================================================"
    echo "✅ GitHubへのプッシュが完了しました！"
    echo "============================================================"
    echo ""
    echo "GitHubのリポジトリを確認してください:"
    echo "$GITHUB_URL"
    echo ""
fi

