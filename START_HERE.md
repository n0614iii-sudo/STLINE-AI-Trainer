# 🚀 STLINE AI Trainer - スタートガイド

## ✅ セットアップ完了！

システムは基本的に動作する状態になっています。

## 🎯 今すぐ使用できる機能

### 1. Webダッシュボード（完全動作）

```bash
source venv/bin/activate
python gym_dashboard.py
```

**ブラウザで `http://localhost:5000` にアクセス**

**使用可能な機能:**
- ✅ ユーザー登録・管理
- ✅ トレーニング履歴表示
- ✅ 統計表示
- ✅ 運動メニュー一覧

### 2. デモデータの作成

```bash
source venv/bin/activate
python demo.py create-data
```

これにより、3人のサンプルユーザーと45件のセッションデータが作成されます。

### 3. 基本的なセッション管理

```bash
source venv/bin/activate
python start_session.py <user_id> <exercise_type>
```

例:
```bash
python start_session.py user001 squat
```

## 📊 現在の動作状況

### ✅ 完全に動作する機能

1. **Webダッシュボード** - すべての機能が使用可能
2. **ユーザー管理** - 登録、一覧、詳細表示
3. **セッション管理** - 開始、終了、データ記録
4. **統計表示** - 各種統計の計算と表示
5. **Agent作成** - StreamEdgeの完全実装で成功

### ⚠️ 制限事項

1. **Stream API認証**
   - 実際のCall作成には追加設定が必要
   - 基本的な機能は動作

2. **ビデオ通話機能**
   - 基本的な構造は完成
   - 実際のWebRTC接続には追加実装が必要

3. **姿勢検出**
   - YOLOPoseProcessorプラグインが必要
   - 現在は代替実装を使用

## 🎬 クイックスタート

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

## 📝 使用例

### 例1: 新規ユーザーを登録

1. Webダッシュボードで「新規ユーザー登録」をクリック
2. 以下を入力:
   - ユーザーID: `user001`
   - 名前: `テスト太郎`
   - フィットネスレベル: `初心者`
   - 目標: `体重減少`
3. 「登録」をクリック

### 例2: ユーザーの統計を確認

1. 「ユーザー管理」をクリック
2. ユーザーを選択
3. 詳細ページで統計を確認

### 例3: デモデータで統計を確認

1. `python demo.py create-data` を実行
2. Webダッシュボードで統計を確認
3. 各ユーザーの詳細を確認

## 🔧 トラブルシューティング

### Webダッシュボードが起動しない

```bash
# ポート5000が使用中の場合
lsof -ti:5000 | xargs kill -9

# 再度起動
python gym_dashboard.py
```

### デモデータが作成されない

```bash
# 仮想環境が有効化されているか確認
which python
# venv/bin/python と表示されればOK

# 再度実行
python demo.py create-data
```

## 📚 詳細ドキュメント

- `ACTUAL_USAGE.md` - 実際の使用方法の詳細
- `USAGE_GUIDE.md` - 使用ガイド
- `README_USAGE.md` - 使用説明書
- `SOLUTION_SUMMARY.md` - 解決策のまとめ

## 🎉 次のステップ

1. **Webダッシュボードを使用**
   - ユーザー登録
   - データ確認
   - 統計分析

2. **基本的な機能をテスト**
   - セッション管理
   - データ記録

3. **今後の拡張**
   - Stream API認証の修正
   - ビデオ通話機能の実装
   - 姿勢検出機能の追加

---

**準備完了！Webダッシュボードを起動して使用を開始してください！**

