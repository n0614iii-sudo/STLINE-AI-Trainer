# STLINE AI Trainer - セットアップガイド

## ⚠️ 重要な要件

このシステムは **Python 3.10以上** が必要です。

現在のPythonバージョン: `python3 --version` で確認してください。

## Python 3.10以上のインストール方法

### macOSの場合

#### 方法1: Homebrewを使用（推奨）

```bash
# Homebrewがインストールされていない場合
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python 3.11をインストール
brew install python@3.11

# パスを確認
which python3.11
```

#### 方法2: pyenvを使用（推奨）

```bash
# pyenvをインストール
brew install pyenv

# pyenvをシェルに追加（~/.zshrcまたは~/.bash_profile）
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc

# シェルを再読み込み
source ~/.zshrc

# Python 3.11をインストール
pyenv install 3.11.7

# プロジェクトディレクトリで使用
cd /Users/hikarunejikane/Downloads/STLINE-AI-Trainer
pyenv local 3.11.7
```

### 確認

```bash
python3.11 --version
# Python 3.11.x と表示されればOK
```

## セットアップ手順（Python 3.10以上がインストールされた後）

### 1. 仮想環境の作成

```bash
cd /Users/hikarunejikane/Downloads/STLINE-AI-Trainer

# Python 3.11を使用して仮想環境を作成
python3.11 -m venv venv

# 仮想環境を有効化
source venv/bin/activate

# 確認（プロンプトに(venv)が表示される）
which python
# venv/bin/python と表示されればOK
```

### 2. 依存関係のインストール

```bash
# pipをアップグレード
pip install --upgrade pip

# 依存関係をインストール
pip install -r requirements.txt
```

**注意**: インストールには数分かかる場合があります。特に`torch`と`ultralytics`は大きなパッケージです。

### 3. セットアップ確認

```bash
python test_setup.py
```

すべてのチェックが✅になれば完了です。

### 4. 動作確認

```bash
# デモデータ作成（オプション）
python demo.py create-data

# Webダッシュボード起動
python gym_dashboard.py
```

ブラウザで `http://localhost:5000` にアクセスしてください。

## トラブルシューティング

### Python 3.10以上が見つからない

```bash
# 利用可能なPythonバージョンを確認
ls -la /usr/local/bin/python*  # Homebrewでインストールした場合
ls -la ~/.pyenv/versions/       # pyenvでインストールした場合
```

### 仮想環境が作成できない

```bash
# python3.11が正しくインストールされているか確認
python3.11 --version

# パスが通っているか確認
which python3.11
```

### 依存関係のインストールエラー

```bash
# 仮想環境が有効化されているか確認
which python
# venv/bin/python と表示される必要がある

# pipをアップグレード
pip install --upgrade pip setuptools wheel

# 再度インストール
pip install -r requirements.txt
```

## 次のステップ

セットアップが完了したら：

1. ✅ APIキーが設定されている（`.env`ファイル）
2. ✅ Python 3.10以上がインストールされている
3. ✅ 仮想環境が作成・有効化されている
4. ✅ 依存関係がインストールされている
5. ✅ `test_setup.py`がすべて✅を表示

これらが完了したら、システムを使用できます！

