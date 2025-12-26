# STLINE AI Trainer - 実際の使用方法

## 🎉 現在使用可能な機能

### ✅ 完全に動作する機能

1. **Webダッシュボード** - 完全動作
   ```bash
   source venv/bin/activate
   python gym_dashboard.py
   ```
   - ブラウザで `http://localhost:5000` にアクセス
   - ユーザー管理、履歴表示、統計表示が使用可能

2. **デモデータ作成**
   ```bash
   python demo.py create-data
   ```
   - 3人のサンプルユーザーと45件のセッションデータを作成

3. **基本的なセッション管理**
   - セッション開始/終了
   - データ記録
   - 統計計算

4. **Agent作成** - 成功
   - StreamEdgeの完全実装
   - 基本的な構造は完成

## 🚀 実際の使用手順

### ステップ1: Webダッシュボードを起動

```bash
cd /Users/hikarunejikane/Downloads/STLINE-AI-Trainer
source venv/bin/activate
python gym_dashboard.py
```

### ステップ2: ブラウザでアクセス

`http://localhost:5000` にアクセス

### ステップ3: デモデータを作成（オプション）

別のターミナルで:
```bash
source venv/bin/activate
python demo.py create-data
```

### ステップ4: Webダッシュボードで確認

- **ダッシュボード**: 全体統計を確認
- **ユーザー管理**: 登録されているユーザーを確認
- **ユーザー詳細**: 各ユーザーの統計を確認
- **運動メニュー**: 利用可能な運動を確認

## 📊 現在の動作状況

### ✅ 成功している項目

1. **Agent作成**: ✅ 成功
   - StreamEdgeの完全実装
   - Gemini Realtime LLM（基本実装）
   - すべての必要な属性が存在

2. **Webダッシュボード**: ✅ 完全動作
   - すべての機能が使用可能

3. **セッション管理**: ✅ 動作
   - セッション開始/終了
   - データ記録

### ⚠️ 制限事項

1. **Stream API認証**
   - 現在: サーバーサイド認証の設定が必要
   - 影響: 実際のCall作成には追加設定が必要
   - 回避策: Webダッシュボードでの基本機能は使用可能

2. **ビデオ通話機能**
   - 現在: 基本的な構造は完成
   - 必要: 実際のWebRTC接続の実装

3. **姿勢検出**
   - 現在: プラグインが見つからない
   - 必要: YOLOPoseProcessorの実装

## 💡 推奨される使用方法

### 今すぐ使用できること

1. **Webダッシュボード**
   - ユーザー登録・管理
   - トレーニング履歴の確認
   - 統計の表示・分析

2. **基本的なセッション管理**
   - セッションの開始/終了
   - データの記録

3. **システムの動作確認**
   - Agent作成のテスト
   - 基本的な機能の確認

### 今後の拡張

1. Stream APIの認証設定を修正
2. 実際のビデオ通話機能を実装
3. 姿勢検出機能を追加

## 📝 使用例

### 例1: Webダッシュボードでユーザーを登録

1. `python gym_dashboard.py` を起動
2. ブラウザで `http://localhost:5000` にアクセス
3. 「新規ユーザー登録」をクリック
4. 情報を入力して登録

### 例2: デモデータで統計を確認

1. `python demo.py create-data` を実行
2. Webダッシュボードで統計を確認
3. ユーザー詳細で各ユーザーの履歴を確認

### 例3: Agent作成のテスト

```bash
python test_agent.py
```

## 🔗 関連ファイル

- `gym_dashboard.py` - Webダッシュボード（✅ 完全動作）
- `personal_gym_trainer.py` - AIトレーナーシステム
- `stream_edge_complete.py` - StreamEdgeの完全実装
- `test_agent.py` - Agent動作テスト
- `demo.py` - デモデータ作成

