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
        pass
    
    def visualize_posture(
        self,
        image: np.ndarray,
        keypoints: Dict[str, Tuple[float, float, float]],
        analysis: PostureAnalysis
    ) -> np.ndarray:
        """
        画像に姿勢評価を可視化
        
        Args:
            image: 入力画像（BGR形式）
            keypoints: キーポイント辞書 {name: (x, y, confidence)}
            analysis: 姿勢分析結果
        
        Returns:
            可視化された画像
        """
        # 画像をコピー
        vis_image = image.copy()
        
        # キーポイントを正規化
        normalized_keypoints = self._normalize_keypoints(keypoints)
        
        # 骨格を描画
        vis_image = self._draw_skeleton(vis_image, normalized_keypoints)
        
        # キーポイントを描画
        vis_image = self._draw_keypoints(vis_image, normalized_keypoints)
        
        # アライメント線を描画
        vis_image = self._draw_alignment_lines(vis_image, normalized_keypoints, analysis)
        
        # 評価項目を描画
        vis_image = self._draw_evaluation_text(vis_image, analysis)
        
        # スコアと問題点を描画
        vis_image = self._draw_score_and_issues(vis_image, analysis)
        
        return vis_image
    
    def _normalize_keypoints(self, keypoints: Dict[str, Tuple[float, float, float]]) -> Dict[str, PostureKeypoint]:
        """キーポイントを正規化"""
        normalized = {}
        for name, (x, y, conf) in keypoints.items():
            normalized[name] = PostureKeypoint(x=x, y=y, confidence=conf, name=name)
        return normalized
    
    def _draw_skeleton(self, image: np.ndarray, keypoints: Dict[str, PostureKeypoint]) -> np.ndarray:
        """骨格を描画"""
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
                    2
                )
        
        return image
    
    def _draw_keypoints(self, image: np.ndarray, keypoints: Dict[str, PostureKeypoint]) -> np.ndarray:
        """キーポイントを描画"""
        for name, kp in keypoints.items():
            if kp.confidence < 0.3:
                continue
            
            # 色を決定
            color = self._get_keypoint_color(name)
            
            # 円を描画
            cv2.circle(
                image,
                (int(kp.x), int(kp.y)),
                5,
                color,
                -1
            )
            
            # 外側の円（視認性向上）
            cv2.circle(
                image,
                (int(kp.x), int(kp.y)),
                7,
                (255, 255, 255),
                1
            )
        
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
        """評価項目を描画"""
        h, w = image.shape[:2]
        
        # 背景パネル
        panel_height = 200
        overlay = image.copy()
        cv2.rectangle(overlay, (0, h - panel_height), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, image, 0.3, 0, image)
        
        y_offset = h - panel_height + 20
        x_offset = 20
        
        # 総合スコア
        score_text = f"Overall Score: {int(analysis.overall_score * 100)}/100"
        score_color = self._get_score_color(analysis.overall_score)
        cv2.putText(image, score_text, (x_offset, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, score_color, 2)
        
        y_offset += 30
        
        # アライメントスコア
        cv2.putText(image, "Alignment Scores:", (x_offset, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        y_offset += 25
        
        alignment_labels = {
            "shoulder_alignment": "Shoulder",
            "hip_alignment": "Hip",
            "head_alignment": "Head",
            "spine_alignment": "Spine",
            "knee_alignment": "Knee"
        }
        
        for key, label in alignment_labels.items():
            if key in analysis.alignment_scores:
                score = analysis.alignment_scores[key]
                color = self._get_alignment_color(score)
                text = f"  {label}: {int(score * 100)}%"
                cv2.putText(image, text, (x_offset, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                y_offset += 20
        
        # 右側に問題点を表示
        x_right = w - 300
        y_right = h - panel_height + 20
        
        if analysis.issues:
            cv2.putText(image, "Issues Detected:", (x_right, y_right), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            y_right += 25
            
            for issue in analysis.issues[:3]:  # 最大3件
                severity_color = self._get_severity_color(issue["severity"])
                text = f"  - {issue['description']}"
                cv2.putText(image, text, (x_right, y_right), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, severity_color, 1)
                y_right += 20
        
        return image
    
    def _draw_score_and_issues(self, image: np.ndarray, analysis: PostureAnalysis) -> np.ndarray:
        """スコアと問題点を右上に描画"""
        h, w = image.shape[:2]
        
        # 総合スコアのバッジ
        score_text = f"{int(analysis.overall_score * 100)}"
        score_color = self._get_score_color(analysis.overall_score)
        
        # 背景円
        cv2.circle(image, (w - 60, 60), 40, (0, 0, 0), -1)
        cv2.circle(image, (w - 60, 60), 40, score_color, 3)
        
        # スコアテキスト
        text_size = cv2.getTextSize(score_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)[0]
        text_x = w - 60 - text_size[0] // 2
        text_y = 60 + text_size[1] // 2
        cv2.putText(image, score_text, (text_x, text_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, score_color, 2)
        
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

