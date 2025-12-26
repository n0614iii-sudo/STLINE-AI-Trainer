# 🌐 STLINE AI Trainer - アクセスURL

## ローカル環境

### Webダッシュボード

**メインURL:**
```
http://localhost:5000
```

### 各ページのURL

1. **ダッシュボード（ホーム）**
   ```
   http://localhost:5000/
   ```

2. **ユーザー一覧**
   ```
   http://localhost:5000/users
   ```

3. **新規ユーザー登録**
   ```
   http://localhost:5000/add_user
   ```

4. **ユーザー詳細**
   ```
   http://localhost:5000/user/<user_id>
   ```
   例: `http://localhost:5000/user/user001`

5. **運動メニュー**
   ```
   http://localhost:5000/exercises
   ```

6. **統計API**
   ```
   http://localhost:5000/api/stats
   ```

## 起動方法

```bash
cd /Users/hikarunejikane/Downloads/STLINE-AI-Trainer
source venv/bin/activate
python gym_dashboard.py
```

## 同じネットワーク内の他のデバイスからアクセス

1. MacのIPアドレスを確認:
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```

2. 他のデバイス（スマートフォン、タブレット、PC）のブラウザで:
   ```
   http://<MacのIPアドレス>:5000
   ```
   例: `http://192.168.1.100:5000`

## 本番環境

デプロイ先に応じてURLが変わります。詳細は `DEPLOYMENT_GUIDE.md` を参照してください。
