#!/usr/bin/env python3
"""
簡単なセットアップ確認スクリプト
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def check_setup():
    """セットアップ状況を確認"""
    print("=" * 60)
    print("STLINE AI Trainer - セットアップ確認")
    print("=" * 60)
    print()
    
    # .envファイルの確認
    env_path = Path(".env")
    if env_path.exists():
        print("✅ .envファイルが存在します")
        load_dotenv()
    else:
        print("❌ .envファイルが見つかりません")
        print("   python3 setup_api_keys.py を実行してAPIキーを設定してください")
        return False
    
    # APIキーの確認
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    stream_key = os.getenv("STREAM_API_KEY", "")
    stream_secret = os.getenv("STREAM_API_SECRET", "")
    
    print()
    print("APIキーの設定状況:")
    
    if gemini_key and gemini_key != "your_gemini_api_key_here":
        print(f"  ✅ GEMINI_API_KEY: {gemini_key[:15]}...")
    else:
        print("  ❌ GEMINI_API_KEY: 未設定")
    
    if stream_key and stream_key != "your_stream_api_key_here":
        print(f"  ✅ STREAM_API_KEY: {stream_key[:15]}...")
    else:
        print("  ❌ STREAM_API_KEY: 未設定")
    
    if stream_secret and stream_secret != "your_stream_api_secret_here":
        print(f"  ✅ STREAM_API_SECRET: {stream_secret[:15]}...")
    else:
        print("  ❌ STREAM_API_SECRET: 未設定")
    
    print()
    
    # 依存関係の確認
    print("依存関係の確認:")
    required_packages = [
        "vision_agents",
        "flask",
        "dotenv",
        "ultralytics",
        "opencv-python",
        "torch"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == "dotenv":
                __import__("dotenv")
            elif package == "opencv-python":
                __import__("cv2")
            else:
                __import__(package.replace("-", "_"))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} (未インストール)")
            missing_packages.append(package)
    
    print()
    
    if missing_packages:
        print("⚠️  以下のパッケージをインストールしてください:")
        print(f"   pip install {' '.join(missing_packages)}")
        print()
    
    # 最終確認
    all_set = (
        gemini_key and gemini_key != "your_gemini_api_key_here" and
        stream_key and stream_key != "your_stream_api_key_here" and
        stream_secret and stream_secret != "your_stream_api_secret_here" and
        len(missing_packages) == 0
    )
    
    if all_set:
        print("=" * 60)
        print("✅ セットアップ完了！")
        print("=" * 60)
        print()
        print("次のステップ:")
        print("  1. python3 demo.py create-data  # デモデータ作成（オプション）")
        print("  2. python3 gym_dashboard.py    # Webダッシュボード起動")
        print("  3. python3 personal_gym_trainer.py  # AIトレーナー起動")
        return True
    else:
        print("=" * 60)
        print("⚠️  セットアップが完了していません")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = check_setup()
    sys.exit(0 if success else 1)

