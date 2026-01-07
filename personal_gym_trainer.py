#!/usr/bin/env python3
"""
パーソナルジム向けAIトレーナーシステム
Vision Agentsを使用したリアルタイム姿勢解析とトレーニング指導

主な機能:
1. リアルタイムフォーム分析
2. 筋トレ動作の自動カウント
3. 音声による即座のフィードバック
4. トレーニング履歴の記録
5. 個別化された運動プログラムの提案
"""

import asyncio
import logging
import json
import datetime
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from dotenv import load_dotenv

from vision_agents.core import User, Agent
from vision_agents.core.agents import AgentLauncher
from vision_agents.core.llm.realtime import Realtime
from vision_agents.core.processors import Processor, VideoProcessor

# StreamEdgeの実装をインポート（プラグインが見つからない場合の代替）
try:
    from vision_agents.plugins.getstream.stream_edge_transport import StreamEdge
    from vision_agents.plugins import ultralytics
    getstream_available = True
except ImportError:
    # プラグインが見つからない場合、完全な実装を使用
    import logging
    logging.warning("vision_agents.pluginsが見つかりません。完全な実装を使用します。")
    getstream_available = False
    
    # StreamEdgeの完全な実装をインポート
    try:
        from stream_edge_complete import StreamEdge
        logging.info("StreamEdgeの完全な実装を読み込みました。")
    except ImportError:
        # フォールバック: 簡易実装
        logging.warning("stream_edge_completeが見つかりません。簡易実装を使用します。")
        class StreamEdge:
            def __init__(self):
                from getstream.video.client import VideoClient
                import os
                api_key = os.getenv("STREAM_API_KEY")
                api_secret = os.getenv("STREAM_API_SECRET")
                if not api_key or not api_secret:
                    raise ValueError("STREAM_API_KEY and STREAM_API_SECRET must be set")
                # 簡易実装
                self.client = type('Client', (), {
                    'video': type('Video', (), {
                        'call': lambda call_type, call_id: None
                    })()
                })()
    
    # ultralyticsは直接インポート
    import ultralytics

# 環境変数を読み込み
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class WorkoutSession:
    """ワークアウトセッション情報"""
    user_id: str
    exercise_type: str
    start_time: datetime.datetime
    end_time: Optional[datetime.datetime] = None
    rep_count: int = 0
    form_score: float = 0.0
    feedback_notes: List[str] = None
    calories_burned: float = 0.0

    def __post_init__(self):
        if self.feedback_notes is None:
            self.feedback_notes = []


@dataclass
class UserProfile:
    """ユーザープロファイル"""
    user_id: str
    name: str
    fitness_level: str  # beginner, intermediate, advanced
    target_goals: List[str]  # weight_loss, muscle_gain, endurance, etc.
    physical_limitations: List[str]
    preferred_language: str = "ja"
    workout_history: List[WorkoutSession] = None
    line_user_id: Optional[str] = None  # LINEユーザーID

    def __post_init__(self):
        if self.workout_history is None:
            self.workout_history = []


