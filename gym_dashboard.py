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
from posture_visualizer import PostureVisualizer
from posture_type_detector import PostureTypeDetector
from pdf_generator import PDFGenerator
from pdf_generator import PDFGenerator

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
os.makedirs(os.path.join(UPLOAD_FOLDER, 'visualizations'), exist_ok=True)  # 可視化画像用ディレクトリ

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

# 姿勢可視化器インスタンス
posture_visualizer = PostureVisualizer()

# 姿勢タイプ自動判定器インスタンス
posture_type_detector = PostureTypeDetector()

# PDF生成器インスタンス
pdf_generator = PDFGenerator()

def get_posture_detector():
    """姿勢検出器を取得（遅延初期化）"""
    global posture_detector
    if posture_detector is None:
        try:
            # 精度向上のため、信頼度閾値を0.25に設定（より敏感な検出）
            posture_detector = PostureDetector(device="cpu", conf_threshold=0.25)
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
        
        # ユーザーIDの重複チェック
        user_id = data.get('user_id', '').strip()
        if not user_id:
            # ユーザーIDが空の場合は自動生成
            import random
            import string
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
            user_id = f"user_{timestamp}_{random_str}"
        
        # 既存ユーザーIDのチェック
        if user_id in trainer.user_profiles:
            # 重複している場合は番号を追加
            counter = 1
            original_user_id = user_id
            while user_id in trainer.user_profiles:
                user_id = f"{original_user_id}_{counter}"
                counter += 1
        
        # 名前の必須チェック
        name = data.get('name', '').strip()
        if not name:
            if request.is_json:
                return jsonify({"status": "error", "message": "名前は必須です"}), 400
            else:
                return redirect(url_for('add_user'))
        
        # デフォルト値の設定
        fitness_level = data.get('fitness_level', 'beginner')
        preferred_language = data.get('preferred_language', 'ja')
        target_goals = data.get('target_goals', [])
        if isinstance(target_goals, str):
            target_goals = target_goals.split(',')
        if not target_goals:
            target_goals = ['general_fitness']  # デフォルト目標
        
        physical_limitations = data.get('physical_limitations', [])
        if isinstance(physical_limitations, str):
            physical_limitations = physical_limitations.split(',')
        
        user_profile = UserProfile(
            user_id=user_id,
            name=name,
            fitness_level=fitness_level,
            target_goals=target_goals,
            physical_limitations=physical_limitations,
            preferred_language=preferred_language
        )
        
        trainer.add_user_profile(user_profile)
        trainer.save_config()
        
        if request.is_json:
            return jsonify({
                "status": "success", 
                "message": "ユーザーが登録されました",
                "user_id": user_id
            })
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
                    # 画像のサイズをログに記録（デバッグ用）
                    logger.info(f"受信した画像サイズ: {image.shape if image is not None else 'None'}")
                    
                    # 姿勢検出器を使用してキーポイントを検出
                    detector = get_posture_detector()
                    if detector:
                        detected_keypoints = detector.detect_keypoints(image)
                        logger.info(f"検出されたキーポイント数: {len(detected_keypoints) if detected_keypoints else 0}")
                        if detected_keypoints:
                            keypoints = detected_keypoints
                            # キーポイントのサンプルをログに記録（デバッグ用）
                            sample_keys = list(detected_keypoints.keys())[:3]
                            for key in sample_keys:
                                logger.info(f"キーポイント {key}: {detected_keypoints[key]}")
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
        
        # 姿勢タイプが指定されていない場合、または'auto'の場合、自動判定
        if not posture_type or posture_type == 'auto' or posture_type == 'standing':
            try:
                detected_type, confidence = posture_type_detector.get_posture_type_confidence(keypoints_tuple)
                posture_type = detected_type
                logger.info(f"姿勢タイプを自動判定: {detected_type} (信頼度: {confidence:.2f})")
            except Exception as e:
                logger.warning(f"姿勢タイプ自動判定エラー: {e}, デフォルト値を使用")
                posture_type = 'standing_front'
        
        # 姿勢を分析
        analysis = posture_analyzer.analyze_posture(keypoints_tuple, posture_type)
        
        # 結果を保存
        posture_analyzer.save_analysis(user_id, analysis)
        
        # 画像が提供されている場合、診断結果レポート画像を生成
        report_image_url = None
        visualized_image_url = None
        if image is not None:
            try:
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                
                # 可視化ディレクトリを確実に作成
                vis_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'visualizations')
                os.makedirs(vis_dir, exist_ok=True)
                logger.info(f"可視化ディレクトリ: {vis_dir}, 存在: {os.path.exists(vis_dir)}")
                
                # 通常の可視化画像も生成（キーポイントと骨格を直接描画）
                try:
                    visualized_image = posture_visualizer.visualize_posture(image, keypoints, analysis, draw_text=False)
                    vis_filename = f"analyzed_{user_id}_{timestamp}.png"
                    vis_path = os.path.join(vis_dir, vis_filename)
                    success1 = cv2.imwrite(vis_path, visualized_image)
                    if success1 and os.path.exists(vis_path):
                        visualized_image_url = url_for('uploaded_file', filename=f'visualizations/{vis_filename}')
                        logger.info(f"可視化画像を保存: {vis_path}, URL: {visualized_image_url}")
                    else:
                        logger.error(f"可視化画像の保存に失敗: {vis_path}")
                        visualized_image_url = None
                except Exception as e:
                    logger.error(f"可視化画像生成エラー: {e}", exc_info=True)
                    visualized_image_url = None
                
                # 診断結果レポート画像を生成
                try:
                    report_image = posture_visualizer.create_diagnosis_report_image(image, keypoints, analysis)
                    report_filename = f"report_{user_id}_{timestamp}.png"
                    report_path = os.path.join(vis_dir, report_filename)
                    
                    success2 = cv2.imwrite(report_path, report_image)
                    if success2:
                        # ファイルが実際に保存されたか確認
                        if os.path.exists(report_path):
                            file_size = os.path.getsize(report_path)
                            logger.info(f"診断結果レポート画像を保存: {report_path}, サイズ: {file_size} bytes")
                            report_image_url = url_for('uploaded_file', filename=f'visualizations/{report_filename}')
                            logger.info(f"診断結果レポート画像URL: {report_image_url}")
                        else:
                            logger.error(f"画像ファイルが保存されませんでした: {report_path}")
                            report_image_url = None
                    else:
                        logger.error(f"cv2.imwriteが失敗: {report_path}")
                        report_image_url = None
                except Exception as e:
                    logger.error(f"診断結果レポート画像生成エラー: {e}", exc_info=True)
                    report_image_url = None
                
                # X線透視風の画像診断
                xray_image_url = None
                try:
                    xray_image = posture_visualizer.create_xray_visualization(image, keypoints, analysis)
                    xray_filename = f"xray_{user_id}_{timestamp}.png"
                    xray_path = os.path.join(vis_dir, xray_filename)
                    success_xray = cv2.imwrite(xray_path, xray_image)
                    if success_xray and os.path.exists(xray_path):
                        xray_image_url = url_for('uploaded_file', filename=f'visualizations/{xray_filename}')
                        logger.info(f"X線透視風画像を保存: {xray_path}, URL: {xray_image_url}")
                    else:
                        logger.error(f"X線透視風画像の保存に失敗: {xray_path}")
                        xray_image_url = None
                except Exception as e:
                    logger.error(f"X線透視風画像生成エラー: {e}", exc_info=True)
                    xray_image_url = None
            except Exception as e:
                logger.error(f"画像生成エラー: {e}", exc_info=True)
        
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
                "timestamp": analysis.timestamp.isoformat(),
                "muscle_assessment": getattr(analysis, 'muscle_assessment', {"tight_muscles": [], "stretch_needed": [], "strengthen_needed": []})
            }
        }
        
        if report_image_url:
            response["report_image_url"] = report_image_url
        if visualized_image_url:
            response["visualized_image_url"] = visualized_image_url
        if xray_image_url:
            response["xray_image_url"] = xray_image_url
        
        logger.info(f"姿勢分析レスポンス: report_image_url={report_image_url}, visualized_image_url={visualized_image_url}, xray_image_url={xray_image_url}")
        
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
            response_data = {
                "status": "success",
                "message": "姿勢分析が完了しました",
                "file_url": f"/uploads/{'videos' if is_video_file(filename) else 'images'}/{safe_filename}",
                "analysis": result.get('analysis')
            }
            if 'report_image_url' in result:
                response_data['report_image_url'] = result['report_image_url']
            if 'visualized_image_url' in result:
                response_data['visualized_image_url'] = result['visualized_image_url']
            return jsonify(response_data)
        else:
            return jsonify(result), 500
    
    except Exception as e:
        logger.error(f"ファイルアップロードエラー: {e}", exc_info=True)
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"エラー詳細:\n{error_details}")
        return jsonify({"status": "error", "message": str(e), "details": error_details}), 500


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
        
        # 姿勢タイプが指定されていない場合、自動判定
        if not posture_type or posture_type == 'auto' or posture_type == 'standing':
            try:
                detected_type, confidence = posture_type_detector.get_posture_type_confidence(keypoints_tuple)
                posture_type = detected_type
                logger.info(f"姿勢タイプを自動判定: {detected_type} (信頼度: {confidence:.2f})")
            except Exception as e:
                logger.warning(f"姿勢タイプ自動判定エラー: {e}, デフォルト値を使用")
                posture_type = 'standing_front'
        
        # 姿勢を分析
        analysis = posture_analyzer.analyze_posture(keypoints_tuple, posture_type)
        posture_analyzer.save_analysis(user_id, analysis)
        
        # 画像に姿勢評価を可視化
        visualized_image_url = None
        report_image_url = None
        
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            base_filename = os.path.splitext(os.path.basename(image_path))[0]
            
            # 可視化ディレクトリを確実に作成
            vis_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'visualizations')
            os.makedirs(vis_dir, exist_ok=True)
            logger.info(f"可視化ディレクトリ: {vis_dir}, 存在: {os.path.exists(vis_dir)}")
            
            # 通常の可視化画像（キーポイントと骨格を直接描画）
            try:
                visualized_image = posture_visualizer.visualize_posture(image, detected_keypoints, analysis, draw_text=False)
                output_filename = f"analyzed_{timestamp}_{base_filename}.png"
                output_path = os.path.join(vis_dir, output_filename)
                success1 = cv2.imwrite(output_path, visualized_image)
                if success1 and os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    visualized_image_url = url_for('uploaded_file', filename=f'visualizations/{output_filename}')
                    logger.info(f"可視化画像を保存: {output_path}, サイズ: {file_size} bytes, URL: {visualized_image_url}")
                else:
                    logger.error(f"可視化画像の保存に失敗: {output_path}")
                    visualized_image_url = None
            except Exception as e:
                logger.error(f"可視化画像生成エラー: {e}", exc_info=True)
                visualized_image_url = None
            
            # 診断結果レポート画像（問題点・改善提案を含む）
            try:
                report_image = posture_visualizer.create_diagnosis_report_image(image, detected_keypoints, analysis)
                report_filename = f"report_{timestamp}_{base_filename}.png"
                report_path = os.path.join(vis_dir, report_filename)
                success2 = cv2.imwrite(report_path, report_image)
                if success2 and os.path.exists(report_path):
                    file_size = os.path.getsize(report_path)
                    report_image_url = url_for('uploaded_file', filename=f'visualizations/{report_filename}')
                    logger.info(f"診断結果レポート画像を保存: {report_path}, サイズ: {file_size} bytes, URL: {report_image_url}")
                else:
                    logger.error(f"診断結果レポート画像の保存に失敗: {report_path}, success={success2}, exists={os.path.exists(report_path) if report_path else False}")
                    report_image_url = None
            except Exception as e:
                logger.error(f"診断結果レポート画像生成エラー: {e}", exc_info=True)
                report_image_url = None
            
            # X線透視風の画像診断
            xray_image_url = None
            try:
                xray_image = posture_visualizer.create_xray_visualization(image, detected_keypoints, analysis)
                xray_filename = f"xray_{timestamp}_{base_filename}.png"
                xray_path = os.path.join(vis_dir, xray_filename)
                success_xray = cv2.imwrite(xray_path, xray_image)
                if success_xray and os.path.exists(xray_path):
                    file_size_xray = os.path.getsize(xray_path)
                    xray_image_url = url_for('uploaded_file', filename=f'visualizations/{xray_filename}')
                    logger.info(f"X線透視風画像を保存: {xray_path}, サイズ: {file_size_xray} bytes, URL: {xray_image_url}")
                else:
                    logger.error(f"X線透視風画像の保存に失敗: {xray_path}")
                    xray_image_url = None
            except Exception as e:
                logger.error(f"X線透視風画像生成エラー: {e}", exc_info=True)
                xray_image_url = None
            
        except Exception as e:
            logger.error(f"画像可視化エラー: {e}", exc_info=True)
            visualized_image_url = None
            report_image_url = None
            xray_image_url = None
        
        result = {
            "status": "success",
            "analysis": {
                "overall_score": analysis.overall_score,
                "posture_type": analysis.posture_type,
                "issues": analysis.issues,
                "recommendations": analysis.recommendations,
                "alignment_scores": analysis.alignment_scores,
                "keypoint_angles": analysis.keypoint_angles,
                "timestamp": analysis.timestamp.isoformat(),
                "muscle_assessment": getattr(analysis, 'muscle_assessment', {"tight_muscles": [], "stretch_needed": [], "strengthen_needed": []})
            }
        }
        
        # URLを追加（Noneでも追加）
        if visualized_image_url:
            result["visualized_image_url"] = visualized_image_url
        if report_image_url:
            result["report_image_url"] = report_image_url
        if xray_image_url:
            result["xray_image_url"] = xray_image_url
        
        logger.info(f"analyze_image_posture結果: visualized_image_url={visualized_image_url}, report_image_url={report_image_url}, xray_image_url={xray_image_url}")
        
        return result
    
    except Exception as e:
        logger.error(f"画像姿勢分析エラー: {e}", exc_info=True)
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"エラー詳細:\n{error_details}")
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
        
        # 最初のフレームを取得してレポート画像を生成
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, first_frame = cap.read()
        report_image_url = None
        
        if ret and first_frame is not None:
            try:
                # 最初のフレームからキーポイントを再検出
                first_keypoints = detector.detect_keypoints(first_frame)
                if first_keypoints:
                    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                    base_filename = os.path.splitext(os.path.basename(video_path))[0]
                    
                    # 最終分析結果を作成（一時的に）
                    temp_analysis = PostureAnalysis(
                        timestamp=datetime.datetime.now(),
                        overall_score=avg_score,
                        posture_type=posture_type,
                        issues=list(unique_issues.values()),
                        recommendations=unique_recommendations,
                        alignment_scores=analyses[0].alignment_scores if analyses else {},
                        keypoint_angles=analyses[0].keypoint_angles if analyses else {},
                        detailed_metrics=analyses[0].detailed_metrics if analyses else {},
                        muscle_assessment=analyses[0].muscle_assessment if analyses and hasattr(analyses[0], 'muscle_assessment') else {"tight_muscles": [], "stretch_needed": [], "strengthen_needed": []}
                    )
                    
                    # 可視化ディレクトリを確実に作成
                    vis_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'visualizations')
                    os.makedirs(vis_dir, exist_ok=True)
                    
                    # 診断結果レポート画像を生成
                    report_image = posture_visualizer.create_diagnosis_report_image(
                        first_frame, first_keypoints, temp_analysis
                    )
                    report_filename = f"report_{timestamp}_{base_filename}.png"
                    report_path = os.path.join(vis_dir, report_filename)
                    success = cv2.imwrite(report_path, report_image)
                    if success and os.path.exists(report_path):
                        report_image_url = url_for('uploaded_file', filename=f'visualizations/{report_filename}')
                        logger.info(f"動画診断結果レポート画像を保存: {report_path}, URL: {report_image_url}")
                    else:
                        logger.error(f"動画診断結果レポート画像の保存に失敗: {report_path}")
                        report_image_url = None
            except Exception as e:
                logger.warning(f"動画診断結果レポート画像生成エラー: {e}")
        
        # 最終分析結果を作成
        final_analysis = PostureAnalysis(
            timestamp=datetime.datetime.now(),
            posture_type=posture_type,
            overall_score=avg_score,
            issues=list(unique_issues.values()),
            recommendations=unique_recommendations[:5],  # 上位5件
            keypoint_angles=analyses[0].keypoint_angles if analyses else {},
            alignment_scores=analyses[0].alignment_scores if analyses else {},
            detailed_metrics=analyses[0].detailed_metrics if analyses else {},
            muscle_assessment=analyses[0].muscle_assessment if analyses and hasattr(analyses[0], 'muscle_assessment') else {"tight_muscles": [], "stretch_needed": [], "strengthen_needed": []}
        )
        
        posture_analyzer.save_analysis(user_id, final_analysis)
        
        result = {
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
                "total_frames": total_frames,
                "muscle_assessment": getattr(final_analysis, 'muscle_assessment', {"tight_muscles": [], "stretch_needed": [], "strengthen_needed": []})
            }
        }
        
        if 'report_image_url' in locals() and report_image_url:
            result["report_image_url"] = report_image_url
        
        return result
    
    except Exception as e:
        logger.error(f"動画姿勢分析エラー: {e}")
        return {"status": "error", "message": str(e)}


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """アップロードされたファイルを提供"""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # ファイルが存在するか確認
        if not os.path.exists(file_path):
            logger.warning(f"ファイルが見つかりません: {file_path}")
            return "File not found", 404
        
        # ディレクトリトラバーサル攻撃を防ぐ
        upload_folder_abs = os.path.abspath(app.config['UPLOAD_FOLDER'])
        file_path_abs = os.path.abspath(file_path)
        if not file_path_abs.startswith(upload_folder_abs):
            logger.warning(f"不正なパスアクセス: {file_path}")
            return "Forbidden", 403
        
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        logger.error(f"ファイル提供エラー: {e}", exc_info=True)
        return f"Error: {str(e)}", 500

