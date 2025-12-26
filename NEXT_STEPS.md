# 🚀 STLINE AI Trainer - 次のステップ

## 🌐 使用可能なURL

### ローカル環境

**Webダッシュボード:**
```
http://localhost:5000
```

このURLにブラウザでアクセスすると、Webダッシュボードが表示されます。

### 本番環境（デプロイ後）

デプロイ先に応じてURLが変わります：

- **Docker**: `http://your-server-ip:5000`
- **AWS EC2**: `http://your-ec2-ip:5000` または `https://your-domain.com`
- **Railway**: `https://your-app.railway.app`
- **Render**: `https://your-app.onrender.com`

## 📋 今すぐできること

### ステップ1: Webダッシュボードを起動

```bash
cd /Users/hikarunejikane/Downloads/STLINE-AI-Trainer
source venv/bin/activate
python gym_dashboard.py
```

### ステップ2: ブラウザでアクセス

以下のURLをブラウザで開く：
```
http://localhost:5000
```

### ステップ3: デモデータを作成（オプション）

別のターミナルで：
```bash
cd /Users/hikarunejikane/Downloads/STLINE-AI-Trainer
source venv/bin/activate
python demo.py create-data
```

これにより、3人のサンプルユーザーと45件のセッションデータが作成されます。

## 🎯 Webダッシュボードでできること

### 1. ダッシュボード（ホーム）
- **URL**: `http://localhost:5000/`
- 全体統計の表示
- 最近のセッション一覧
- システム概要

### 2. ユーザー管理
- **URL**: `http://localhost:5000/users`
- 登録ユーザー一覧
- 新規ユーザー登録
- ユーザー詳細表示

### 3. 新規ユーザー登録
- **URL**: `http://localhost:5000/add_user`
- ユーザー情報の入力
- フィットネスレベルの設定
- 目標の設定

### 4. ユーザー詳細
- **URL**: `http://localhost:5000/user/<user_id>`
- 例: `http://localhost:5000/user/user001`
- 過去30日の統計
- セッション履歴
- 改善提案

### 5. 運動メニュー
- **URL**: `http://localhost:5000/exercises`
- 利用可能な運動の一覧
- 各運動の詳細情報

## 🔧 トラブルシューティング

### Webダッシュボードが起動しない

```bash
# ポート5000が使用中か確認
lsof -ti:5000

# 使用中のプロセスを停止
lsof -ti:5000 | xargs kill -9

# 再度起動
source venv/bin/activate
python gym_dashboard.py
```

### 別のポートで起動したい

`gym_dashboard.py`の最後の行を編集：
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # ポートを変更
```

## 📱 アクセス方法

### 同じマシンから
```
http://localhost:5000
```

### 同じネットワーク内の他のデバイスから
```
http://<あなたのMacのIPアドレス>:5000
```

IPアドレスの確認方法：
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

## 🚀 本番環境への展開

### Dockerを使用

```bash
# イメージをビルド
docker build -t stline-ai-trainer .

# コンテナを起動
docker run -d -p 5000:5000 --env-file .env --name stline-dashboard stline-ai-trainer
```

### Docker Composeを使用

```bash
docker-compose up -d
```

### クラウドに展開

詳細は `DEPLOYMENT_GUIDE.md` を参照してください。

## 📝 クイックスタートコマンド

```bash
# 1. 仮想環境を有効化
source venv/bin/activate

# 2. Webダッシュボードを起動
python gym_dashboard.py

# 3. ブラウザで以下にアクセス
# http://localhost:5000
```

## 🎉 まとめ

**今すぐ使用開始:**

1. ターミナルで以下を実行：
   ```bash
   source venv/bin/activate
   python gym_dashboard.py
   ```

2. ブラウザで以下にアクセス：
   ```
   http://localhost:5000
   ```

3. Webダッシュボードで以下を確認：
   - ダッシュボード（統計）
   - ユーザー管理
   - 運動メニュー

**準備完了！今すぐ使用できます！**