class PersonalGymTrainer:
    """パーソナルジムトレーナー AI システム"""
    
    def __init__(self, config_path: str = "gym_config.json"):
        self.config_path = Path(config_path)
        self.user_profiles: Dict[str, UserProfile] = {}
        self.current_session: Optional[WorkoutSession] = None
        self.exercise_database = self._load_exercise_database()
        
        # ログ設定
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _load_exercise_database(self) -> Dict[str, Dict]:
        """運動データベースを読み込み"""
        return {
            "squat": {
                "name": "スクワット",
                "target_muscles": ["大腿四頭筋", "大臀筋", "ハムストリング"],
                "form_checkpoints": [
                    "膝がつま先より前に出すぎない",
                    "背中をまっすぐ保つ",
                    "太ももが床と平行になるまで下げる",
                    "かかとに体重をかける"
                ],
                "common_mistakes": [
                    "膝の内転",
                    "前傾姿勢",
                    "可動域不足",
                    "足首の硬さ"
                ],
                "calories_per_rep": 0.32
            },
            "push_up": {
                "name": "腕立て伏せ",
                "target_muscles": ["大胸筋", "三角筋", "上腕三頭筋"],
                "form_checkpoints": [
                    "体を一直線に保つ",
                    "手の位置は肩幅よりやや広く",
                    "胸を床に近づける",
                    "肘は45度の角度"
                ],
                "common_mistakes": [
                    "腰の反り",
                    "可動域不足",
                    "肘の開きすぎ",
                    "頭の下がり"
                ],
                "calories_per_rep": 0.29
            },
            "deadlift": {
                "name": "デッドリフト",
                "target_muscles": ["ハムストリング", "大臀筋", "脊柱起立筋"],
                "form_checkpoints": [
                    "バーを体に近づける",
                    "背中をニュートラルに保つ",
                    "膝と股関節を同時に伸展",
                    "肩甲骨を後ろに引く"
                ],
                "common_mistakes": [
                    "バーが体から離れる",
                    "背中の丸まり",
                    "膝の前方移動",
                    "肩の前方突出"
                ],
                "calories_per_rep": 0.45
            },
            "plank": {
                "name": "プランク",
                "target_muscles": ["腹直筋", "腹横筋", "脊柱起立筋"],
                "form_checkpoints": [
                    "体を一直線に保つ",
                    "肘は肩の真下に置く",
                    "お尻を上げすぎない",
                    "呼吸を止めない"
                ],
                "common_mistakes": [
                    "腰の反り",
                    "お尻の上がり",
                    "頭の下がり",
                    "肘の位置不良"
                ],
                "calories_per_second": 0.05
            }
        }
    
    async def create_agent(self, user_profile: UserProfile) -> Agent:
        """ユーザー専用のAIトレーナーエージェントを作成"""
        
        # ユーザー専用の指示を生成
        instructions = self._generate_personalized_instructions(user_profile)
        
        # StreamEdgeを作成
        edge = StreamEdge()
        
        # Realtime LLMを作成
        # プラグインが見つからない場合、代替実装を使用
        try:
            # プラグインからGemini Realtimeをインポート
            from vision_agents.plugins.gemini import Realtime as GeminiRealtimePlugin
            llm = GeminiRealtimePlugin(fps=5)
        except ImportError:
            # 代替実装を使用
            try:
                from gemini_realtime_impl import GeminiRealtime
                llm = GeminiRealtime(fps=5)  # 適度なFPSでコスト調整
            except (ImportError, Exception) as e:
                # フォールバック: 簡易LLM実装を使用
                import logging
                logging.warning(f"Gemini Realtime実装の読み込みに失敗しました: {e}")
                logging.warning("簡易LLM実装を使用します（機能が制限される可能性があります）。")
                # 簡易LLM実装（実際の使用には完全な実装が必要）
                from vision_agents.core.llm import LLM
                class SimpleLLM(LLM):
                    def __init__(self):
                        super().__init__()
                    async def respond(self, *args, **kwargs):
                        return "簡易LLM実装です。完全な実装が必要です。"
                llm = SimpleLLM()
        
        # Processorの作成（ultralyticsプラグインが利用可能な場合）
        processors = []
        if getstream_available and hasattr(ultralytics, 'YOLOPoseProcessor'):
            processors.append(
                ultralytics.YOLOPoseProcessor(
                    model_path="yolo11n-pose.pt",
                    conf_threshold=0.3,  # より敏感な検出
                    device="cuda" if self._cuda_available() else "cpu",
                    enable_hand_tracking=True,
                    enable_wrist_highlights=True
                )
            )
        else:
            import logging
            logging.warning("YOLOPoseProcessorが利用できません。プラグインのインストールが必要です。")
        
        # Userオブジェクトを作成（IDが必要）
        agent_user = User(
            id=f"agent_{user_profile.user_id}",  # ユニークなIDを設定
            name=f"AIトレーナー for {user_profile.name}"
        )
        
        agent = Agent(
            edge=edge,
            agent_user=agent_user,
            instructions=instructions,
            llm=llm,
            processors=processors if processors else None,
        )
        
        logger.info(f"✅ AIトレーナーエージェント作成完了: {user_profile.name}")
        return agent
    
    def _generate_personalized_instructions(self, user_profile: UserProfile) -> str:
        """ユーザー専用の指示を生成"""
        
        base_instructions = f"""
あなたは{user_profile.name}さん専用のパーソナルジムトレーナーAIです。

## ユーザー情報:
- 名前: {user_profile.name}
- フィットネスレベル: {user_profile.fitness_level}
- 目標: {', '.join(user_profile.target_goals)}
- 身体的制約: {', '.join(user_profile.physical_limitations) if user_profile.physical_limitations else 'なし'}

## あなたの役割:
1. **リアルタイム姿勢分析**: YOLOによる姿勢検出データを基に、運動フォームを即座に評価
2. **即座のフィードバック**: 危険なフォームや間違いを発見したらすぐに音声で指導
3. **モチベーション維持**: 励ましの言葉と適切なタイミングでの休憩指示
4. **回数カウント**: 正しいフォームでの反復回数を自動計測
5. **安全性確保**: 怪我のリスクがある動作は即座に停止指示

## 指導スタイル:
- 日本語で親しみやすく、でも専門的に指導
- 褒める時は具体的に（「膝の角度が完璧です！」など）
- 注意する時は建設的に（「もう少し背中をまっすぐにしましょう」など）
- 安全第一で、無理をさせない

## フォーム評価の重点:
"""
        
        # ユーザーのレベルに応じた指導内容を調整
        if user_profile.fitness_level == "beginner":
            base_instructions += """
- 基本的なフォームの習得を最優先
- 回数より質を重視
- 十分な休憩時間を確保
- 簡潔で分かりやすい指示
"""
        elif user_profile.fitness_level == "intermediate":
            base_instructions += """
- フォームの細かい修正
- 適度なチャレンジを提供
- 効率性の向上を支援
- より詳細な技術指導
"""
        else:  # advanced
            base_instructions += """
- 高度な技術の最適化
- パフォーマンスの数値化
- 細かいバイオメカニクスの指導
- 競技レベルの精度を追求
"""
        
        base_instructions += """

## 緊急時の対応:
- 明らかに危険なフォームの場合は「ストップ！」と大きな声で停止指示
- 疲労の兆候を見つけたら即座に休憩を勧める
- 痛みを訴えた場合は運動を中止し、医師の診察を勧める

YOLOの姿勢検出データと映像を組み合わせて、リアルタイムで的確な指導を行ってください。
"""
        
        return base_instructions
    
    def _cuda_available(self) -> bool:
        """CUDA利用可能性をチェック"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def start_workout_session(self, user_id: str, exercise_type: str) -> WorkoutSession:
        """ワークアウトセッション開始"""
        session = WorkoutSession(
            user_id=user_id,
            exercise_type=exercise_type,
            start_time=datetime.datetime.now()
        )
        self.current_session = session
        logger.info(f"🏃‍♂️ ワークアウト開始: {exercise_type} (ユーザー: {user_id})")
        return session
    
    def end_workout_session(self) -> Optional[WorkoutSession]:
        """ワークアウトセッション終了"""
        if not self.current_session:
            return None
        
        self.current_session.end_time = datetime.datetime.now()
        
        # カロリー計算
        exercise_info = self.exercise_database.get(self.current_session.exercise_type, {})
        if "calories_per_rep" in exercise_info:
            self.current_session.calories_burned = (
                self.current_session.rep_count * exercise_info["calories_per_rep"]
            )
        elif "calories_per_second" in exercise_info:
            duration = (self.current_session.end_time - self.current_session.start_time).seconds
            self.current_session.calories_burned = duration * exercise_info["calories_per_second"]
        
        # ユーザープロファイルに記録
        if self.current_session.user_id in self.user_profiles:
            self.user_profiles[self.current_session.user_id].workout_history.append(self.current_session)
        
        completed_session = self.current_session
        self.current_session = None
        
        logger.info(f"✅ ワークアウト完了: {completed_session.rep_count}回, {completed_session.calories_burned:.1f}kcal")
        return completed_session
    
    def add_user_profile(self, user_profile: UserProfile):
        """ユーザープロファイル追加"""
        self.user_profiles[user_profile.user_id] = user_profile
        logger.info(f"👤 ユーザー追加: {user_profile.name}")
    
    def get_workout_summary(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """ワークアウト履歴サマリー取得"""
        if user_id not in self.user_profiles:
            return {}
        
        user = self.user_profiles[user_id]
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        
        recent_sessions = [
            session for session in user.workout_history
            if session.start_time >= cutoff_date
        ]
        
        if not recent_sessions:
            return {"message": f"過去{days}日間のワークアウト記録がありません"}
        
        # 統計計算
        total_sessions = len(recent_sessions)
        total_reps = sum(session.rep_count for session in recent_sessions)
        total_calories = sum(session.calories_burned for session in recent_sessions)
        average_form_score = sum(session.form_score for session in recent_sessions) / total_sessions
        
        exercise_breakdown = {}
        for session in recent_sessions:
            if session.exercise_type not in exercise_breakdown:
                exercise_breakdown[session.exercise_type] = {"count": 0, "reps": 0}
            exercise_breakdown[session.exercise_type]["count"] += 1
            exercise_breakdown[session.exercise_type]["reps"] += session.rep_count
        
        return {
            "period_days": days,
            "total_sessions": total_sessions,
            "total_reps": total_reps,
            "total_calories": round(total_calories, 1),
            "average_form_score": round(average_form_score, 2),
            "exercise_breakdown": exercise_breakdown,
            "improvement_suggestions": self._generate_suggestions(user, recent_sessions)
        }
    
    def _generate_suggestions(self, user: UserProfile, sessions: List[WorkoutSession]) -> List[str]:
        """改善提案を生成"""
        suggestions = []
        
        # フォームスコアが低い場合
        avg_form_score = sum(s.form_score for s in sessions) / len(sessions)
        if avg_form_score < 0.7:
            suggestions.append("フォームの改善に重点を置きましょう。回数よりも正しいフォームを優先してください。")
        
        # 同じ運動ばかりしている場合
        exercise_types = set(s.exercise_type for s in sessions)
        if len(exercise_types) < 2:
            suggestions.append("運動のバリエーションを増やして、全身をバランス良く鍛えましょう。")
        
        # セッション頻度が少ない場合
        if len(sessions) < 3:
            suggestions.append("週3回以上のトレーニングを目標にしましょう。")
        
        return suggestions
    
    def save_config(self):
        """設定とデータを保存"""
        config_data = {
            "user_profiles": {
                user_id: asdict(profile) for user_id, profile in self.user_profiles.items()
            },
            "exercise_database": self.exercise_database
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info("💾 設定を保存しました")
    
    def load_config(self):
        """設定とデータを読み込み"""
        if not self.config_path.exists():
            logger.info("設定ファイルが見つかりません。新規作成します。")
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # ユーザープロファイルを復元
            if "user_profiles" in config_data:
                for user_id, profile_data in config_data["user_profiles"].items():
                    # WorkoutSessionオブジェクトを復元
                    if "workout_history" in profile_data:
                        workout_history = []
                        for session_data in profile_data["workout_history"]:
                            session_data["start_time"] = datetime.datetime.fromisoformat(session_data["start_time"])
                            if session_data["end_time"]:
                                session_data["end_time"] = datetime.datetime.fromisoformat(session_data["end_time"])
                            workout_history.append(WorkoutSession(**session_data))
                        profile_data["workout_history"] = workout_history
                    
                    self.user_profiles[user_id] = UserProfile(**profile_data)
            
            logger.info("📂 設定を読み込みました")
        
        except Exception as e:
            logger.error(f"設定読み込みエラー: {e}")


async def join_call(agent: Agent, call_type: str, call_id: str, trainer: PersonalGymTrainer, user_id: str, exercise_type: str) -> None:
    """通話に参加してトレーニングセッションを開始"""
    call = await agent.create_call(call_type, call_id)
    
    # ワークアウトセッション開始
    session = trainer.start_workout_session(user_id, exercise_type)
    
    try:
        # vision_agentsのAPIに応じて、適切な方法でjoinを呼び出す
        # 方法1: async withを使用（agent.joinがコンテキストマネージャーを返す場合）
        join_result = await agent.join(call)
        
        # コンテキストマネージャーとして使用できるか確認
        if hasattr(join_result, '__aenter__'):
            async with join_result:
                await _run_training_session(agent, trainer, exercise_type)
        else:
            # 方法2: 直接使用（コンテキストマネージャーでない場合）
            await _run_training_session(agent, trainer, exercise_type)
            if hasattr(join_result, 'close'):
                await join_result.close()
    
    except Exception as e:
        logger.error(f"セッション実行エラー: {e}")
        raise
    finally:
        # セッション終了処理
        completed_session = trainer.end_workout_session()
        if completed_session:
            summary = f"""
