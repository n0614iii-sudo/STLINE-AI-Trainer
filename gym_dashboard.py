#!/usr/bin/env python3
"""
パーソナルジム管理ダッシュボード
Webベースの管理インターフェース
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
import json
import datetime
import os
import base64
import numpy as np
from pathlib import Path
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from personal_gym_trainer import PersonalGymTrainer, UserProfile, WorkoutSession
from posture_analyzer import PostureAnalyzer, PostureAnalysis
from posture_detector import PostureDetector

# 環境変数を読み込み
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# ファイルアップロード設定
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'webm'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# アップロードフォルダを作成
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'images'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'videos'), exist_ok=True)

# ロガー設定
import logging
logger = logging.getLogger(__name__)

def allowed_file(filename):
    """許可されたファイル拡張子かチェック"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_video_file(filename):
    """動画ファイルかチェック"""
    video_extensions = {'mp4', 'mov', 'avi', 'webm'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in video_extensions

# グローバルトレーナーインスタンス
trainer = PersonalGymTrainer()

# 姿勢分析器インスタンス
posture_analyzer = PostureAnalyzer()

# 姿勢検出器インスタンス（必要に応じて初期化）
posture_detector = None

def get_posture_detector():
    """姿勢検出器を取得（遅延初期化）"""
    global posture_detector
    if posture_detector is None:
        try:
            posture_detector = PostureDetector(device="cpu")  # RailwayではCPUを使用
        except Exception as e:
            logger.warning(f"姿勢検出器の初期化に失敗しました: {e}")
            posture_detector = None
    return posture_detector


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


@app.route('/posture_diagnosis')
def posture_diagnosis():
    """姿勢診断ページ"""
    users_data = []
    for user_id, user in trainer.user_profiles.items():
        users_data.append({
            'user_id': user_id,
            'name': user.name
        })
    
    return render_template('posture_diagnosis.html', users=users_data)


@app.route('/posture_diagnosis/<user_id>')
def posture_diagnosis_user(user_id):
    """ユーザー別姿勢診断ページ"""
    if user_id not in trainer.user_profiles:
        return "ユーザーが見つかりません", 404
    
    user = trainer.user_profiles[user_id]
    
    # 過去の診断結果を読み込み
    analyses = posture_analyzer.load_analyses(user_id)
    
    # 最新の診断結果
    latest_analysis = analyses[-1] if analyses else None
    
    # 診断履歴
    history_data = []
    for analysis in sorted(analyses, key=lambda a: a.timestamp, reverse=True)[:10]:
        history_data.append({
            'date': analysis.timestamp.strftime('%Y-%m-%d %H:%M'),
            'score': analysis.overall_score,
            'posture_type': analysis.posture_type,
            'issues_count': len(analysis.issues)
        })
    
    # サマリー
    summary = posture_analyzer.get_analysis_summary(user_id, days=30)
    
    return render_template('posture_diagnosis_user.html',
                         user=user,
                         latest_analysis=latest_analysis,
                         history=history_data,
                         summary=summary)


@app.route('/api/posture/analyze', methods=['POST'])
def api_posture_analyze():
    """姿勢分析API"""
    data = request.json
    
    user_id = data.get('user_id')
    keypoints = data.get('keypoints', {})
    image_data = data.get('image', None)  # Base64エンコードされた画像
    posture_type = data.get('posture_type', 'standing')
    
    if not user_id:
        return jsonify({"status": "error", "message": "user_idが必要です"}), 400
    
    try:
        # 画像が提供されている場合、YOLOでキーポイントを検出
        if image_data:
            try:
                # Base64デコード
                image_bytes = base64.b64decode(image_data.split(',')[-1])
                try:
                    import cv2
                    nparr = np.frombuffer(image_bytes, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                except ImportError:
                    # opencv-python-headlessがインストールされていない場合
                    logger.warning("cv2が利用できません。キーポイント検出をスキップします。")
                    image = None
                
                if image is not None:
                    # 姿勢検出器を使用してキーポイントを検出
                    detector = get_posture_detector()
                    if detector:
                        detected_keypoints = detector.detect_keypoints(image)
                        if detected_keypoints:
                            keypoints = detected_keypoints
            except Exception as e:
                logger.warning(f"画像からのキーポイント検出に失敗しました: {e}")
                # フォールバック: 提供されたキーポイントを使用
        
        # キーポイントが提供されていない場合
        if not keypoints:
            return jsonify({"status": "error", "message": "keypointsまたはimageが必要です"}), 400
        
        # キーポイントをタプル形式に変換
        keypoints_tuple = {}
        for name, point in keypoints.items():
            if isinstance(point, (list, tuple)) and len(point) >= 2:
                x, y = point[0], point[1]
                conf = point[2] if len(point) >= 3 else 1.0
                keypoints_tuple[name] = (float(x), float(y), float(conf))
        
        # 姿勢を分析
        analysis = posture_analyzer.analyze_posture(keypoints_tuple, posture_type)
        
        # 結果を保存
        posture_analyzer.save_analysis(user_id, analysis)
        
        # レスポンスを準備
        response = {
            "status": "success",
            "analysis": {
                "overall_score": analysis.overall_score,
                "posture_type": analysis.posture_type,
                "issues": analysis.issues,
                "recommendations": analysis.recommendations,
                "alignment_scores": analysis.alignment_scores,
                "keypoint_angles": analysis.keypoint_angles,
                "timestamp": analysis.timestamp.isoformat()
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"姿勢分析エラー: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/posture/history/<user_id>')
def api_posture_history(user_id):
    """姿勢診断履歴API"""
    if user_id not in trainer.user_profiles:
        return jsonify({"status": "error", "message": "ユーザーが見つかりません"}), 404
    
    analyses = posture_analyzer.load_analyses(user_id)
    
    history = []
    for analysis in sorted(analyses, key=lambda a: a.timestamp, reverse=True):
        history.append({
            "timestamp": analysis.timestamp.isoformat(),
            "overall_score": analysis.overall_score,
            "posture_type": analysis.posture_type,
            "issues_count": len(analysis.issues),
            "issues": analysis.issues
        })
    
    return jsonify({"status": "success", "history": history})


@app.route('/api/posture/summary/<user_id>')
def api_posture_summary(user_id):
    """姿勢診断サマリーAPI"""
    if user_id not in trainer.user_profiles:
        return jsonify({"status": "error", "message": "ユーザーが見つかりません"}), 404
    
    days = request.args.get('days', 30, type=int)
    summary = posture_analyzer.get_analysis_summary(user_id, days=days)
    
    return jsonify({"status": "success", "summary": summary})


@app.route('/api/posture/upload', methods=['POST'])
def api_posture_upload():
    """動画・画像アップロードAPI"""
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "ファイルが選択されていません"}), 400
    
    file = request.files['file']
    user_id = request.form.get('user_id')
    posture_type = request.form.get('posture_type', 'standing')
    
    if not user_id:
        return jsonify({"status": "error", "message": "user_idが必要です"}), 400
    
    if file.filename == '':
        return jsonify({"status": "error", "message": "ファイルが選択されていません"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"status": "error", "message": "許可されていないファイル形式です"}), 400
    
    try:
        # ファイルを保存
        filename = secure_filename(file.filename)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"{timestamp}_{filename}"
        
        if is_video_file(filename):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', safe_filename)
        else:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'images', safe_filename)
        
        file.save(filepath)
        
        # 画像または動画から姿勢分析を実行
        if is_video_file(filename):
            # 動画からフレームを抽出して分析
            result = analyze_video_posture(filepath, user_id, posture_type)
        else:
            # 画像から姿勢分析
            result = analyze_image_posture(filepath, user_id, posture_type)
        
        if result['status'] == 'success':
            return jsonify({
                "status": "success",
                "message": "姿勢分析が完了しました",
                "file_url": f"/uploads/{'videos' if is_video_file(filename) else 'images'}/{safe_filename}",
                "analysis": result.get('analysis')
            })
        else:
            return jsonify(result), 500
    
    except Exception as e:
        logger.error(f"ファイルアップロードエラー: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


def analyze_image_posture(image_path, user_id, posture_type):
    """画像から姿勢分析"""
    try:
        import cv2
        image = cv2.imread(image_path)
        
        if image is None:
            return {"status": "error", "message": "画像の読み込みに失敗しました"}
        
        # 姿勢検出器を使用してキーポイントを検出
        detector = get_posture_detector()
        if not detector:
            return {"status": "error", "message": "姿勢検出器が利用できません"}
        
        detected_keypoints = detector.detect_keypoints(image)
        if not detected_keypoints:
            return {"status": "error", "message": "姿勢が検出できませんでした"}
        
        # キーポイントをタプル形式に変換
        keypoints_tuple = {}
        for name, point in detected_keypoints.items():
            if isinstance(point, (list, tuple)) and len(point) >= 2:
                x, y = point[0], point[1]
                conf = point[2] if len(point) >= 3 else 1.0
                keypoints_tuple[name] = (float(x), float(y), float(conf))
        
        # 姿勢を分析
        analysis = posture_analyzer.analyze_posture(keypoints_tuple, posture_type)
        posture_analyzer.save_analysis(user_id, analysis)
        
        return {
            "status": "success",
            "analysis": {
                "overall_score": analysis.overall_score,
                "posture_type": analysis.posture_type,
                "issues": analysis.issues,
                "recommendations": analysis.recommendations,
                "alignment_scores": analysis.alignment_scores,
                "keypoint_angles": analysis.keypoint_angles,
                "timestamp": analysis.timestamp.isoformat()
            }
        }
    
    except Exception as e:
        logger.error(f"画像姿勢分析エラー: {e}")
        return {"status": "error", "message": str(e)}


def analyze_video_posture(video_path, user_id, posture_type):
    """動画から姿勢分析（最初のフレームと中間フレームを分析）"""
    try:
        import cv2
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {"status": "error", "message": "動画の読み込みに失敗しました"}
        
        # 動画の情報を取得
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        if total_frames == 0:
            return {"status": "error", "message": "動画にフレームがありません"}
        
        # 分析するフレームを選択（最初、中間、最後）
        frame_indices = [0, total_frames // 2, total_frames - 1]
        analyses = []
        
        detector = get_posture_detector()
        if not detector:
            return {"status": "error", "message": "姿勢検出器が利用できません"}
        
        for frame_idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if not ret:
                continue
            
            # キーポイントを検出
            detected_keypoints = detector.detect_keypoints(frame)
            if not detected_keypoints:
                continue
            
            # キーポイントをタプル形式に変換
            keypoints_tuple = {}
            for name, point in detected_keypoints.items():
                if isinstance(point, (list, tuple)) and len(point) >= 2:
                    x, y = point[0], point[1]
                    conf = point[2] if len(point) >= 3 else 1.0
                    keypoints_tuple[name] = (float(x), float(y), float(conf))
            
            # 姿勢を分析
            analysis = posture_analyzer.analyze_posture(keypoints_tuple, posture_type)
            analyses.append(analysis)
        
        cap.release()
        
        if not analyses:
            return {"status": "error", "message": "動画から姿勢が検出できませんでした"}
        
        # 複数のフレームの平均を計算
        avg_score = sum(a.overall_score for a in analyses) / len(analyses)
        all_issues = []
        for a in analyses:
            all_issues.extend(a.issues)
        
        # ユニークな問題点を取得
        unique_issues = {}
        for issue in all_issues:
            issue_type = issue['type']
            if issue_type not in unique_issues or issue['severity'] == 'high':
                unique_issues[issue_type] = issue
        
        # 推奨事項を統合
        all_recommendations = []
        for a in analyses:
            all_recommendations.extend(a.recommendations)
        unique_recommendations = list(dict.fromkeys(all_recommendations))
        
        # 最終分析結果を作成
        final_analysis = PostureAnalysis(
            timestamp=datetime.datetime.now(),
            posture_type=posture_type,
            overall_score=avg_score,
            issues=list(unique_issues.values()),
            recommendations=unique_recommendations[:5],  # 上位5件
            keypoint_angles=analyses[0].keypoint_angles if analyses else {},
            alignment_scores=analyses[0].alignment_scores if analyses else {},
            detailed_metrics=analyses[0].detailed_metrics if analyses else {}
        )
        
        posture_analyzer.save_analysis(user_id, final_analysis)
        
        return {
            "status": "success",
            "analysis": {
                "overall_score": final_analysis.overall_score,
                "posture_type": final_analysis.posture_type,
                "issues": final_analysis.issues,
                "recommendations": final_analysis.recommendations,
                "alignment_scores": final_analysis.alignment_scores,
                "keypoint_angles": final_analysis.keypoint_angles,
                "timestamp": final_analysis.timestamp.isoformat(),
                "frames_analyzed": len(analyses),
                "total_frames": total_frames
            }
        }
    
    except Exception as e:
        logger.error(f"動画姿勢分析エラー: {e}")
        return {"status": "error", "message": str(e)}


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """アップロードされたファイルを提供"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


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