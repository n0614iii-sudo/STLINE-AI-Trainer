#!/usr/bin/env python3
"""
Agentの実際の動作テストスクリプト
"""

import asyncio
import os
from dotenv import load_dotenv
from personal_gym_trainer import PersonalGymTrainer, UserProfile

load_dotenv()


async def test_agent_creation():
    """Agent作成のテスト"""
    print("=" * 60)
    print("Agent作成テスト")
    print("=" * 60)
    
    trainer = PersonalGymTrainer()
    trainer.load_config()
    
    # テストユーザーを作成
    user = UserProfile(
        user_id="test_user_001",
        name="テストユーザー",
        fitness_level="beginner",
        target_goals=["weight_loss"],
        physical_limitations=[],
        preferred_language="ja"
    )
    trainer.add_user_profile(user)
    
    print(f"✅ ユーザー作成: {user.name}")
    
    # Agentを作成
    try:
        agent = await trainer.create_agent(user)
        print("✅ Agent作成成功！")
        print(f"   - edge型: {type(agent.edge).__name__}")
        print(f"   - llm型: {type(agent.llm).__name__}")
        print(f"   - processors数: {len(agent.processors) if agent.processors else 0}")
        
        return agent, trainer, user
    except Exception as e:
        print(f"❌ Agent作成エラー: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None


async def test_create_call(agent, trainer, user):
    """Call作成のテスト"""
    print("\n" + "=" * 60)
    print("Call作成テスト")
    print("=" * 60)
    
    try:
        # Callを作成
        call_type = "default"
        call_id = f"test_call_{user.user_id}"
        
        print(f"Call作成中: type={call_type}, id={call_id}")
        call = await agent.create_call(call_type, call_id)
        
        print("✅ Call作成成功！")
        print(f"   - Call型: {type(call).__name__}")
        print(f"   - Call ID: {call.id if hasattr(call, 'id') else 'N/A'}")
        
        return call
    except Exception as e:
        print(f"❌ Call作成エラー: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_workout_session(agent, trainer, user):
    """ワークアウトセッションのテスト"""
    print("\n" + "=" * 60)
    print("ワークアウトセッションテスト")
    print("=" * 60)
    
    exercise_type = "squat"
    
    # セッション開始
    session = trainer.start_workout_session(user.user_id, exercise_type)
    print(f"✅ セッション開始: {exercise_type}")
    print(f"   - 開始時刻: {session.start_time}")
    
    # セッション終了
    completed_session = trainer.end_workout_session()
    if completed_session:
        print("✅ セッション終了")
        print(f"   - 回数: {completed_session.rep_count}")
        print(f"   - カロリー: {completed_session.calories_burned:.1f}kcal")
        print(f"   - フォームスコア: {completed_session.form_score:.1f}/1.0")


async def main():
    """メインテスト"""
    print("\n" + "=" * 60)
    print("STLINE AI Trainer - 実際の動作テスト")
    print("=" * 60)
    print()
    
    # APIキーの確認
    gemini_key = os.getenv("GEMINI_API_KEY")
    stream_key = os.getenv("STREAM_API_KEY")
    stream_secret = os.getenv("STREAM_API_SECRET")
    
    print("APIキーの確認:")
    print(f"  ✅ GEMINI_API_KEY: {'設定済み' if gemini_key and gemini_key != 'your_gemini_api_key_here' else '❌ 未設定'}")
    print(f"  ✅ STREAM_API_KEY: {'設定済み' if stream_key and stream_key != 'your_stream_api_key_here' else '❌ 未設定'}")
    print(f"  ✅ STREAM_API_SECRET: {'設定済み' if stream_secret and stream_secret != 'your_stream_api_secret_here' else '❌ 未設定'}")
    print()
    
    if not all([gemini_key, stream_key, stream_secret]):
        print("⚠️  APIキーが設定されていません。.envファイルを確認してください。")
        return
    
    # Agent作成テスト
    agent, trainer, user = await test_agent_creation()
    if not agent:
        return
    
    # Call作成テスト
    call = await test_create_call(agent, trainer, user)
    
    # ワークアウトセッションテスト
    await test_workout_session(agent, trainer, user)
    
    print("\n" + "=" * 60)
    print("✅ すべてのテストが完了しました！")
    print("=" * 60)
    print()
    print("次のステップ:")
    print("  1. Webダッシュボードを起動: python gym_dashboard.py")
    print("  2. ブラウザで http://localhost:5000 にアクセス")
    print("  3. ユーザーを登録してセッションを開始")


if __name__ == "__main__":
    asyncio.run(main())