お疲れ様でした！今回のトレーニング結果：
- 運動: {trainer.exercise_database.get(completed_session.exercise_type, {}).get('name', completed_session.exercise_type)}
- 回数: {completed_session.rep_count}回
- 消費カロリー: {completed_session.calories_burned:.1f}kcal
- フォームスコア: {completed_session.form_score:.1f}/1.0

素晴らしいトレーニングでした！次回も頑張りましょう！
"""
            print(summary)


async def _run_training_session(agent: Agent, trainer: PersonalGymTrainer, exercise_type: str) -> None:
    """トレーニングセッションの実行ロジック"""
    # 初期挨拶とセッション開始
    exercise_info = trainer.exercise_database.get(exercise_type, {})
    exercise_name = exercise_info.get("name", exercise_type)
    
    greeting = f"""
こんにちは！今日は{exercise_name}のトレーニングですね。
まず軽くウォームアップをして、準備ができたら声をかけてください。
正しいフォームで安全にトレーニングしましょう！

注目ポイント：
"""
    
    if "form_checkpoints" in exercise_info:
        for i, checkpoint in enumerate(exercise_info["form_checkpoints"], 1):
            greeting += f"\n{i}. {checkpoint}"
    
    # 挨拶を送信（vision_agentsのAPIに応じて調整が必要な場合あり）
    try:
        # 方法1: simple_responseが利用可能な場合
        if hasattr(agent.llm, 'simple_response'):
            await agent.llm.simple_response(text=greeting)
        # 方法2: agentに直接メソッドがある場合
        elif hasattr(agent, 'say') or hasattr(agent, 'speak'):
            method = getattr(agent, 'say', None) or getattr(agent, 'speak', None)
            await method(greeting)
        else:
            # 方法3: ログに記録（デバッグ用）
            logger.info(f"挨拶: {greeting}")
    except Exception as e:
        logger.warning(f"挨拶送信エラー（続行）: {e}")
    
    # セッション継続（通話が終了するまで）
    # 注意: agent.finish()は実際のAPIに応じて調整が必要
    try:
        if hasattr(agent, 'finish'):
            await agent.finish()
        elif hasattr(agent, 'wait'):
            await agent.wait()
    except Exception as e:
        logger.warning(f"セッション終了処理エラー: {e}")


def main():
    """メイン実行関数"""
    # トレーナーシステム初期化
    trainer = PersonalGymTrainer()
    trainer.load_config()
    
    # サンプルユーザー作成（実際の使用では外部から登録）
    sample_user = UserProfile(
        user_id="user001",
        name="田中太郎",
        fitness_level="intermediate",
        target_goals=["muscle_gain", "strength"],
        physical_limitations=[],
        preferred_language="ja"
    )
    trainer.add_user_profile(sample_user)
    
    # エージェント作成とセッション開始のための関数を定義
    async def create_agent(**kwargs) -> Agent:
        user_id = kwargs.get("user_id", "user001")
        user_profile = trainer.user_profiles[user_id]
        return await trainer.create_agent(user_profile)
    
    async def session_join_call(agent: Agent, call_type: str, call_id: str, **kwargs) -> None:
        user_id = kwargs.get("user_id", "user001")
        exercise_type = kwargs.get("exercise_type", "squat")
        await join_call(agent, call_type, call_id, trainer, user_id, exercise_type)
    
    # CLI起動
    from vision_agents.core import cli
    
    print("""
🏋️‍♀️ パーソナルジム AIトレーナーシステム起動

利用可能な運動:
- squat (スクワット)
- push_up (腕立て伏せ)  
- deadlift (デッドリフト)
- plank (プランク)

システムが起動したら、Webブラウザでアクセスしてトレーニングを開始してください。
""")
    
    try:
        cli(AgentLauncher(
            create_agent=create_agent,
            join_call=session_join_call
        ))
    finally:
        # 終了時に設定を保存
        trainer.save_config()
        print("👋 トレーニングお疲れ様でした！")


if __name__ == "__main__":
    main()