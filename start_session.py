#!/usr/bin/env python3
"""
実際のトレーニングセッションを開始するスクリプト
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from personal_gym_trainer import PersonalGymTrainer, UserProfile

load_dotenv()


async def start_training_session(user_id: str, exercise_type: str):
    """トレーニングセッションを開始"""
    print("=" * 60)
    print("STLINE AI Trainer - トレーニングセッション開始")
    print("=" * 60)
    print()
    
    # トレーナーを初期化
    trainer = PersonalGymTrainer()
    trainer.load_config()
    
    # ユーザーを確認
    if user_id not in trainer.user_profiles:
        print(f"❌ ユーザー '{user_id}' が見つかりません")
        print("\n利用可能なユーザー:")
        for uid, user in trainer.user_profiles.items():
            print(f"  - {uid}: {user.name}")
        return
    
    user = trainer.user_profiles[user_id]
    print(f"👤 ユーザー: {user.name}")
    print(f"📊 レベル: {user.fitness_level}")
    print(f"🎯 目標: {', '.join(user.target_goals)}")
    print()
    
    # 運動タイプを確認
    if exercise_type not in trainer.exercise_database:
        print(f"❌ 運動タイプ '{exercise_type}' が見つかりません")
        print("\n利用可能な運動:")
        for ex_id, ex_info in trainer.exercise_database.items():
            print(f"  - {ex_id}: {ex_info['name']}")
        return
    
    exercise_info = trainer.exercise_database[exercise_type]
    print(f"💪 運動: {exercise_info['name']}")
    print(f"🎯 対象筋群: {', '.join(exercise_info['target_muscles'])}")
    print()
    
    # Agentを作成
    print("🤖 AIトレーナーを初期化中...")
    try:
        agent = await trainer.create_agent(user)
        print("✅ AIトレーナー準備完了")
    except Exception as e:
        print(f"❌ AIトレーナー初期化エラー: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # セッション開始
    print("\n" + "=" * 60)
    print("セッション開始")
    print("=" * 60)
    print()
    print("注意: 実際のビデオ通話を開始するには、以下が必要です:")
    print("  1. Webカメラとマイクが接続されていること")
    print("  2. ブラウザでビデオ通話を開始すること")
    print()
    print("現在は基本的なセッション管理のみテストします。")
    print()
    
    # ワークアウトセッション開始
    session = trainer.start_workout_session(user_id, exercise_type)
    print(f"✅ ワークアウトセッション開始")
    print(f"   - 開始時刻: {session.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   - 運動: {exercise_info['name']}")
    print()
    
    # Callを作成（テスト用）
    try:
        call_type = "default"
        call_id = f"session_{user_id}_{session.start_time.strftime('%Y%m%d%H%M%S')}"
        print(f"📞 Call作成中: {call_id}")
        call = await agent.create_call(call_type, call_id)
        print("✅ Call作成成功")
        print()
        print("実際のビデオ通話を開始するには:")
        print(f"  1. Stream APIを使用してCallに参加")
        print(f"  2. WebRTCを使用してビデオ/オーディオストリームを開始")
        print()
    except Exception as e:
        print(f"⚠️  Call作成エラー（続行）: {e}")
        print()
    
    # セッション終了
    print("セッションを終了しますか？ (y/n): ", end="")
    try:
        response = input().strip().lower()
        if response == 'y':
            completed_session = trainer.end_workout_session()
            if completed_session:
                print("\n✅ セッション終了")
                print(f"   - 回数: {completed_session.rep_count}回")
                print(f"   - 消費カロリー: {completed_session.calories_burned:.1f}kcal")
                print(f"   - フォームスコア: {completed_session.form_score:.1f}/1.0")
                
                # 設定を保存
                trainer.save_config()
                print("\n💾 データを保存しました")
        else:
            print("セッションは継続中です。")
    except KeyboardInterrupt:
        print("\n\nセッションを中断しました。")
        completed_session = trainer.end_workout_session()
        trainer.save_config()


async def main():
    """メイン関数"""
    if len(sys.argv) < 3:
        print("使用方法:")
        print("  python start_session.py <user_id> <exercise_type>")
        print()
        print("例:")
        print("  python start_session.py user001 squat")
        print("  python start_session.py user001 push_up")
        print()
        print("利用可能な運動:")
        print("  - squat (スクワット)")
        print("  - push_up (腕立て伏せ)")
        print("  - deadlift (デッドリフト)")
        print("  - plank (プランク)")
        return
    
    user_id = sys.argv[1]
    exercise_type = sys.argv[2]
    
    await start_training_session(user_id, exercise_type)


if __name__ == "__main__":
    asyncio.run(main())

