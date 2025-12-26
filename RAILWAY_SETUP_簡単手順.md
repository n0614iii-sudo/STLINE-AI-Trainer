# 🚀 Railwayデプロイ設定 - 簡単手順

## 📋 ステップバイステップ

### ステップ1: Railwayにアクセス

1. **Railwayのサイトを開く**
   - https://railway.app/ にアクセス
   - 「Start a New Project」または「Login」をクリック

2. **GitHubでログイン**
   - 「Login with GitHub」をクリック
   - GitHubの認証を許可

### ステップ2: プロジェクトを作成

1. **新しいプロジェクトを作成**
   - 「New Project」をクリック
   - 「Deploy from GitHub repo」を選択

2. **リポジトリを選択**
   - `n0614iii-sudo/STLINE-AI-Trainer` を選択
   - Railwayが自動的にデプロイを開始します

### ステップ3: 環境変数を設定 ⚠️ 重要

1. **Settingsタブを開く**
   - プロジェクトのダッシュボードで「Settings」をクリック

2. **Variablesセクションを開く**
   - 左側のメニューから「Variables」をクリック
   - または「Environment Variables」をクリック

3. **環境変数を追加**
   
   以下の環境変数を追加してください：

   | 変数名 | 説明 | 例 |
   |--------|------|-----|
   | `GEMINI_API_KEY` | Gemini APIキー | `AIza...` |
   | `STREAM_API_KEY` | Stream APIキー | `your-stream-key` |
   | `STREAM_API_SECRET` | Stream API Secret | `your-stream-secret` |
   | `FLASK_SECRET_KEY` | Flaskの秘密鍵（任意） | `your-secret-key` |

   **追加方法:**
   - 「+ New Variable」をクリック
   - 変数名を入力
   - 値を入力
   - 「Add」をクリック

### ステップ4: ネットワーク設定

1. **Networkingセクションを開く**
   - Settings → Networking

2. **ポートを確認**
   - 「Enter the port your app is listening on」が **空欄** または **5000** になっているか確認
   - Railwayが自動的に `PORT` 環境変数を設定するので、空欄のままでOK

3. **ドメインを生成**
   - 「Generate Domain」ボタンをクリック
   - Railwayが自動的にURLを生成します
   - 例: `https://stline-ai-trainer-production.up.railway.app`

### ステップ5: デプロイの確認

1. **Deploymentsタブを確認**
   - デプロイの進行状況を確認
   - 「Building...」→「Deploying...」→「Active」になるまで待つ

2. **Logsタブで確認**
   - 「Logs」タブを開く
   - エラーがないか確認
   - 以下のようなメッセージが表示されれば成功：
     ```
     🌐 パーソナルジム管理ダッシュボード起動
     http://0.0.0.0:5000 でアクセスできます
     ```

### ステップ6: アプリケーションにアクセス

1. **生成されたURLをコピー**
   - Settings → Networking で表示されているURL
   - または、プロジェクトのダッシュボードの上部に表示されているURL

2. **ブラウザでアクセス**
   - コピーしたURLをブラウザで開く
   - ダッシュボードが表示されれば成功！

## ✅ 確認チェックリスト

- [ ] RailwayにGitHubでログインした
- [ ] リポジトリを選択してプロジェクトを作成した
- [ ] 環境変数を設定した（GEMINI_API_KEY, STREAM_API_KEY, STREAM_API_SECRET）
- [ ] ドメインを生成した
- [ ] デプロイが完了した（Active状態）
- [ ] アプリケーションにアクセスできた

## 🔧 トラブルシューティング

### デプロイが失敗する場合

1. **Logsタブを確認**
   - エラーメッセージを確認
   - よくあるエラー：
     - 環境変数が設定されていない
     - 依存関係のインストールエラー

2. **環境変数を再確認**
   - Settings → Variables で正しく設定されているか確認
   - 値に余分なスペースがないか確認

### アプリケーションにアクセスできない場合

1. **ドメインが生成されているか確認**
   - Settings → Networking でドメインが表示されているか

2. **デプロイが完了しているか確認**
   - Deploymentsタブで「Active」になっているか

3. **数分待つ**
   - デプロイ直後は数分かかる場合があります

## 📝 重要なポイント

1. **環境変数は必須**
   - GEMINI_API_KEY、STREAM_API_KEY、STREAM_API_SECRETは必須です
   - 設定しないとアプリケーションが起動しません

2. **デプロイには時間がかかる**
   - 初回デプロイは5-10分かかることがあります
   - 依存関係のインストールに時間がかかります

3. **自動デプロイ**
   - GitHubにプッシュすると、自動的に再デプロイされます
   - 手動で再デプロイする場合は、Deploymentsタブで「Redeploy」をクリック

## 🎯 次のステップ

デプロイが完了したら：

1. **アプリケーションをテスト**
   - ダッシュボードにアクセス
   - ユーザー登録をテスト
   - 姿勢診断をテスト

2. **カスタムドメインを設定（オプション）**
   - Settings → Networking → Custom Domain
   - 独自のドメインを設定できます

3. **モニタリング**
   - Logsタブでアプリケーションのログを確認
   - Metricsタブでリソース使用状況を確認

## 🎉 完了！

これでRailwayでのデプロイが完了しました！

アクセスURL: `https://your-app.railway.app`