@app.route('/api/posture/pdf/<user_id>', methods=['POST'])
def api_generate_pdf(user_id):
    """診断結果をPDF形式で生成"""
    try:
        data = request.json
        analysis = data.get('analysis')
        
        if not analysis:
            return jsonify({"status": "error", "message": "分析結果が必要です"}), 400
        
        # ユーザー名を取得
        user_name = data.get('user_name', None)
        
        # 画像パスを取得
        report_image_url = data.get('report_image_url', None)
        xray_image_url = data.get('xray_image_url', None)
        visualized_image_url = data.get('visualized_image_url', None)
        
        # URLからパスを取得
        report_image_path = None
        xray_image_path = None
        visualized_image_path = None
        
        if report_image_url:
            # URLからパスを抽出（例: /uploads/visualizations/report_xxx.png）
            if report_image_url.startswith('/uploads/'):
                report_image_path = os.path.join(app.config['UPLOAD_FOLDER'], report_image_url.replace('/uploads/', ''))
        
        if xray_image_url:
            if xray_image_url.startswith('/uploads/'):
                xray_image_path = os.path.join(app.config['UPLOAD_FOLDER'], xray_image_url.replace('/uploads/', ''))
        
        if visualized_image_url:
            if visualized_image_url.startswith('/uploads/'):
                visualized_image_path = os.path.join(app.config['UPLOAD_FOLDER'], visualized_image_url.replace('/uploads/', ''))
        
        # PDFファイル名を生成
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f"posture_report_{user_id}_{timestamp}.pdf"
        pdf_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'pdfs')
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        
        # PDFを生成
        success = pdf_generator.generate_diagnosis_pdf(
            output_path=pdf_path,
            analysis=analysis,
            user_id=user_id,
            user_name=user_name,
            report_image_path=report_image_path,
            xray_image_path=xray_image_path,
            visualized_image_path=visualized_image_path
        )
        
        if success and os.path.exists(pdf_path):
            pdf_url = url_for('uploaded_file', filename=f'pdfs/{pdf_filename}')
            logger.info(f"PDFを生成しました: {pdf_path}, URL: {pdf_url}")
            return jsonify({
                "status": "success",
                "pdf_url": pdf_url,
                "message": "PDFを生成しました"
            })
        else:
            logger.error(f"PDF生成に失敗しました: {pdf_path}")
            return jsonify({"status": "error", "message": "PDF生成に失敗しました"}), 500
    
    except Exception as e:
        logger.error(f"PDF生成APIエラー: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

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