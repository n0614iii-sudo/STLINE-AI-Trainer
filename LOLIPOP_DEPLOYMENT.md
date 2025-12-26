# ロリポップサーバーへの展開ガイド

## ⚠️ ロリポップでの制限事項

ロリポップ（ロリポップ！レンタルサーバー）は主にPHP/WordPress向けのサービスで、Pythonアプリケーションの実行には以下の制限があります：

### 制限事項

1. **Python環境**
   - Python 3.10以上が利用できない可能性
   - カスタムパッケージのインストールに制限
   - `vision-agents`、`torch`などの大型パッケージはインストール困難

2. **依存関係**
   - 多くのPythonパッケージがインストールできない
   - GPU/CUDAは利用不可
   - システムレベルの依存関係に制限

3. **実行環境**
   - 長時間実行プロセスに制限
   - WebSocket/リアルタイム通信に制限
   - メモリ・CPU制限

## ✅ 推奨される展開方法

### オプション1: VPSサーバー（推奨）

ロリポップの代わりに、VPSサーバーを使用することを強く推奨します。

#### 日本のVPSサービス

1. **ConoHa VPS**
   - 月額500円〜
   - Ubuntu/Debian対応
   - 完全なrootアクセス
   - **推奨プラン**: 1GB RAM以上

2. **さくらのVPS**
   - 月額500円〜
   - 安定性が高い
   - 完全なrootアクセス

3. **AWS Lightsail**
   - 月額$3.50〜（約500円）
   - グローバル展開可能
   - スケーラブル

#### VPS展開手順

```bash
# 1. VPSサーバーにSSH接続
ssh root@your-server-ip

# 2. システム更新
apt update && apt upgrade -y

# 3. Python 3.11をインストール
apt install python3.11 python3.11-venv python3-pip -y

# 4. プロジェクトをアップロード
# (Git、SCP、FTPなどでアップロード)

# 5. 仮想環境を作成
python3.11 -m venv venv
source venv/bin/activate

# 6. 依存関係をインストール
pip install -r requirements.txt

# 7. 環境変数を設定
nano .env

# 8. 起動（systemdサービスとして）
# (後述の手順を参照)
```

### オプション2: Railway / Render（簡単）

PaaSサービスを使用すると、簡単にデプロイできます。

#### Railway

```bash
# 1. Railway CLIをインストール
npm i -g @railway/cli

# 2. ログイン
railway login

# 3. プロジェクトを初期化
railway init

# 4. 環境変数を設定
railway variables set GEMINI_API_KEY=your_key
railway variables set STREAM_API_KEY=your_key
railway variables set STREAM_API_SECRET=your_secret

# 5. デプロイ
railway up
```

#### Render

1. GitHubにリポジトリをプッシュ
2. Renderで「New Web Service」を選択
3. リポジトリを選択
4. 環境変数を設定
5. デプロイ

### オプション3: Docker + VPS

Dockerを使用してVPSに展開：

```bash
# VPSサーバーで
docker-compose up -d
```

## 🔄 ロリポップで可能な場合の方法

もしロリポップの上位プランでPythonが利用可能な場合：

### 手順

1. **SSHアクセスの確認**
   - ロリポップの管理画面でSSHアクセスを有効化

2. **Python環境の確認**
   ```bash
   ssh your-account@lolipop-server
   python3 --version
   ```

3. **プロジェクトのアップロード**
   - FTPまたはSCPでファイルをアップロード

4. **依存関係のインストール**
   ```bash
   pip3 install --user -r requirements.txt
   ```

5. **起動**
   ```bash
   python3 gym_dashboard.py
   ```

**注意**: ロリポップでは多くの制限があるため、正常に動作しない可能性が高いです。

## 🎯 最適な展開方法の推奨

### 推奨順位

1. **ConoHa VPS / さくらのVPS** ⭐⭐⭐
   - コスト: 月額500円〜
   - 完全な制御が可能
   - すべての機能が動作

2. **Railway / Render** ⭐⭐
   - コスト: 無料プランあり
   - 簡単にデプロイ可能
   - 一部機能に制限

3. **AWS Lightsail** ⭐⭐
   - コスト: 月額$3.50〜
   - スケーラブル
   - グローバル展開可能

4. **ロリポップ** ⚠️
   - 制限が多く、正常動作が困難

## 📝 具体的な展開手順（VPS推奨）

詳細な手順は `VPS_DEPLOYMENT.md` を参照してください。

