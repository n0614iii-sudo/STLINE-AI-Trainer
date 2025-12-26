# 🚀 STLINE AI Personal Trainer - クイックスタートガイド

**株式会社STLINE提供**  
**開発: HIKARU NEJIKANE**

---

## 📦 パッケージ内容

```
STLINE-AI-Trainer/
├── STLINE_README.md          # 製品詳細ドキュメント
├── QUICK_START.md            # このファイル
├── stline_config.py          # システム設定ファイル
├── personal_gym_trainer.py   # AIトレーナーメインシステム
├── gym_dashboard.py          # Web管理ダッシュボード
├── demo.py                   # デモ・テスト用スクリプト
├── requirements.txt          # Python依存関係
├── .env.example              # 環境変数テンプレート
└── templates/                # Webテンプレートファイル
    ├── stline_base.html      # STLINEブランドベーステンプレート
    ├── base.html             # 標準ベーステンプレート
    ├── dashboard.html        # ダッシュボード
    ├── users.html            # ユーザー管理
    ├── user_detail.html      # ユーザー詳細
    ├── add_user.html         # ユーザー登録
    └── exercises.html        # 運動メニュー
```

---

## ⚡ 5分でスタート

### Step 1: APIキー設定

#### 1.1 Gemini APIキー取得（必須）
1. https://ai.google.dev/ にアクセス
2. Googleアカウントでログイン
3. 「Get API Key」をクリック
4. APIキーをコピー

#### 1.2 Stream APIキー取得（必須）
1. https://getstream.io/ でアカウント作成
2. 無料プラン（333,000分）を選択
3. Dashboard → Keys から取得
4. API KeyとSecretをコピー

### Step 2: 環境設定

```bash
# .envファイル作成
cp .env.example .env

# .envファイルを編集（お好きなエディタで）
nano .env  # または vim, code など
```

**以下を設定：**
```bash
GEMINI_API_KEY=あなたのGemini APIキー
STREAM_API_KEY=あなたのStream APIキー
STREAM_API_SECRET=あなたのStream Secret
```

### Step 3: インストール

```bash
# Python仮想環境作成（推奨）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt
```

### Step 4: 起動

```bash
# ターミナル1: AIトレーナー起動
python personal_gym_trainer.py

# ターミナル2（別ウィンドウ）: Web管理画面起動
python gym_dashboard.py
```

### Step 5: アクセス

ブラウザで以下にアクセス：
```
http://localhost:5000
```

---

## 🎯 最初のトレーニング

### 1. ユーザー登録
1. Web画面で「新規ユーザー登録」をクリック
2. 以下を入力：
   - ユーザーID: `demo_user001`
   - 名前: `テスト太郎`
   - レベル: `初心者`
   - 目標: `体重減少`を選択
3. 「登録」をクリック

### 2. デモデータ作成（オプション）
```bash
python demo.py create-data
```
これにより、3人のサンプルユーザーと45件のセッションデータが自動生成されます。

### 3. セッション開始
1. ダッシュボードで「セッション開始」をクリック
2. ユーザーと運動（例：スクワット）を選択
3. 「セッション開始」をクリック
4. AIトレーナーとのビデオ通話が開始

### 4. トレーニング実施
- Webカメラに全身が映るように位置調整
- AIの音声指導に従ってトレーニング
- リアルタイムでフォーム修正指導を受ける

---

## 🔧 トラブルシューティング

### Pythonモジュールが見つからない
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Webカメラが認識されない
- カメラのアクセス許可を確認
- ブラウザの設定でカメラを許可
- 他のアプリでカメラが使用されていないか確認

### ポート5000が使用中
```bash
# 別のポートで起動
python gym_dashboard.py
# または、既存のプロセスを停止
lsof -ti:5000 | xargs kill -9  # macOS/Linux
```

### APIキーエラー
- `.env`ファイルが正しく設定されているか確認
- APIキーに余分なスペースがないか確認
- APIキーの有効期限を確認

