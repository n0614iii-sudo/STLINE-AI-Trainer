#!/usr/bin/env python3
"""
クイックテスト - 実際の使用例
"""

import asyncio
from personal_gym_trainer import PersonalGymTrainer, UserProfile
from dotenv import load_dotenv

load_dotenv()


async def quick_test():
    """クイックテスト"""
    print("=" * 60)
    print("STLINE AI Trainer - クイックテスト")
    print("=" * 60)
    print()
    
    # トレーナーを初期化
    trainer = PersonalGymTrainer()
    trainer.load_config()
    
    # デモデータが存在するか確認
    if not trainer.user_profiles:
        print("デモデータを作成しますか？ (y/n): ", end="")
        response = input().strip().lower()
        if response == 'y':
            from demo import create_demo_data
            await create_demo_data()
            trainer.load_config()
    
    if not trainer.user_profiles:
        print("ユーザーが登録されていません。")
        print("Webダッシュボードでユーザーを登録してください。")
        return
    
    # ユーザーを選択
    print("\n登録されているユーザー:")
    users = list(trainer.user_profiles.items())
    for i, (user_id, user) in enumerate(users, 1):
        print(f"  {i}. {user.name} ({user_id}) - {user.fitness_level}")
    
    print(f"\n{len(users)}人のユーザーが登録されています。")
    print("\n利用可能な運動:")
    for ex_id, ex_info in trainer.exercise_database.items():
        print(f"  - {ex_id}: {ex_info['name']}")
    
    print("\n" + "=" * 60)
    print("Webダッシュボードを使用する場合:")
    print("  python gym_dashboard.py")
    print("  ブラウザで http://localhost:5000 にアクセス")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(quick_test())

