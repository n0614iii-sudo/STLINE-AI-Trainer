#!/usr/bin/env python3
"""
姿勢可視化モジュール
画像に姿勢評価、アライメント、キーポイントを描画
"""

import cv2
import numpy as np
import math
from typing import Dict, Tuple, List, Optional
from posture_analyzer import PostureKeypoint, PostureAnalysis
from PIL import Image, ImageDraw, ImageFont
import os
import logging

logger = logging.getLogger(__name__)


class PostureVisualizer:
    """姿勢可視化クラス"""
    
    # キーポイント接続（骨格構造）
    SKELETON_CONNECTIONS = [
        # 頭部
        ("nose", "left_eye"), ("nose", "right_eye"),
        ("left_eye", "left_ear"), ("right_eye", "right_ear"),
        # 上半身
        ("left_shoulder", "right_shoulder"),  # 肩
        ("left_shoulder", "left_elbow"), ("left_elbow", "left_wrist"),
        ("right_shoulder", "right_elbow"), ("right_elbow", "right_wrist"),
        # 体幹
        ("left_shoulder", "left_hip"), ("right_shoulder", "right_hip"),
        ("left_hip", "right_hip"),  # 骨盤
        # 下半身
        ("left_hip", "left_knee"), ("left_knee", "left_ankle"),
        ("right_hip", "right_knee"), ("right_knee", "right_ankle"),
    ]
    
    # キーポイントの色（BGR形式）
    KEYPOINT_COLORS = {
        "head": (255, 200, 0),  # 黄色
        "shoulder": (0, 255, 0),  # 緑
        "elbow": (255, 0, 255),  # マゼンタ
        "wrist": (0, 255, 255),  # シアン
        "hip": (255, 0, 0),  # 青
        "knee": (0, 165, 255),  # オレンジ
        "ankle": (128, 0, 128),  # 紫
    }
    
    def __init__(self):
        """可視化器を初期化"""
        # 日本語フォントのパスを取得
        self.japanese_font = self._get_japanese_font()
    
    def _get_japanese_font(self, size=20):
        """日本語フォントを取得"""
        try:
            # システムフォントを試す（macOS, Linux, Windows）
            font_paths = [
                # macOS
                '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
                '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc',
                '/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
                # Linux
                '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                # Windows
                'C:/Windows/Fonts/msgothic.ttc',
                'C:/Windows/Fonts/msmincho.ttc',
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        return ImageFont.truetype(font_path, size)
                    except:
                        continue
            
            # フォールバック: デフォルトフォント
            return ImageFont.load_default()
        except:
            return ImageFont.load_default()
    
    def _put_japanese_text(self, image: np.ndarray, text: str, position: Tuple[int, int], 
                          font_size: int = 20, color: Tuple[int, int, int] = (255, 255, 255),
                          thickness: int = 2) -> np.ndarray:
        """
        PILを使用して日本語テキストを描画
        
        Args:
            image: OpenCV画像（BGR形式）
            text: 描画するテキスト
            position: 描画位置 (x, y)
            font_size: フォントサイズ
            color: 色 (B, G, R)
            thickness: 線の太さ（PILでは使用しないが互換性のため）
        
        Returns:
            描画された画像
        """
        try:
            # 画像が空でないことを確認
            if image is None or image.size == 0:
                logger.warning("空の画像が渡されました")
                return image
            
            # OpenCV画像をPIL画像に変換（BGR -> RGB）
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_image)
            
            # フォントを取得
            font = self._get_japanese_font(font_size)
            
            # テキストを描画
            # PILの色はRGB形式なので、BGRからRGBに変換
            rgb_color = (color[2], color[1], color[0])
            draw.text(position, text, font=font, fill=rgb_color)
            
            # PIL画像をOpenCV画像に変換（RGB -> BGR）
            result = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            return result
        except Exception as e:
            logger.warning(f"日本語テキスト描画エラー（フォールバック）: {e}")
            # エラー時はOpenCVのデフォルトフォントで描画（英語のみ）
            try:
                cv2.putText(image, text.encode('utf-8', 'replace').decode('utf-8', 'replace'), 
                           position, cv2.FONT_HERSHEY_SIMPLEX, font_size / 20.0, color, thickness)
            except Exception as e2:
                logger.error(f"テキスト描画エラー: {e2}")
            return image
    
    def _get_text_size_japanese(self, text: str, font_size: int = 20) -> Tuple[int, int]:
        """日本語テキストのサイズを取得"""
        try:
            font = self._get_japanese_font(font_size)
            # ダミー画像でサイズを測定
            dummy_img = Image.new('RGB', (1000, 1000), (0, 0, 0))
            draw = ImageDraw.Draw(dummy_img)
            bbox = draw.textbbox((0, 0), text, font=font)
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            return (width, height)
        except:
            # フォールバック: OpenCVのサイズ計算
            font_scale = font_size / 20.0
            (width, height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)
            return (width, height)
    
    def visualize_posture(
        self,
        image: np.ndarray,
        keypoints: Dict[str, Tuple[float, float, float]],
        analysis: PostureAnalysis,
        draw_text: bool = True
    ) -> np.ndarray:
        """
        画像に姿勢評価を可視化（キーポイントと骨格を直接描画）
        
        Args:
            image: 入力画像（BGR形式）
            keypoints: キーポイント辞書 {name: (x, y, confidence)}
            analysis: 姿勢分析結果
            draw_text: テキストを描画するか（デフォルト: True）
        
        Returns:
            可視化された画像
        """
        # 画像をコピー
        vis_image = image.copy()
        
        # 画像が空でないことを確認
        if vis_image is None or vis_image.size == 0:
            logger.warning("空の画像が渡されました")
            return vis_image
        
        # キーポイントを正規化
        normalized_keypoints = self._normalize_keypoints(keypoints)
        
        # 骨格を描画（太く、見やすく）
        vis_image = self._draw_skeleton(vis_image, normalized_keypoints, line_thickness=3)
        
        # キーポイントを描画（大きく、見やすく）
        vis_image = self._draw_keypoints(vis_image, normalized_keypoints, point_size=8)
        
        # アライメント線を描画
        vis_image = self._draw_alignment_lines(vis_image, normalized_keypoints, analysis)
        
        # テキストを描画する場合のみ
        if draw_text:
            # 評価項目を描画
            vis_image = self._draw_evaluation_text(vis_image, analysis)
            
            # スコアと問題点を描画
            vis_image = self._draw_score_and_issues(vis_image, analysis)
        
        return vis_image
    
    def create_diagnosis_report_image(
        self,
        image: np.ndarray,
        keypoints: Dict[str, Tuple[float, float, float]],
        analysis: PostureAnalysis
    ) -> np.ndarray:
        """
        診断結果レポート画像を生成（問題点・改善提案を含む）
        
        Args:
            image: 入力画像（BGR形式）
            keypoints: キーポイント辞書 {name: (x, y, confidence)}
            analysis: 姿勢分析結果
        
        Returns:
            診断結果レポート画像（濃い背景、見やすいテキスト）
        """
        h, w = image.shape[:2]
        
        # 元の画像に姿勢評価を可視化
        analyzed_image = self.visualize_posture(image, keypoints, analysis)
        
        # 診断結果パネルの高さを計算（問題点、改善提案、筋肉評価を含む）
        panel_height = 500
        if analysis.issues:
            panel_height += len(analysis.issues) * 50
        if analysis.recommendations:
            panel_height += len(analysis.recommendations) * 40
        
        # 筋肉評価の高さを追加
        muscle_assessment = getattr(analysis, 'muscle_assessment', {})
        if muscle_assessment:
            if muscle_assessment.get('tight_muscles'):
                panel_height += len(muscle_assessment['tight_muscles']) * 45
            if muscle_assessment.get('stretch_needed'):
                panel_height += len(muscle_assessment['stretch_needed']) * 45
            if muscle_assessment.get('strengthen_needed'):
                panel_height += len(muscle_assessment['strengthen_needed']) * 45
        
        # 新しい画像を作成（元の画像 + 診断結果パネル）
        report_image = np.zeros((h + panel_height, w, 3), dtype=np.uint8)
        
        # 元の画像をコピー
        report_image[:h, :w] = analyzed_image
        
        # 診断結果パネルを描画（濃い背景）
        panel_y = h
        cv2.rectangle(report_image, (0, panel_y), (w, h + panel_height), (20, 20, 30), -1)
        cv2.rectangle(report_image, (0, panel_y), (w, h + panel_height), (60, 60, 80), 2)
        
        y_offset = panel_y + 30
        x_offset = 30
        
        # タイトル
        title_text = "姿勢診断結果レポート"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale_title = 1.2
        thickness_title = 3
        (title_width, title_height), _ = cv2.getTextSize(title_text, font, font_scale_title, thickness_title)
        
        # タイトルの背景
        cv2.rectangle(report_image,
                     (x_offset - 10, y_offset - title_height - 10),
                     (x_offset + title_width + 10, y_offset + 10),
                     (40, 40, 60), -1)
        cv2.rectangle(report_image,
                     (x_offset - 10, y_offset - title_height - 10),
                     (x_offset + title_width + 10, y_offset + 10),
                     (100, 150, 255), 2)
        
        cv2.putText(report_image, title_text, (x_offset, y_offset), 
                   font, font_scale_title, (255, 255, 255), thickness_title)
        y_offset += title_height + 40
        
        # 総合スコア
        score_text = f"総合スコア: {int(analysis.overall_score * 100)}/100"
        score_color = self._get_score_color(analysis.overall_score)
        font_size_score = 20
        score_width, score_height = self._get_text_size_japanese(score_text, font_size_score)
        
        # スコアの背景
        cv2.rectangle(report_image,
                     (x_offset - 10, y_offset - score_height - 10),
                     (x_offset + score_width + 10, y_offset + score_height + 10),
                     (30, 30, 40), -1)
        cv2.rectangle(report_image,
                     (x_offset - 10, y_offset - score_height - 10),
                     (x_offset + score_width + 10, y_offset + score_height + 10),
                     score_color, 2)
        
        report_image = self._put_japanese_text(report_image, score_text, (x_offset, y_offset), 
                                               font_size=font_size_score, color=score_color, thickness=3)
        y_offset += score_height + 40
        
        # 検出された問題
        if analysis.issues:
            issues_title = "検出された問題"
            font_size_issues_title = 18
            issues_title_width, issues_title_height = self._get_text_size_japanese(issues_title, font_size_issues_title)
            
            # タイトルの背景
            cv2.rectangle(report_image,
                         (x_offset - 5, y_offset - issues_title_height - 5),
                         (x_offset + issues_title_width + 5, y_offset + 5),
                         (60, 30, 30), -1)
            cv2.rectangle(report_image,
                         (x_offset - 5, y_offset - issues_title_height - 5),
                         (x_offset + issues_title_width + 5, y_offset + 5),
                         (255, 100, 100), 2)
            
            report_image = self._put_japanese_text(report_image, issues_title, (x_offset, y_offset), 
                                                   font_size=font_size_issues_title, color=(255, 200, 200), thickness=2)
            y_offset += issues_title_height + 25
            
            for issue in analysis.issues:
                # 深刻度バッジ
                severity_text = issue["severity"].upper()
                severity_color = self._get_severity_color(issue["severity"])
                font_scale_severity = 0.6
                thickness_severity = 2
                (severity_width, severity_height), _ = cv2.getTextSize(severity_text, font, font_scale_severity, thickness_severity)
                
                # バッジの背景
                badge_x = x_offset
                badge_y = y_offset
                cv2.rectangle(report_image,
                             (badge_x - 5, badge_y - severity_height - 5),
                             (badge_x + severity_width + 5, badge_y + 5),
                             (int(severity_color[0] * 0.3), int(severity_color[1] * 0.3), int(severity_color[2] * 0.3)), -1)
                cv2.rectangle(report_image,
                             (badge_x - 5, badge_y - severity_height - 5),
                             (badge_x + severity_width + 5, badge_y + 5),
                             severity_color, 2)
                
                cv2.putText(report_image, severity_text, (badge_x, badge_y), 
                           font, font_scale_severity, severity_color, thickness_severity)
                
                # 問題の説明
                desc_x = badge_x + severity_width + 20
                desc_text = issue["description"]
                font_size_desc = 14
                report_image = self._put_japanese_text(report_image, desc_text, (desc_x, badge_y), 
                                                      font_size=font_size_desc, color=(255, 255, 255), thickness=2)
                y_offset += severity_height + 15
                
                # 影響の説明
                if "impact" in issue:
                    impact_text = f"  → {issue['impact']}"
                    font_size_impact = 12
                    report_image = self._put_japanese_text(report_image, impact_text, (desc_x, y_offset), 
                                                          font_size=font_size_impact, color=(200, 200, 200), thickness=1)
                    y_offset += 25
                else:
                    y_offset += 10
        
        y_offset += 20
        
        # 改善提案
        if analysis.recommendations:
            rec_title = "改善提案"
            font_size_rec_title = 18
            rec_title_width, rec_title_height = self._get_text_size_japanese(rec_title, font_size_rec_title)
            
            # タイトルの背景
            cv2.rectangle(report_image,
                         (x_offset - 5, y_offset - rec_title_height - 5),
                         (x_offset + rec_title_width + 5, y_offset + 5),
                         (30, 60, 30), -1)
            cv2.rectangle(report_image,
                         (x_offset - 5, y_offset - rec_title_height - 5),
                         (x_offset + rec_title_width + 5, y_offset + 5),
                         (100, 255, 100), 2)
            
            report_image = self._put_japanese_text(report_image, rec_title, (x_offset, y_offset), 
                                                   font_size=font_size_rec_title, color=(200, 255, 200), thickness=2)
            y_offset += rec_title_height + 25
            
            for i, rec in enumerate(analysis.recommendations):
                rec_text = f"  • {rec}"
                font_size_rec = 13
                rec_width, rec_height = self._get_text_size_japanese(rec_text, font_size_rec)
                
                # テキストの背景
                cv2.rectangle(report_image,
                             (x_offset - 3, y_offset - rec_height - 3),
                             (x_offset + rec_width + 3, y_offset + rec_height + 3),
                             (25, 40, 25), -1)
                
                report_image = self._put_japanese_text(report_image, rec_text, (x_offset, y_offset), 
                                                       font_size=font_size_rec, color=(200, 255, 200), thickness=2)
                y_offset += rec_height + 20
        
        y_offset += 20
        
        # 筋肉評価
        muscle_assessment = getattr(analysis, 'muscle_assessment', {})
        if muscle_assessment:
            # 硬い可能性のある筋肉
            if muscle_assessment.get('tight_muscles'):
                tight_title = "硬い可能性のある筋肉"
                font_size_tight_title = 18
                tight_title_width, tight_title_height = self._get_text_size_japanese(tight_title, font_size_tight_title)
                
                # タイトルの背景
                cv2.rectangle(report_image,
                             (x_offset - 5, y_offset - tight_title_height - 5),
                             (x_offset + tight_title_width + 5, y_offset + 5),
                             (60, 40, 20), -1)
                cv2.rectangle(report_image,
                             (x_offset - 5, y_offset - tight_title_height - 5),
                             (x_offset + tight_title_width + 5, y_offset + 5),
                             (255, 150, 50), 2)
                
                report_image = self._put_japanese_text(report_image, tight_title, (x_offset, y_offset), 
                                                       font_size=font_size_tight_title, color=(255, 200, 150), thickness=2)
                y_offset += tight_title_height + 25
                
                for muscle in muscle_assessment['tight_muscles']:
                    # 筋肉名
                    muscle_name = muscle.get('name', '')
                    severity = muscle.get('severity', 'medium')
                    severity_color = self._get_severity_color(severity)
                    font_scale_muscle = 0.7
                    thickness_muscle = 2
                    (muscle_width, muscle_height), _ = cv2.getTextSize(muscle_name, font, font_scale_muscle, thickness_muscle)
                    
                    # 背景
                    cv2.rectangle(report_image,
                                 (x_offset - 3, y_offset - muscle_height - 3),
                                 (x_offset + muscle_width + 3, y_offset + 3),
                                 (int(severity_color[0] * 0.2), int(severity_color[1] * 0.2), int(severity_color[2] * 0.2)), -1)
                    
                    font_size_muscle = 14
                    report_image = self._put_japanese_text(report_image, f"  • {muscle_name}", (x_offset, y_offset), 
                                                          font_size=font_size_muscle, color=severity_color, thickness=2)
                    muscle_height = self._get_text_size_japanese(f"  • {muscle_name}", font_size_muscle)[1]
                    y_offset += muscle_height + 15
                    
                    # 理由
                    if 'reason' in muscle:
                        reason_text = f"    → {muscle['reason']}"
                        font_size_reason = 12
                        report_image = self._put_japanese_text(report_image, reason_text, (x_offset, y_offset), 
                                                              font_size=font_size_reason, color=(200, 200, 200), thickness=1)
                        y_offset += 20
                    else:
                        y_offset += 5
            
            y_offset += 15
            
            # ストレッチが必要な筋肉
            if muscle_assessment.get('stretch_needed'):
                stretch_title = "ストレッチが必要な筋肉"
                font_size_stretch_title = 18
                stretch_title_width, stretch_title_height = self._get_text_size_japanese(stretch_title, font_size_stretch_title)
                
                # タイトルの背景
                cv2.rectangle(report_image,
                             (x_offset - 5, y_offset - stretch_title_height - 5),
                             (x_offset + stretch_title_width + 5, y_offset + 5),
                             (20, 60, 40), -1)
                cv2.rectangle(report_image,
                             (x_offset - 5, y_offset - stretch_title_height - 5),
                             (x_offset + stretch_title_width + 5, y_offset + 5),
                             (50, 200, 100), 2)
                
                report_image = self._put_japanese_text(report_image, stretch_title, (x_offset, y_offset), 
                                                      font_size=font_size_stretch_title, color=(150, 255, 200), thickness=2)
                y_offset += stretch_title_height + 25
                
                for stretch in muscle_assessment['stretch_needed']:
                    muscle_name = stretch.get('muscle', '')
                    method = stretch.get('method', '')
                    frequency = stretch.get('frequency', '')
                    
                    # 筋肉名と方法
                    stretch_text = f"  • {muscle_name}: {method}"
                    font_scale_stretch = 0.65
                    thickness_stretch = 2
                    (stretch_width, stretch_height), baseline = cv2.getTextSize(stretch_text, font, font_scale_stretch, thickness_stretch)
                    
                    # 背景
                    cv2.rectangle(report_image,
                                 (x_offset - 3, y_offset - stretch_height - 3),
                                 (x_offset + stretch_width + 3, y_offset + baseline + 3),
                                 (15, 40, 25), -1)
                    
                    font_size_stretch = 13
                    report_image = self._put_japanese_text(report_image, stretch_text, (x_offset, y_offset), 
                                                          font_size=font_size_stretch, color=(150, 255, 200), thickness=2)
                    stretch_height = self._get_text_size_japanese(stretch_text, font_size_stretch)[1]
                    y_offset += stretch_height + 15
                    
                    # 頻度
                    if frequency:
                        freq_text = f"    頻度: {frequency}"
                        font_size_freq = 12
                        report_image = self._put_japanese_text(report_image, freq_text, (x_offset, y_offset), 
                                                              font_size=font_size_freq, color=(150, 200, 150), thickness=1)
                        y_offset += 20
                    else:
                        y_offset += 5
            
            y_offset += 15
            
            # 強化が必要な筋肉
            if muscle_assessment.get('strengthen_needed'):
                strengthen_title = "強化が必要な筋肉"
                font_size_strengthen_title = 18
                strengthen_title_width, strengthen_title_height = self._get_text_size_japanese(strengthen_title, font_size_strengthen_title)
                
                # タイトルの背景
                cv2.rectangle(report_image,
                             (x_offset - 5, y_offset - strengthen_title_height - 5),
                             (x_offset + strengthen_title_width + 5, y_offset + 5),
                             (40, 20, 60), -1)
                cv2.rectangle(report_image,
                             (x_offset - 5, y_offset - strengthen_title_height - 5),
                             (x_offset + strengthen_title_width + 5, y_offset + 5),
                             (150, 50, 200), 2)
                
                report_image = self._put_japanese_text(report_image, strengthen_title, (x_offset, y_offset), 
                                                      font_size=font_size_strengthen_title, color=(200, 150, 255), thickness=2)
                y_offset += strengthen_title_height + 25
                
                for strengthen in muscle_assessment['strengthen_needed']:
                    muscle_name = strengthen.get('muscle', '')
                    exercise = strengthen.get('exercise', '')
                    frequency = strengthen.get('frequency', '')
                    
                    # 筋肉名とエクササイズ
                    strengthen_text = f"  • {muscle_name}: {exercise}"
                    font_scale_strengthen = 0.65
                    thickness_strengthen = 2
                    (strengthen_width, strengthen_height), baseline = cv2.getTextSize(strengthen_text, font, font_scale_strengthen, thickness_strengthen)
                    
                    # 背景
                    cv2.rectangle(report_image,
                                 (x_offset - 3, y_offset - strengthen_height - 3),
                                 (x_offset + strengthen_width + 3, y_offset + baseline + 3),
                                 (30, 15, 40), -1)
                    
                    font_size_strengthen = 13
                    report_image = self._put_japanese_text(report_image, strengthen_text, (x_offset, y_offset), 
                                                          font_size=font_size_strengthen, color=(200, 150, 255), thickness=2)
                    strengthen_height = self._get_text_size_japanese(strengthen_text, font_size_strengthen)[1]
                    y_offset += strengthen_height + 15
                    
                    # 頻度
                    if frequency:
                        freq_text = f"    頻度: {frequency}"
                        font_size_freq = 12
                        report_image = self._put_japanese_text(report_image, freq_text, (x_offset, y_offset), 
                                                              font_size=font_size_freq, color=(200, 150, 200), thickness=1)
                        y_offset += 20
                    else:
                        y_offset += 5
        
        return report_image
    
    def _normalize_keypoints(self, keypoints: Dict[str, Tuple[float, float, float]]) -> Dict[str, PostureKeypoint]:
        """キーポイントを正規化"""
        normalized = {}
        for name, (x, y, conf) in keypoints.items():
            normalized[name] = PostureKeypoint(x=x, y=y, confidence=conf, name=name)
        return normalized
    
    def _draw_skeleton(self, image: np.ndarray, keypoints: Dict[str, PostureKeypoint], line_thickness: int = 2) -> np.ndarray:
        """骨格を描画（太さを調整可能）"""
        for start_name, end_name in self.SKELETON_CONNECTIONS:
            if start_name in keypoints and end_name in keypoints:
                start = keypoints[start_name]
                end = keypoints[end_name]
                
                # 信頼度が低い場合はスキップ
                if start.confidence < 0.3 or end.confidence < 0.3:
                    continue
                
                # 色を決定
                color = self._get_connection_color(start_name, end_name)
                
                # 線を描画
                cv2.line(
                    image,
                    (int(start.x), int(start.y)),
                    (int(end.x), int(end.y)),
                    color,
                    line_thickness
                )
        
        return image
    
    def _draw_keypoints(self, image: np.ndarray, keypoints: Dict[str, PostureKeypoint], point_size: int = 5) -> np.ndarray:
        """
        キーポイントを描画（信頼度ベースの改善版）
        
        改善点:
        - 信頼度に基づいたサイズと色の調整
        - より正確な位置への描画
        - 視認性の向上
        """
        for name, kp in keypoints.items():
            # 信頼度が低すぎる場合はスキップ
            if kp.confidence < 0.2:
                continue
            
            # 基本色を決定
            base_color = self._get_keypoint_color(name)
            
            # 信頼度に基づいて色の明度を調整
            confidence_factor = min(1.0, max(0.5, kp.confidence))
            color = tuple(int(c * confidence_factor) for c in base_color)
            
            # 信頼度に基づいてサイズを調整
            # 高信頼度: 大きめ、低信頼度: 小さめ
            size_factor = 0.5 + (kp.confidence * 0.5)  # 0.5-1.0の範囲
            actual_size = max(3, int(point_size * size_factor))
            outer_size = actual_size + 2
            
            # 外側の円（白、視認性向上）
            cv2.circle(
                image,
                (int(kp.x), int(kp.y)),
                outer_size,
                (255, 255, 255),
                2
            )
            
            # 内側の円（色付き、信頼度に応じたサイズ）
            cv2.circle(
                image,
                (int(kp.x), int(kp.y)),
                actual_size,
                color,
                -1
            )
            
            # 中心点（高信頼度の場合のみ）
            if kp.confidence > 0.7:
                cv2.circle(
                    image,
                    (int(kp.x), int(kp.y)),
                    2,
                    (255, 255, 255),
                    -1
                )
            
            # 低信頼度の場合は点線で表示
            if kp.confidence < 0.5:
                # 点線の円を描画
                for angle in range(0, 360, 30):
                    rad = math.radians(angle)
                    x1 = int(kp.x + (outer_size - 1) * math.cos(rad))
                    y1 = int(kp.y + (outer_size - 1) * math.sin(rad))
                    x2 = int(kp.x + outer_size * math.cos(rad))
                    y2 = int(kp.y + outer_size * math.sin(rad))
                    cv2.line(image, (x1, y1), (x2, y2), (200, 200, 200), 1)
        
        return image
    
    def _draw_alignment_lines(self, image: np.ndarray, keypoints: Dict[str, PostureKeypoint], analysis: PostureAnalysis) -> np.ndarray:
        """アライメント線を描画"""
        h, w = image.shape[:2]
        
        # 肩の水平線
        if "left_shoulder" in keypoints and "right_shoulder" in keypoints:
            ls = keypoints["left_shoulder"]
            rs = keypoints["right_shoulder"]
            if ls.confidence > 0.3 and rs.confidence > 0.3:
                # 肩の水平線
                y_shoulder = int((ls.y + rs.y) / 2)
                color = self._get_alignment_color(analysis.alignment_scores.get("shoulder_alignment", 0.5))
                cv2.line(image, (0, y_shoulder), (w, y_shoulder), color, 2)
                cv2.putText(image, "Shoulder", (10, y_shoulder - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # 骨盤の水平線
        if "left_hip" in keypoints and "right_hip" in keypoints:
            lh = keypoints["left_hip"]
            rh = keypoints["right_hip"]
            if lh.confidence > 0.3 and rh.confidence > 0.3:
                y_hip = int((lh.y + rh.y) / 2)
                color = self._get_alignment_color(analysis.alignment_scores.get("hip_alignment", 0.5))
                cv2.line(image, (0, y_hip), (w, y_hip), color, 2)
                cv2.putText(image, "Hip", (10, y_hip - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # 背骨の垂直線
        if "left_shoulder" in keypoints and "right_shoulder" in keypoints and \
           "left_hip" in keypoints and "right_hip" in keypoints:
            ls = keypoints["left_shoulder"]
            rs = keypoints["right_shoulder"]
            lh = keypoints["left_hip"]
            rh = keypoints["right_hip"]
            
            if all(kp.confidence > 0.3 for kp in [ls, rs, lh, rh]):
                shoulder_center_x = int((ls.x + rs.x) / 2)
                hip_center_x = int((lh.x + rh.x) / 2)
                spine_y_top = int(min(ls.y, rs.y))
                spine_y_bottom = int(max(lh.y, rh.y))
                
                # 背骨の中心線
                spine_center_x = int((shoulder_center_x + hip_center_x) / 2)
                color = self._get_alignment_color(analysis.alignment_scores.get("spine_alignment", 0.5))
                cv2.line(image, (spine_center_x, spine_y_top), (spine_center_x, spine_y_bottom), color, 2)
                cv2.putText(image, "Spine", (spine_center_x + 5, spine_y_top + 15), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # 頭部の位置
        if "nose" in keypoints and "left_shoulder" in keypoints and "right_shoulder" in keypoints:
            nose = keypoints["nose"]
            ls = keypoints["left_shoulder"]
            rs = keypoints["right_shoulder"]
            if nose.confidence > 0.3 and ls.confidence > 0.3 and rs.confidence > 0.3:
                shoulder_center_x = int((ls.x + rs.x) / 2)
                color = self._get_alignment_color(analysis.alignment_scores.get("head_alignment", 0.5))
                cv2.line(image, (shoulder_center_x, int(ls.y)), (int(nose.x), int(nose.y)), color, 1)
        
        return image
    
    def _draw_evaluation_text(self, image: np.ndarray, analysis: PostureAnalysis) -> np.ndarray:
        """評価項目を描画（見やすく改善）"""
        h, w = image.shape[:2]
        
        # 背景パネル（より濃く、見やすく）
        panel_height = 220
        overlay = image.copy()
        cv2.rectangle(overlay, (0, h - panel_height), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.85, image, 0.15, 0, image)  # より濃い背景
        
        y_offset = h - panel_height + 25
        x_offset = 25
        
        # 総合スコア（大きく、太く、背景付き）
        score_text = f"総合スコア: {int(analysis.overall_score * 100)}/100"
        score_color = self._get_score_color(analysis.overall_score)
        
        # 日本語テキストのサイズを取得
        font_size = 20
        text_width, text_height = self._get_text_size_japanese(score_text, font_size)
        
        # 背景矩形
        cv2.rectangle(image, 
                     (x_offset - 5, y_offset - text_height - 5),
                     (x_offset + text_width + 5, y_offset + text_height + 5),
                     (0, 0, 0), -1)
        cv2.rectangle(image, 
                     (x_offset - 5, y_offset - text_height - 5),
                     (x_offset + text_width + 5, y_offset + text_height + 5),
                     score_color, 2)
        
        # 日本語テキストを描画
        image = self._put_japanese_text(image, score_text, (x_offset, y_offset), 
                                        font_size=font_size, color=score_color, thickness=3)
        
        y_offset += 40
        
        # アライメントスコア（見やすく改善）
        title_text = "評価項目:"
        font_scale_title = 0.7
        thickness_title = 2
        (title_width, title_height), _ = cv2.getTextSize(title_text, font, font_scale_title, thickness_title)
        
        # タイトルの背景
        cv2.rectangle(image,
                     (x_offset - 3, y_offset - title_height - 3),
                     (x_offset + title_width + 3, y_offset + 3),
                     (0, 0, 0), -1)
        
        cv2.putText(image, title_text, (x_offset, y_offset), 
                   font, font_scale_title, (255, 255, 255), thickness_title)
        y_offset += 30
        
        alignment_labels = {
            "shoulder_alignment": "肩の水平度",
            "hip_alignment": "骨盤の水平度",
            "head_alignment": "頭部の位置",
            "spine_alignment": "背骨の整列",
            "knee_alignment": "膝の位置"
        }
        
        for key, label in alignment_labels.items():
            if key in analysis.alignment_scores:
                score = analysis.alignment_scores[key]
                color = self._get_alignment_color(score)
                text = f"  {label}: {int(score * 100)}%"
                
                # テキストの背景を描画
                font_size_item = 12
                text_width, text_height = self._get_text_size_japanese(text, font_size_item)
                
                cv2.rectangle(image,
                             (x_offset - 3, y_offset - text_height - 2),
                             (x_offset + text_width + 3, y_offset + text_height + 2),
                             (0, 0, 0), -1)
                
                image = self._put_japanese_text(image, text, (x_offset, y_offset), 
                                               font_size=font_size_item, color=color, thickness=2)
                y_offset += 25
        
        # 右側に問題点を表示（見やすく改善）
        x_right = w - 350
        y_right = h - panel_height + 25
        
        if analysis.issues:
            title_text = "検出された問題:"
            font_size_issue_title = 14
            title_width, title_height = self._get_text_size_japanese(title_text, font_size_issue_title)
            
            # タイトルの背景
            cv2.rectangle(image,
                         (x_right - 3, y_right - title_height - 3),
                         (x_right + title_width + 3, y_right + 3),
                         (0, 0, 0), -1)
            
            image = self._put_japanese_text(image, title_text, (x_right, y_right), 
                                           font_size=font_size_issue_title, color=(255, 255, 255), thickness=2)
            y_right += 30
            
            for issue in analysis.issues[:3]:  # 最大3件
                severity_color = self._get_severity_color(issue["severity"])
                text = f"  • {issue['description']}"
                
                # テキストの背景を描画
                font_scale_issue = 0.6
                thickness_issue = 2
                (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale_issue, thickness_issue)
                
                # 背景矩形（色付き）
                bg_color = (int(severity_color[0] * 0.3), int(severity_color[1] * 0.3), int(severity_color[2] * 0.3))
                cv2.rectangle(image,
                             (x_right - 5, y_right - text_height - 3),
                             (x_right + text_width + 5, y_right + baseline + 3),
                             bg_color, -1)
                cv2.rectangle(image,
                             (x_right - 5, y_right - text_height - 3),
                             (x_right + text_width + 5, y_right + baseline + 3),
                             severity_color, 1)
                
                cv2.putText(image, text, (x_right, y_right), 
                           font, font_scale_issue, severity_color, thickness_issue)
                y_right += 28
        
        return image
    
    def _draw_score_and_issues(self, image: np.ndarray, analysis: PostureAnalysis) -> np.ndarray:
        """スコアと問題点を右上に描画（見やすく改善）"""
        h, w = image.shape[:2]
        
        # 総合スコアのバッジ（大きく、見やすく）
        score_text = f"{int(analysis.overall_score * 100)}"
        score_color = self._get_score_color(analysis.overall_score)
        
        # 背景円（より大きく）
        circle_center = (w - 70, 70)
        circle_radius = 50
        cv2.circle(image, circle_center, circle_radius, (0, 0, 0), -1)
        cv2.circle(image, circle_center, circle_radius, score_color, 4)
        
        # スコアテキスト（大きく、太く）
        font_scale = 1.5
        thickness = 3
        text_size = cv2.getTextSize(score_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
        text_x = circle_center[0] - text_size[0] // 2
        text_y = circle_center[1] + text_size[1] // 2
        cv2.putText(image, score_text, (text_x, text_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, score_color, thickness)
        
        # "点"のテキスト
        point_text = "点"
        point_size = cv2.getTextSize(point_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        point_x = circle_center[0] + text_size[0] // 2 + 5
        point_y = circle_center[1] + point_size[1] // 2
        cv2.putText(image, point_text, (point_x, point_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, score_color, 2)
        
        return image
    
    def _get_connection_color(self, start_name: str, end_name: str) -> Tuple[int, int, int]:
        """接続の色を取得"""
        if "shoulder" in start_name or "shoulder" in end_name:
            return self.KEYPOINT_COLORS["shoulder"]
        elif "hip" in start_name or "hip" in end_name:
            return self.KEYPOINT_COLORS["hip"]
        elif "knee" in start_name or "knee" in end_name:
            return self.KEYPOINT_COLORS["knee"]
        elif "elbow" in start_name or "elbow" in end_name:
            return self.KEYPOINT_COLORS["elbow"]
        elif "wrist" in start_name or "wrist" in end_name:
            return self.KEYPOINT_COLORS["wrist"]
        elif "ankle" in start_name or "ankle" in end_name:
            return self.KEYPOINT_COLORS["ankle"]
        else:
            return (255, 255, 255)  # 白
    
    def _get_keypoint_color(self, name: str) -> Tuple[int, int, int]:
        """キーポイントの色を取得"""
        if "nose" in name or "eye" in name or "ear" in name:
            return self.KEYPOINT_COLORS["head"]
        elif "shoulder" in name:
            return self.KEYPOINT_COLORS["shoulder"]
        elif "elbow" in name:
            return self.KEYPOINT_COLORS["elbow"]
        elif "wrist" in name:
            return self.KEYPOINT_COLORS["wrist"]
        elif "hip" in name:
            return self.KEYPOINT_COLORS["hip"]
        elif "knee" in name:
            return self.KEYPOINT_COLORS["knee"]
        elif "ankle" in name:
            return self.KEYPOINT_COLORS["ankle"]
        else:
            return (255, 255, 255)
    
    def _get_alignment_color(self, score: float) -> Tuple[int, int, int]:
        """アライメントスコアに基づく色を取得"""
        if score >= 0.8:
            return (0, 255, 0)  # 緑（良好）
        elif score >= 0.6:
            return (0, 165, 255)  # オレンジ（やや問題）
        else:
            return (0, 0, 255)  # 赤（問題あり）
    
    def _get_score_color(self, score: float) -> Tuple[int, int, int]:
        """スコアに基づく色を取得"""
        if score >= 0.8:
            return (0, 255, 0)  # 緑
        elif score >= 0.6:
            return (0, 165, 255)  # オレンジ
        else:
            return (0, 0, 255)  # 赤
    
    def _get_severity_color(self, severity: str) -> Tuple[int, int, int]:
        """深刻度に基づく色を取得"""
        if severity == "high":
            return (0, 0, 255)  # 赤
        elif severity == "medium":
            return (0, 165, 255)  # オレンジ
        else:
            return (255, 255, 0)  # 黄色
    
    def create_xray_visualization(
        self,
        image: np.ndarray,
        keypoints: Dict[str, Tuple[float, float, float]],
        analysis: PostureAnalysis
    ) -> np.ndarray:
        """
        X線透視風の画像診断を生成
        
        Args:
            image: 入力画像（BGR形式）
            keypoints: キーポイント辞書 {name: (x, y, confidence)}
            analysis: 姿勢分析結果
        
        Returns:
            X線透視風の画像
        """
        # 画像をコピー
        xray_image = image.copy()
        
        # 画像が空でないことを確認
        if xray_image is None or xray_image.size == 0:
            logger.warning("空の画像が渡されました")
            return xray_image
        
        h, w = xray_image.shape[:2]
        
        # 背景を暗くする（X線風）
        overlay = xray_image.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, xray_image, 0.3, 0, xray_image)
        
        # キーポイントを正規化
        normalized_keypoints = self._normalize_keypoints(keypoints)
        
        # 骨格を描画（太く、明るく、X線風）
        xray_image = self._draw_skeleton_xray(xray_image, normalized_keypoints)
        
        # キーポイントを描画（大きく、明るく、X線風）
        xray_image = self._draw_keypoints_xray(xray_image, normalized_keypoints)
        
        # アライメント線を描画（明るく）
        xray_image = self._draw_alignment_lines_xray(xray_image, normalized_keypoints, analysis)
        
        # タイトルを追加
        title_text = "X線透視風 姿勢診断"
        title_size = 30
        title_width, title_height = self._get_text_size_japanese(title_text, title_size)
        title_x = (w - title_width) // 2
        title_y = 40
        
        # タイトルの背景
        cv2.rectangle(xray_image,
                     (title_x - 15, title_y - title_height - 10),
                     (title_x + title_width + 15, title_y + 10),
                     (0, 0, 0), -1)
        cv2.rectangle(xray_image,
                     (title_x - 15, title_y - title_height - 10),
                     (title_x + title_width + 15, title_y + 10),
                     (255, 255, 255), 2)
        
        xray_image = self._put_japanese_text(xray_image, title_text, (title_x, title_y),
                                            font_size=title_size, color=(255, 255, 255), thickness=3)
        
        return xray_image
    
    def _draw_skeleton_xray(self, image: np.ndarray, keypoints: Dict[str, PostureKeypoint]) -> np.ndarray:
        """X線風の骨格を描画（明るく、太く）"""
        for start_name, end_name in self.SKELETON_CONNECTIONS:
            if start_name in keypoints and end_name in keypoints:
                start = keypoints[start_name]
                end = keypoints[end_name]
                
                # 信頼度が低い場合はスキップ
                if start.confidence < 0.3 or end.confidence < 0.3:
                    continue
                
                # X線風の色（明るい白/シアン）
                color = (255, 255, 255)  # 白
                
                # 太い線を描画
                cv2.line(
                    image,
                    (int(start.x), int(start.y)),
                    (int(end.x), int(end.y)),
                    color,
                    4
                )
                
                # 外側にグロー効果（薄い線）
                cv2.line(
                    image,
                    (int(start.x), int(start.y)),
                    (int(end.x), int(end.y)),
                    (200, 255, 255),  # 薄いシアン
                    2
                )
        
        return image
    
    def _draw_keypoints_xray(self, image: np.ndarray, keypoints: Dict[str, PostureKeypoint]) -> np.ndarray:
        """X線風のキーポイントを描画（大きく、明るく）"""
        for name, kp in keypoints.items():
            if kp.confidence < 0.3:
                continue
            
            # X線風の色（明るい白）
            color = (255, 255, 255)
            
            # 大きな円を描画（外側）
            cv2.circle(
                image,
                (int(kp.x), int(kp.y)),
                12,
                (200, 255, 255),  # 薄いシアン
                -1
            )
            
            # 内側の円（明るい白）
            cv2.circle(
                image,
                (int(kp.x), int(kp.y)),
                8,
                color,
                -1
            )
            
            # 中心点
            cv2.circle(
                image,
                (int(kp.x), int(kp.y)),
                3,
                (0, 255, 255),  # シアン
                -1
            )
        
        return image
    
    def _draw_alignment_lines_xray(self, image: np.ndarray, keypoints: Dict[str, PostureKeypoint], analysis: PostureAnalysis) -> np.ndarray:
        """X線風のアライメント線を描画（明るく）"""
        h, w = image.shape[:2]
        
        # 肩の水平線
        if "left_shoulder" in keypoints and "right_shoulder" in keypoints:
            ls = keypoints["left_shoulder"]
            rs = keypoints["right_shoulder"]
            if ls.confidence > 0.3 and rs.confidence > 0.3:
                y_shoulder = int((ls.y + rs.y) / 2)
                color = (0, 255, 255)  # シアン
                cv2.line(image, (0, y_shoulder), (w, y_shoulder), color, 2)
                # ラベル
                label = "肩"
                image = self._put_japanese_text(image, label, (10, y_shoulder - 5),
                                              font_size=16, color=color, thickness=2)
        
        # 骨盤の水平線
        if "left_hip" in keypoints and "right_hip" in keypoints:
            lh = keypoints["left_hip"]
            rh = keypoints["right_hip"]
            if lh.confidence > 0.3 and rh.confidence > 0.3:
                y_hip = int((lh.y + rh.y) / 2)
                color = (0, 255, 255)  # シアン
                cv2.line(image, (0, y_hip), (w, y_hip), color, 2)
                # ラベル
                label = "骨盤"
                image = self._put_japanese_text(image, label, (10, y_hip - 5),
                                              font_size=16, color=color, thickness=2)
        
        # 背骨の垂直線
        if "left_shoulder" in keypoints and "right_shoulder" in keypoints and \
           "left_hip" in keypoints and "right_hip" in keypoints:
            ls = keypoints["left_shoulder"]
            rs = keypoints["right_shoulder"]
            lh = keypoints["left_hip"]
            rh = keypoints["right_hip"]
            
            if all(kp.confidence > 0.3 for kp in [ls, rs, lh, rh]):
                shoulder_center_x = int((ls.x + rs.x) / 2)
                hip_center_x = int((lh.x + rh.x) / 2)
                spine_y_top = int(min(ls.y, rs.y))
                spine_y_bottom = int(max(lh.y, rh.y))
                
                # 背骨の中心線
                spine_center_x = int((shoulder_center_x + hip_center_x) / 2)
                color = (0, 255, 255)  # シアン
                cv2.line(image, (spine_center_x, spine_y_top), (spine_center_x, spine_y_bottom), color, 2)
                # ラベル
                label = "背骨"
                image = self._put_japanese_text(image, label, (spine_center_x + 5, spine_y_top + 15),
                                              font_size=16, color=color, thickness=2)
        
        return image

