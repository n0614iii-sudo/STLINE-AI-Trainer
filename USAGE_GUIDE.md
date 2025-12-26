# STLINE AI Trainer - 使用ガイド

## 🚀 クイックスタート

### 1. 環境準備

```bash
# 仮想環境を有効化
source venv/bin/activate

# APIキーが設定されているか確認
python test_setup.py
```

### 2. Webダッシュボードを起動

```bash
python gym_dashboard.py
```

ブラウザで `http://localhost:5000` にアクセス

### 3. 基本的な使用

#### デモデータの作成

```bash
python demo.py create-data
```

これにより、3人のサンプルユーザーと45件のセッションデータが作成されます。

#### ユーザー登録

1. Webダッシュボードで「新規ユーザー登録」をクリック
2. 必要情報を入力
3. 登録完了

#### トレーニングセッション開始

```bash
python start_session.py <user_id> <exercise_type>
```

例:
```bash
python start_session.py user001 squat
python start_session.py user001 push_up
```

## 📋 利用可能な機能

### ✅ 動作する機能

1. **Webダッシュボード**
   - ユーザー管理
   - トレーニング履歴表示
   - 統計表示
   - セッション管理

2. **基本的なセッション管理**
   - セッション開始/終了
   - データ記録
   - 統計計算

3. **Agent作成**
   - StreamEdgeの完全実装
   - Gemini Realtime LLM（基本実装）

### ⚠️ 制限事項

1. **ビデオ通話機能**
   - Stream APIのトークン生成が必要
   - 実際のWebRTC接続には追加実装が必要

2. **YOLOPoseProcessor**
   - プラグインが見つからない場合、姿勢検出機能は利用不可
   - 代替実装が必要

3. **Gemini Realtime API**
   - 基本実装のみ
   - 実際の音声応答には完全な実装が必要

## 🔧 トラブルシューティング

### Stream APIトークンエラー

```
Stream error code 5: GetOrCreateCall failed with error: "Token is invalid"
```

**解決方法:**
- Stream APIキーとSecretが正しく設定されているか確認
- `.env`ファイルの内容を確認

### プラグインが見つからない

```
WARNING: vision_agents.pluginsが見つかりません
```

**現在の状態:**
- 代替実装を使用しているため、基本的な機能は動作します
- 完全な機能には公式プラグインのインストールが必要

## 📝 次のステップ

1. **Stream APIトークンの修正**
   - JWTトークンの正しい生成方法を実装

2. **WebRTC接続の実装**
   - 実際のビデオ/オーディオストリームの処理

3. **YOLOPoseProcessorの実装**
   - 姿勢検出機能の追加

4. **Gemini Realtime APIの完全実装**
   - 実際の音声応答機能

## 💡 ヒント

- Webダッシュボードは完全に動作します
- 基本的なセッション管理機能は使用可能です
- 実際のビデオ通話機能は追加の実装が必要です