### CUDAエラー（GPU関連）
```bash
# CPUモードで実行
# stline_config.py の AI_CONFIG を編集
"yolo_device": "cpu"
```

---

## 📱 動作確認

### システムチェック
```bash
python demo.py info
```

### ライセンスチェック
```bash
python stline_config.py
```

### AIセッションデモ
```bash
python demo.py ai-session
```

---

## 🎨 カスタマイズ

### ブランドカラー変更
`stline_config.py`の`BRAND_COLORS`を編集：
```python
BRAND_COLORS = {
    "primary": "#あなたの色",
    "secondary": "#あなたの色",
}
```

### 運動メニュー追加
`personal_gym_trainer.py`の`_load_exercise_database()`に追加

### 指導スタイル変更
`personal_gym_trainer.py`の`_generate_personalized_instructions()`を編集

---

## 📞 サポート

### 技術サポート
- **Email**: support@stline.co.jp
- **電話**: 03-XXXX-XXXX（平日10:00-18:00）
- **Web**: https://stline.co.jp/ai-trainer

### 緊急連絡先
重大なバグやセキュリティ問題：
- emergency@stline.co.jp

### よくある質問（FAQ）
https://stline.co.jp/ai-trainer/faq

---

## 📚 追加リソース

### ドキュメント
- [STLINE_README.md](STLINE_README.md) - 製品詳細
- [Vision Agents公式](https://visionagents.ai/)
- [YOLO11ドキュメント](https://docs.ultralytics.com/)

### チュートリアル動画
- https://stline.co.jp/ai-trainer/tutorials

### コミュニティ
- GitHub Discussions（準備中）
- Discordサーバー（準備中）

---

## 🔐 セキュリティ重要事項

### APIキー管理
- ⚠️ **APIキーを絶対に公開しないでください**
- Gitリポジトリに`.env`をコミットしない
- `.gitignore`に`.env`を追加
- 定期的にAPIキーをローテーション

### データ保護
- ユーザーデータはローカル保存
- 映像は処理後即座に破棄
- バックアップは暗号化推奨

---

## 📈 パフォーマンス最適化

### GPU使用（推奨）
NVIDIA GPUがある場合：
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### FPS調整
`stline_config.py`の`AI_CONFIG`：
```python
"default_fps": 5  # 低い値 = 低コスト、高い値 = 高精度
```

### メモリ最適化
大量ユーザー時：
```python
"enable_caching": True
"cache_ttl": 300
```

---

## 🚀 本番環境デプロイ

### 推奨環境
- Ubuntu Server 20.04 LTS
- 16GB RAM以上
- NVIDIA GPU（RTX 3060以上）
- SSD 100GB以上

### セキュリティ設定
```bash
# Firewall設定
sudo ufw allow 5000/tcp
sudo ufw enable

# SSL証明書設定（Let's Encrypt推奨）
# HTTPS化は必須
```

### プロセス管理
```bash
# Systemdサービス化
sudo systemctl enable stline-ai-trainer
sudo systemctl start stline-ai-trainer
```

---

## 📝 ライセンス情報

本ソフトウェアは**株式会社STLINE**の商用ライセンスのもとで提供されます。

### トライアル版
- 期間: 30日間
- 機能: 全機能利用可能
- ユーザー数: 10名まで

### 製品版
購入後、ライセンスキーを受け取ります：
```python
# stline_config.py の LICENSE_CONFIG を更新
"license_key": "あなたのライセンスキー"
"license_holder": "貴社名"
```

---

## 🎉 始めましょう！

```bash
# STLINEシステム起動バナー表示
python stline_config.py

# すべて準備完了！
python personal_gym_trainer.py
python gym_dashboard.py
```

**ブラウザでアクセス**: http://localhost:5000

---

**STLINE AI Personal Trainer System**  
*Designed by HIKARU NEJIKANE*  
*株式会社STLINE - 未来のフィットネスを、今日から*

Copyright © 2025 STLINE Corporation. All Rights Reserved.