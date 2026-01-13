# 🏗️ Railway Architecture設定ガイド

## 📋 Architecture設定について

RailwayでArchitecture設定が見えない場合の対処法です。

## 🔍 確認方法

### 方法1: RailwayのSettingsで確認

1. **Railwayのダッシュボードを開く**
   - https://railway.app/ にアクセス
   - プロジェクトを選択

2. **Settingsタブを開く**
   - プロジェクトのダッシュボードで「Settings」をクリック

3. **Build & Deployセクションを確認**
   - 左側のメニューから「Build & Deploy」をクリック
   - または、Settingsページ内で「Build & Deploy」セクションを探す

4. **Architecture設定を確認**
   - 「Architecture」または「Platform」という項目があるか確認
   - 通常は「amd64」または「linux/amd64」が表示されます

### 方法2: railway.jsonで設定

`railway.json`ファイルにArchitecture設定を追加できます：

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile",
    "arch": "amd64"
  },
  "deploy": {
    "startCommand": "python gym_dashboard.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

## 🎯 推奨設定

### CPUアーキテクチャ

- **amd64** (x86_64): 通常のサーバー用（推奨）
- **arm64**: ARMベースのサーバー用（Apple Siliconなど）

### 現在のプロジェクト

このプロジェクトは **amd64** を使用しています（CPU版のPyTorchを使用しているため）。

## 🔧 設定方法

### オプション1: railway.jsonで設定（推奨）

1. **railway.jsonを編集**
   ```json
   {
     "build": {
       "builder": "DOCKERFILE",
       "dockerfilePath": "Dockerfile",
       "arch": "amd64"
     }
   }
   ```

2. **GitHubにプッシュ**
   ```bash
   git add railway.json
   git commit -m "Add architecture setting to railway.json"
   git push
   ```

3. **Railwayで再デプロイ**
   - Railwayが自動的に再デプロイを開始します

### オプション2: RailwayのUIで設定

1. **Settings → Build & Deploy** を開く
2. **Architecture** または **Platform** セクションを探す
3. **amd64** を選択
4. **Save** をクリック

## ⚠️ 注意事項

### Architecture設定が表示されない場合

Railwayの新しいUIでは、Architecture設定が自動的に検出される場合があります：

1. **Dockerfileがある場合**
   - Railwayは自動的にDockerfileを検出
   - Architectureは自動的に設定されます

2. **railway.jsonがある場合**
   - railway.jsonの設定が優先されます

3. **どちらもない場合**
   - Railwayは自動的に最適なArchitectureを選択します

## 🔍 トラブルシューティング

### Architecture設定が見えない場合

1. **railway.jsonを確認**
   - プロジェクトのルートに`railway.json`があるか確認
   - 正しい形式になっているか確認

2. **Dockerfileを確認**
   - Dockerfileが存在するか確認
   - 正しい形式になっているか確認

3. **Railwayのログを確認**
   - Deploymentsタブで最新のデプロイメントを確認
   - エラーメッセージがないか確認

### ビルドエラーが発生する場合

1. **Architectureの不一致を確認**
   - Dockerfileで指定されているArchitectureと一致しているか確認

2. **依存関係を確認**
   - CPU版のPyTorchを使用しているか確認（requirements.txt）

## 📝 現在の設定

このプロジェクトでは：

- **Builder**: DOCKERFILE
- **Dockerfile**: Dockerfile
- **Architecture**: amd64（自動検出）
- **Platform**: linux/amd64

## 🎯 まとめ

1. **railway.jsonで設定**（推奨）
   - `"arch": "amd64"` を追加

2. **GitHubにプッシュ**
   - 変更をコミットしてプッシュ

3. **Railwayで再デプロイ**
   - 自動的に再デプロイされます

Architecture設定は通常、自動的に検出されるため、明示的に設定する必要はありません。もし問題が発生する場合は、`railway.json`に明示的に設定してください。



