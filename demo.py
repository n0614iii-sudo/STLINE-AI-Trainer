#!/usr/bin/env python3
"""
パーソナルジムAIトレーナー - デモ・テスト用スクリプト
"""

import asyncio
import json
from pathlib import Path
from personal_gym_trainer import PersonalGymTrainer, UserProfile, WorkoutSession
import datetime

async def create_demo_data():
    """デモ用のサンプルデータを作成"""
    trainer = PersonalGymTrainer(config_path="demo_gym_config.json")
    
    print("🏋️‍♀️ パーソナルジムAIトレーナー - デモデータ作成")
    print("=" * 50)
    
    # サンプルユーザー作成
    users = [
        UserProfile(
            user_id="demo_beginner",
            name="田中太郎",
            fitness_level="beginner",
            target_goals=["weight_loss", "general_fitness"],
            physical_limitations=[],
            preferred_language="ja"
        ),
        UserProfile(
            user_id="demo_intermediate",
            name="佐藤花子",
            fitness_level="intermediate", 
            target_goals=["muscle_gain", "strength"],
            physical_limitations=["knee_issues"],
            preferred_language="ja"
        ),
        UserProfile(
            user_id="demo_advanced",
            name="鈴木一郎",
            fitness_level="advanced",
            target_goals=["strength", "endurance"],
            physical_limitations=[],
            preferred_language="ja"
        )
    ]
    
    # ユーザー登録
    for user in users:
        trainer.add_user_profile(user)
        print(f"✅ ユーザー登録完了: {user.name} ({user.fitness_level})")
    
    print("\n📊 サンプルセッションデータ作成中...")
    
    # サンプルセッションデータ作成
    for user in users:
        # 過去30日間のランダムなセッションを生成
        for i in range(15):  # 各ユーザー15セッション
            days_ago = 30 - (i * 2)
            session_time = datetime.datetime.now() - datetime.timedelta(days=days_ago, hours=2)
            
            # 運動タイプをレベルに応じて選択
            if user.fitness_level == "beginner":
                exercises = ["squat", "push_up"]
                max_reps = [12, 8]
            elif user.fitness_level == "intermediate":
                exercises = ["squat", "push_up", "plank"]
                max_reps = [15, 12, 45]  # プランクは秒数
            else:
                exercises = ["squat", "push_up", "deadlift", "plank"]
                max_reps = [20, 18, 12, 60]
            
            import random
            ex_idx = random.randint(0, len(exercises) - 1)
            exercise_type = exercises[ex_idx]
            
            # セッション作成
            session = WorkoutSession(
                user_id=user.user_id,
                exercise_type=exercise_type,
                start_time=session_time,
                end_time=session_time + datetime.timedelta(minutes=random.randint(10, 30))
            )
            
            # ランダムなパフォーマンスデータ
            base_reps = max_reps[ex_idx]
            variation = random.uniform(0.7, 1.2)
            session.rep_count = int(base_reps * variation)
            
            # フォームスコア（レベルに応じて調整）
            if user.fitness_level == "beginner":
                session.form_score = random.uniform(0.5, 0.8)
            elif user.fitness_level == "intermediate":
                session.form_score = random.uniform(0.7, 0.9)
            else:
                session.form_score = random.uniform(0.8, 1.0)
            
            # カロリー計算
            exercise_info = trainer.exercise_database.get(exercise_type, {})
            if "calories_per_rep" in exercise_info:
                session.calories_burned = session.rep_count * exercise_info["calories_per_rep"]
            elif "calories_per_second" in exercise_info:
                duration = (session.end_time - session.start_time).seconds
                session.calories_burned = duration * exercise_info["calories_per_second"]
            
            # フィードバック生成
            feedback_count = random.randint(0, 3)
            for _ in range(feedback_count):
                if session.form_score < 0.7:
                    session.feedback_notes.append("フォームに注意してください")
                elif session.form_score > 0.9:
                    session.feedback_notes.append("素晴らしいフォームです！")
                else:
                    session.feedback_notes.append("良いペースです")
            
            user.workout_history.append(session)
    
    # 設定保存
    trainer.save_config()
    
    print(f"✅ デモデータ作成完了！")
    print(f"📁 設定ファイル: {trainer.config_path}")
    print(f"👥 ユーザー数: {len(trainer.user_profiles)}")
    
    total_sessions = sum(len(user.workout_history) for user in trainer.user_profiles.values())
    print(f"💪 総セッション数: {total_sessions}")
    
    return trainer

async def demo_ai_session():
    """AIトレーナーセッションのデモ"""
    print("\n🤖 AIトレーナーセッションデモ")
    print("=" * 50)
    print("注意: 実際のセッションにはWebカメラとマイクが必要です")
    print("このデモでは設定とデータ構造のみ表示します\n")
    
    trainer = PersonalGymTrainer()
    trainer.load_config()
    
    # デモユーザーを選択
    demo_user_id = "demo_intermediate"
    if demo_user_id not in trainer.user_profiles:
        print(f"❌ ユーザー {demo_user_id} が見つかりません")
        print("先にデモデータを作成してください: python demo.py create-data")
        return
    
    user_profile = trainer.user_profiles[demo_user_id]
    print(f"👤 選択ユーザー: {user_profile.name}")
    print(f"📊 フィットネスレベル: {user_profile.fitness_level}")
    print(f"🎯 目標: {', '.join(user_profile.target_goals)}")
    
    # AIエージェント作成（実際には実行されない）
    print("\n🧠 AIエージェント設定:")
    instructions = trainer._generate_personalized_instructions(user_profile)
    print("指導内容プレビュー:")
    print("─" * 30)
    print(instructions[:300] + "...")
    print("─" * 30)
    
    # セッション統計表示
    summary = trainer.get_workout_summary(demo_user_id, days=30)
    print(f"\n📈 過去30日の統計:")
    for key, value in summary.items():
        if key != 'improvement_suggestions':
            print(f"  {key}: {value}")
    
    if 'improvement_suggestions' in summary:
        print(f"\n💡 改善提案:")
        for suggestion in summary['improvement_suggestions']:
            print(f"  • {suggestion}")

def show_system_info():
    """システム情報表示"""
    print("🏋️‍♀️ パーソナルジムAIトレーナーシステム")
    print("=" * 50)
    print("Vision Agents ベース リアルタイム姿勢解析システム")
    print()
    print("主な機能:")
    print("  • YOLOによるリアルタイム姿勢検出")
    print("  • AIによる音声フィードバック")
    print("  • 個別化されたトレーニング指導")
    print("  • 自動セッション記録・分析")
    print("  • Webベース管理ダッシュボード")
    print()
    print("対応運動:")
    
    trainer = PersonalGymTrainer()
    for ex_id, exercise in trainer.exercise_database.items():
        print(f"  • {exercise['name']}: {', '.join(exercise['target_muscles'])}")
    print()

async def main():
    """メイン実行関数"""
    import sys
    
    if len(sys.argv) < 2:
        show_system_info()
        print("使用方法:")
        print("  python demo.py create-data    # デモデータ作成")
        print("  python demo.py ai-session     # AIセッションデモ")
        print("  python demo.py info           # システム情報表示")
        return
    
    command = sys.argv[1]
    
    if command == "create-data":
        await create_demo_data()
    elif command == "ai-session":
        await demo_ai_session()
    elif command == "info":
        show_system_info()
    else:
        print(f"❌ 不明なコマンド: {command}")
        print("利用可能なコマンド: create-data, ai-session, info")

if __name__ == "__main__":
    asyncio.run(main())