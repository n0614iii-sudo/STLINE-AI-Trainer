# 🚀 GitHubにプッシュする方法

## 現在の状況

✅ Gitリポジトリは初期化済み
✅ ファイルはコミット済み
⚠️ GitHubへのプッシュには認証が必要

## 方法1: Personal Access Tokenを使用（推奨）

### ステップ1: Personal Access Tokenを作成

1. GitHubにログイン
2. 右上のプロフィール画像をクリック → **Settings**
3. 左メニューの一番下 → **Developer settings**
4. **Personal access tokens** → **Tokens (classic)**
5. **Generate new token** → **Generate new token (classic)** をクリック
6. 設定:
   - **Note**: `STLINE-AI-Trainer`（任意の名前）
   - **Expiration**: `90 days` または `No expiration`（お好みで）
   - **Select scopes**: `repo` にチェック（すべてのリポジトリへのアクセス）
7. **Generate token** をクリック
8. **トークンをコピー**（⚠️ この画面を閉じると二度と見れません！）

### ステップ2: プッシュを実行

ターミナルで以下を実行：

```bash
cd /Users/hikarunejikane/Downloads/STLINE-AI-Trainer

# GitHubに接続
git remote add origin https://github.com/n0614iii-sudo/STLINE-AI-Trainer.git

# ブランチ名をmainに設定
git branch -M main

# プッシュ（ユーザー名とトークンを入力）
git push -u origin main
```

**入力内容:**
- **Username**: `n0614iii-sudo`
- **Password**: 先ほどコピーした**Personal Access Token**を貼り付け

## 方法2: SSHキーを使用（より安全）

### ステップ1: SSHキーを生成

```bash
# SSHキーを生成（まだの場合）
ssh-keygen -t ed25519 -C "your_email@example.com"

# 公開鍵を表示
cat ~/.ssh/id_ed25519.pub
```

### ステップ2: GitHubにSSHキーを登録

1. 表示された公開鍵をコピー
2. GitHub → Settings → **SSH and GPG keys**
3. **New SSH key** をクリック
4. タイトルを入力し、公開鍵を貼り付け
5. **Add SSH key** をクリック

### ステップ3: SSH URLで接続

```bash
cd /Users/hikarunejikane/Downloads/STLINE-AI-Trainer

# SSH URLに変更
git remote set-url origin git@github.com:n0614iii-sudo/STLINE-AI-Trainer.git

# プッシュ
git push -u origin main
```

## 方法3: GitHub CLIを使用（最も簡単）

### ステップ1: GitHub CLIをインストール

```bash
# macOSの場合
brew install gh

# ログイン
gh auth login
```

### ステップ2: プッシュ

```bash
cd /Users/hikarunejikane/Downloads/STLINE-AI-Trainer
git push -u origin main
```

## 🎯 推奨: 方法1（Personal Access Token）

最も簡単で確実な方法です。

1. Personal Access Tokenを作成（上記の手順）
2. 以下のコマンドを実行：

```bash
cd /Users/hikarunejikane/Downloads/STLINE-AI-Trainer
git remote add origin https://github.com/n0614iii-sudo/STLINE-AI-Trainer.git
git branch -M main
git push -u origin main
```

**認証情報:**
- Username: `n0614iii-sudo`
- Password: Personal Access Token（コピーしたトークン）

## ✅ 確認

プッシュが成功したら、GitHubのリポジトリページをリロードして、ファイルが表示されているか確認してください：

https://github.com/n0614iii-sudo/STLINE-AI-Trainer

## 🔄 今後の更新

一度プッシュしたら、今後の更新は簡単です：

```bash
git add .
git commit -m "変更内容の説明"
git push
```

（認証情報は一度入力すれば保存されます）



