#!/usr/bin/env python3
"""
APIキー設定スクリプト
セキュアにAPIキーを.envファイルに設定します
"""

import os
from pathlib import Path

def setup_api_keys():
    """APIキーを対話的に設定"""
    env_path = Path(".env")
    
    print("=" * 60)
    print("STLINE AI Trainer - APIキー設定")
    print("=" * 60)
    print()
    
    # 既存の.envファイルを読み込み（存在する場合）
    existing_keys = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    if value and value != f"your_{key.lower()}_here":
                        existing_keys[key] = value
    
    # Gemini APIキー
    print("1. Gemini APIキーを入力してください")
    if 'GEMINI_API_KEY' in existing_keys:
        print(f"   (現在の値: {existing_keys['GEMINI_API_KEY'][:10]}...)")
        use_existing = input("   既存の値を使用しますか？ (y/n): ").lower()
        if use_existing == 'y':
            gemini_key = existing_keys['GEMINI_API_KEY']
        else:
            gemini_key = input("   Gemini APIキー: ").strip()
    else:
        gemini_key = input("   Gemini APIキー: ").strip()
    
    print()
    
    # Stream APIキー
    print("2. Stream APIキーを入力してください")
    if 'STREAM_API_KEY' in existing_keys:
        print(f"   (現在の値: {existing_keys['STREAM_API_KEY'][:10]}...)")
        use_existing = input("   既存の値を使用しますか？ (y/n): ").lower()
        if use_existing == 'y':
            stream_key = existing_keys['STREAM_API_KEY']
        else:
            stream_key = input("   Stream APIキー: ").strip()
    else:
        stream_key = input("   Stream APIキー: ").strip()
    
    print()
    
    # Stream API Secret
    print("3. Stream API Secretを入力してください")
    if 'STREAM_API_SECRET' in existing_keys:
        print(f"   (現在の値: {existing_keys['STREAM_API_SECRET'][:10]}...)")
        use_existing = input("   既存の値を使用しますか？ (y/n): ").lower()
        if use_existing == 'y':
            stream_secret = existing_keys['STREAM_API_SECRET']
        else:
            stream_secret = input("   Stream API Secret: ").strip()
    else:
        stream_secret = input("   Stream API Secret: ").strip()
    
    print()
    
    # 確認
    print("設定内容:")
    print(f"  GEMINI_API_KEY: {gemini_key[:10]}..." if gemini_key else "  (未設定)")
    print(f"  STREAM_API_KEY: {stream_key[:10]}..." if stream_key else "  (未設定)")
    print(f"  STREAM_API_SECRET: {stream_secret[:10]}..." if stream_secret else "  (未設定)")
    print()
    
    confirm = input("この設定で保存しますか？ (y/n): ").lower()
    
    if confirm != 'y':
        print("キャンセルされました。")
        return
    
    # .envファイルに書き込み
    env_content = f"""# STLINE AI Personal Trainer - 環境変数設定ファイル
# このファイルは自動生成されました

# Gemini API キー（必須）
GEMINI_API_KEY={AIzaSyAoGJCxfhUO6G1aZ10iQvoaQbIa9iuwFvU}

# Stream API キー（必須）
STREAM_API_KEY={98yhwcjpzcpr}
STREAM_API_SECRET={x95fkr4rjrct7du3caujexugp3w5vr9yvdkug48k9x7s3qqjyje8q3f3s4627ftm}

# オプション設定
DEBUG=false
LOG_LEVEL=INFO
"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print()
    print("✅ APIキーを.envファイルに保存しました！")
    print()
    print("次のステップ:")
    print("  1. python gym_dashboard.py  # Webダッシュボードを起動")
    print("  2. python demo.py create-data  # デモデータを作成（オプション）")
    print("  3. python personal_gym_trainer.py  # AIトレーナーを起動")
    print()

if __name__ == "__main__":
    setup_api_keys()

