#!/usr/bin/env python3
"""
パーソナルジム管理ダッシュボード
Webベースの管理インターフェース
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import datetime
import os
from pathlib import Path
from dotenv import load_dotenv
from personal_gym_trainer import PersonalGymTrainer, UserProfile, WorkoutSession

# 環境変数を読み込み
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# グローバルトレーナーインスタンス
trainer = PersonalGymTrainer()


@app.route('/')
def dashboard():
    """メインダッシュボード"""
    # 全体統計を計算
    total_users = len(trainer.user_profiles)
    total_sessions = sum(len(user.workout_history) for user in trainer.user_profiles.values())
    
    recent_sessions = []
    for user in trainer.user_profiles.values():
        for session in user.workout_history[-5:]:  # 最新5件
            recent_sessions.append({
                'user_name': user.name,
                'exercise': trainer.exercise_database.get(session.exercise_type, {}).get('name', session.exercise_type),
                'date': session.start_time.strftime('%Y-%m-%d %H:%M'),
                'reps': session.rep_count,
                'form_score': round(session.form_score, 2)
            })
    
    recent_sessions.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('dashboard.html', 
                         total_users=total_users,
                         total_sessions=total_sessions,
                         recent_sessions=recent_sessions[:10])


@app.route('/users')
def users_list():
    """ユーザー一覧"""
    users_data = []
    for user_id, user in trainer.user_profiles.items():
        last_session = user.workout_history[-1] if user.workout_history else None
        users_data.append({
            'user_id': user_id,
            'name': user.name,
            'fitness_level': user.fitness_level,
            'total_sessions': len(user.workout_history),
            'last_session': last_session.start_time.strftime('%Y-%m-%d') if last_session else 'なし',
            'target_goals': ', '.join(user.target_goals)
        })
    
    return render_template('users.html', users=users_data)


@app.route('/user/<user_id>')
def user_detail(user_id):
    """ユーザー詳細画面"""
    if user_id not in trainer.user_profiles:
        return "ユーザーが見つかりません", 404
    
    user = trainer.user_profiles[user_id]
    
    # 過去30日間の統計
    summary = trainer.get_workout_summary(user_id, days=30)
    
    # セッション履歴（日付順）
    sessions_data = []
    for session in sorted(user.workout_history, key=lambda s: s.start_time, reverse=True):
        duration = "継続中"
        if session.end_time:
            duration = str(session.end_time - session.start_time).split('.')[0]
        
        sessions_data.append({
            'date': session.start_time.strftime('%Y-%m-%d %H:%M'),
            'exercise': trainer.exercise_database.get(session.exercise_type, {}).get('name', session.exercise_type),
            'reps': session.rep_count,
            'form_score': round(session.form_score, 2),
            'calories': round(session.calories_burned, 1),
            'duration': duration,
            'feedback_count': len(session.feedback_notes)
        })
    
    return render_template('user_detail.html', 
                         user=user, 
                         summary=summary, 
                         sessions=sessions_data[:20])  # 最新20件


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """新規ユーザー登録"""
    if request.method == 'POST':
        data = request.json if request.is_json else request.form
        
        user_profile = UserProfile(
            user_id=data['user_id'],
            name=data['name'],
            fitness_level=data['fitness_level'],
            target_goals=data['target_goals'].split(',') if isinstance(data['target_goals'], str) else data['target_goals'],
            physical_limitations=data['physical_limitations'].split(',') if data.get('physical_limitations') else [],
            preferred_language=data.get('preferred_language', 'ja')
        )
        
        trainer.add_user_profile(user_profile)
        trainer.save_config()
        
        if request.is_json:
            return jsonify({"status": "success", "message": "ユーザーが登録されました"})
        else:
            return redirect(url_for('users_list'))
    
    return render_template('add_user.html')


@app.route('/start_session', methods=['POST'])
def start_session():
    """セッション開始"""
    data = request.json
    user_id = data['user_id']
    exercise_type = data['exercise_type']
    
    if user_id not in trainer.user_profiles:
        return jsonify({"status": "error", "message": "ユーザーが見つかりません"}), 404
    
    session = trainer.start_workout_session(user_id, exercise_type)
    return jsonify({
        "status": "success",
        "message": "セッションが開始されました",
        "session_id": f"{session.user_id}_{session.start_time.isoformat()}"
    })


@app.route('/exercises')
def exercises_list():
    """運動一覧とその詳細"""
    return render_template('exercises.html', exercises=trainer.exercise_database)


@app.route('/api/stats')
def api_stats():
    """統計API"""
    # 今日の統計
    today = datetime.date.today()
    today_sessions = []
    
    for user in trainer.user_profiles.values():
        for session in user.workout_history:
            if session.start_time.date() == today:
                today_sessions.append(session)
    
    # 週間統計
    week_ago = today - datetime.timedelta(days=7)
    week_sessions = []
    
    for user in trainer.user_profiles.values():
        for session in user.workout_history:
            if session.start_time.date() >= week_ago:
                week_sessions.append(session)
    
    # 運動別統計
    exercise_stats = {}
    for session in week_sessions:
        ex_type = session.exercise_type
        if ex_type not in exercise_stats:
            exercise_stats[ex_type] = {
                'name': trainer.exercise_database.get(ex_type, {}).get('name', ex_type),
                'count': 0,
                'total_reps': 0,
                'avg_form_score': 0
            }
        exercise_stats[ex_type]['count'] += 1
        exercise_stats[ex_type]['total_reps'] += session.rep_count
        exercise_stats[ex_type]['avg_form_score'] += session.form_score
    
    # 平均スコア計算
    for stats in exercise_stats.values():
        if stats['count'] > 0:
            stats['avg_form_score'] = round(stats['avg_form_score'] / stats['count'], 2)
    
    return jsonify({
        'today_sessions': len(today_sessions),
        'week_sessions': len(week_sessions),
        'total_users': len(trainer.user_profiles),
        'exercise_stats': exercise_stats
    })


if __name__ == '__main__':
    # 設定読み込み
    trainer.load_config()
    
    print("""
🌐 パーソナルジム管理ダッシュボード起動
http://localhost:5000 でアクセスできます

主な機能:
- ユーザー管理
- トレーニング履歴確認
- 統計表示
- セッション管理
""")
    
    # RailwayではPORT環境変数が自動的に設定される
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)