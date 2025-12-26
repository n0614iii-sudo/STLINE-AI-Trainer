# 🚀 GitHubへのプッシュ - 簡単手順

## 📖 用語の簡単な説明

- **GitHub**: コードを保存するクラウドサービス（Googleドライブのようなもの）
- **プッシュ**: ローカルのコードをGitHubにアップロードすること
- **リポジトリ**: プロジェクトのフォルダ（このプロジェクト全体）

## 🎯 3ステップで完了

### ステップ1: GitHubアカウントを作成

1. https://github.com/ にアクセス
2. 「Sign up」をクリック
3. アカウントを作成

### ステップ2: GitHubでリポジトリを作成

1. https://github.com/new にアクセス
2. リポジトリ名: `STLINE-AI-Trainer`
3. **「Initialize this repository with a README」のチェックを外す**（重要！）
4. 「Create repository」をクリック

### ステップ3: ターミナルで実行

```bash
cd /Users/hikarunejikane/Downloads/STLINE-AI-Trainer

# 自動セットアップスクリプトを実行
./setup_github.sh
```

その後、GitHubのリポジトリURLを入力するか、手動で以下を実行：

```bash
# YOUR-USERNAMEをあなたのGitHubユーザー名に置き換えてください
git remote add origin https://github.com/YOUR-USERNAME/STLINE-AI-Trainer.git
git branch -M main
git push -u origin main
```

## ✅ 完了！

これで、コードがGitHubに保存されました！

GitHubのリポジトリページで確認できます：
`https://github.com/YOUR-USERNAME/STLINE-AI-Trainer`

## 🔄 今後の更新方法

コードを変更したら：

```bash
git add .
git commit -m "変更内容"
git push
```

## 📚 詳細な説明

詳しい説明は `GITHUB_SETUP.md` を参照してください。
