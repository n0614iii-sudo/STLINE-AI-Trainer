# STLINE AI Trainer - 動作確認チェックリスト

## ✅ 修正済みの問題

1. ✅ `.env.example`ファイルを作成
2. ✅ 環境変数の読み込みコードを追加（`python-dotenv`）
3. ✅ `vision_agents`のAPI使用を修正（エラーハンドリング追加）
4. ✅ 非同期コンテキストマネージャーの使用方法を修正

## ⚠️ 動作前に必要な設定

### 1. 環境変数の設定（必須）

```bash
# .envファイルを作成
cp .env.example .env

# .envファイルを編集して以下を設定：
# - GEMINI_API_KEY: https://ai.google.dev/ で取得
# - STREAM_API_KEY: https://getstream.io/ で取得
# - STREAM_API_SECRET: https://getstream.io/ で取得
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. YOLOモデルのダウンロード

初回起動時に自動ダウンロードされますが、手動で確認する場合：

```bash
# yolo11n-pose.ptが存在するか確認
ls -la yolo11n-pose.pt
```

## 🔍 動作確認手順

### Step 1: Webダッシュボードの起動確認

```bash
python gym_dashboard.py
```

**確認ポイント:**
- ✅ エラーなく起動する
- ✅ `http://localhost:5000` にアクセスできる
- ✅ ダッシュボードが表示される

### Step 2: デモデータの作成

```bash
python demo.py create-data
```

**確認ポイント:**
- ✅ エラーなく実行される
- ✅ `demo_gym_config.json`が作成される
- ✅ 3人のユーザーと45件のセッションデータが作成される

### Step 3: AIトレーナーの起動確認

```bash
python personal_gym_trainer.py
```

**確認ポイント:**
- ✅ エラーなく起動する
- ⚠️ APIキーが設定されていない場合はエラーが表示される（正常）
- ⚠️ 実際のセッション開始にはWebカメラとマイクが必要

## ⚠️ 既知の制限事項

### 1. vision_agents APIの依存

`vision_agents`パッケージの実際のAPIに依存します。以下の点で調整が必要な場合があります：

- `agent.join(call)`の戻り値の型
- `agent.llm.simple_response()`の有無
- `agent.finish()`の有無

現在のコードは、これらの違いに対応できるようエラーハンドリングを追加しています。

### 2. APIキーの必要性

以下のAPIキーが必要です：
- **Gemini API**: AIトレーナーの音声応答に使用
- **Stream API**: WebRTC通話機能に使用

### 3. ハードウェア要件

- Webカメラ（姿勢検出用）
- マイク（音声入力用）
- GPU（推奨、CPUでも動作可能）

## 🐛 トラブルシューティング

### エラー: "ModuleNotFoundError: No module named 'vision_agents'"

```bash
pip install vision-agents
```

### エラー: "API key not found"

`.env`ファイルにAPIキーが正しく設定されているか確認：

```bash
cat .env
```

### エラー: "Port 5000 already in use"

```bash
# 既存のプロセスを停止
lsof -ti:5000 | xargs kill -9  # macOS/Linux
```

または、`gym_dashboard.py`のポート番号を変更：

```python
app.run(debug=True, host='0.0.0.0', port=5001)  # 5001に変更
```

### CUDAエラー（GPU関連）

CPUモードで実行する場合、`stline_config.py`を編集：

```python
AI_CONFIG = {
    ...
    "yolo_device": "cpu",  # "cuda"から変更
}
```

## 📝 動作確認結果

実際に動作させる場合、以下を記録してください：

- [ ] Webダッシュボードが起動する
- [ ] デモデータが作成できる
- [ ] ユーザー登録ができる
- [ ] AIトレーナーが起動する（APIキー設定後）
- [ ] セッション開始ができる（カメラ・マイク接続後）

## 🔗 参考リンク

- [Vision Agents ドキュメント](https://visionagents.ai/)
- [Gemini API ドキュメント](https://ai.google.dev/docs)
- [Stream API ドキュメント](https://getstream.io/docs/)

