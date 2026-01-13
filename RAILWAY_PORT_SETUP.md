# 🔧 Railwayポート設定ガイド

## ⚠️ 重要な設定

アプリケーションは**ポート5000**で動作**していますが、Railwayの設定では**8080**が表示されています。

## 🎯 正しい設定手順

### ステップ1: ポートを5000に変更

RailwayのSettingsページで：

1. **"Enter the port your app is listening on"** の入力欄を見つける
2. **8080** を **5000** に変更
3. **"Generate Domain"** ボタンをクリック

### ステップ2: ドメインを生成

1. ポートを5000に設定したら
2. **"Generate Domain"** ボタン（紫色のボタン）をクリック
3. Railwayが自動的にURLを生成します

例: `https://stline-ai-trainer.railway.app`

## 📋 確認事項

### アプリケーションのポート

`gym_dashboard.py`では、デフォルトでポート5000を使用しています：

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

### Railwayの環境変数でポートを設定（オプション）

もしポートを変更したい場合：

1. RailwayのSettings → Variables
2. 新しい環境変数を追加：
   - 名前: `PORT`
   - 値: `5000`

そして、`gym_dashboard.py`を修正：

```python
import os
port = int(os.getenv('PORT', 5000))
app.run(debug=False, host='0.0.0.0', port=port)
```

## 🚀 次のステップ

1. **ポートを5000に設定**
2. **"Generate Domain"をクリック**
3. **生成されたURLをコピー**
4. **ブラウザでアクセス**

## ✅ 完了後の確認

ドメインを生成したら：

1. 生成されたURLをコピー
2. ブラウザでアクセス
3. ダッシュボードが表示されれば成功！

例: `https://stline-ai-trainer.railway.app`

## 🔧 トラブルシューティング

### ポートが正しく設定されない場合

1. Settings → Variables で `PORT=5000` を設定
2. アプリケーションを再デプロイ

### ドメインが生成されない場合

1. ポートが正しく設定されているか確認（5000）
2. デプロイメントが完了しているか確認
3. 数秒待ってから再試行

## 🎯 まとめ

1. **ポートを8080から5000に変更**
2. **"Generate Domain"をクリック**
3. **生成されたURLでアクセス**

これでアプリケーションにアクセスできます！



