# 🚀 クイック展開ガイド

## ⚠️ ロリポップについて

**ロリポップは使用できません。** Python 3.10以上と多くの依存関係が必要なため、ロリポップでは動作しません。

## ✅ 推奨展開方法

### 1. Railway（最も簡単）⭐

**URL**: https://railway.app/

**手順:**
1. GitHubにリポジトリをプッシュ
2. Railwayで「New Project」→ GitHubを選択
3. 環境変数を設定
4. デプロイ完了

**アクセスURL**: `https://your-app.railway.app`

### 2. ConoHa VPS（推奨）⭐⭐⭐

**URL**: https://www.conoha.jp/
**価格**: 月額500円〜

**手順:**
```bash
# ローカルマシンで
./deploy_to_vps.sh your-server-ip
```

**アクセスURL**: `http://your-server-ip:5000`

### 3. さくらのVPS

**URL**: https://vps.sakura.ad.jp/
**価格**: 月額500円〜

詳細は `VPS_DEPLOYMENT.md` を参照

## 🎯 今すぐ展開する方法

### Railwayを使用（推奨）

1. **GitHubにプッシュ**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/your-username/STLINE-AI-Trainer.git
   git push -u origin main
   ```

2. **Railwayで展開**
   - https://railway.app/ にアクセス
   - 「New Project」→ GitHubを選択
   - リポジトリを選択
   - 環境変数を設定
   - デプロイ

3. **アクセス**
   - Railwayが自動的にURLを生成
   - 例: `https://stline-ai-trainer.railway.app`

### VPSを使用

1. **VPSサーバーを作成**（ConoHaまたはさくら）
2. **展開スクリプトを実行**
   ```bash
   ./deploy_to_vps.sh your-server-ip
   ```
3. **アクセス**
   ```
   http://your-server-ip:5000
   ```

## 📝 詳細ドキュメント

- `PRODUCTION_DEPLOYMENT.md` - 本番環境展開の詳細
- `VPS_DEPLOYMENT.md` - VPS展開の詳細手順
- `DEPLOYMENT_GUIDE.md` - 全般的な展開ガイド
