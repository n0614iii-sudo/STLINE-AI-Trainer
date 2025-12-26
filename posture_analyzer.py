#!/usr/bin/env python3
"""
姿勢診断モジュール
YOLO11-Poseを使用した姿勢分析と評価システム
"""

import numpy as np
import math
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json


@dataclass
class PostureKeypoint:
    """姿勢キーポイント情報"""
    x: float
    y: float
    confidence: float
    name: str


@dataclass
class PostureAnalysis:
    """姿勢分析結果"""
    timestamp: datetime
    posture_type: str  # standing_front, standing_side, standing_back, sitting, walking, etc.
    overall_score: float  # 0.0-1.0
    issues: List[Dict[str, Any]]  # 検出された問題点
    recommendations: List[str]  # 改善提案
    keypoint_angles: Dict[str, float]  # 各関節の角度
    alignment_scores: Dict[str, float]  # 各部位の整列スコア
    detailed_metrics: Dict[str, Any]  # 詳細な測定値
    muscle_assessment: Dict[str, Any]  # 筋肉評価（硬さ、ストレッチ、強化）


class PostureAnalyzer:
    """姿勢分析エンジン"""
    
    # YOLO11-Poseのキーポイント定義
    KEYPOINT_NAMES = [
        "nose", "left_eye", "right_eye", "left_ear", "right_ear",
        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_hip", "right_hip",
        "left_knee", "right_knee", "left_ankle", "right_ankle"
    ]
    
    def __init__(self):
        """姿勢分析器を初期化"""
        self.analysis_history: List[PostureAnalysis] = []
    
    def analyze_posture(
        self, 
        keypoints: Dict[str, Tuple[float, float, float]], 
        posture_type: str = "standing"
    ) -> PostureAnalysis:
        """
        姿勢を分析
        
        Args:
            keypoints: キーポイント辞書 {name: (x, y, confidence)}
            posture_type: 姿勢タイプ (standing, sitting, walking, etc.)
        
        Returns:
            PostureAnalysis: 分析結果
        """
        # キーポイントを正規化
        normalized_keypoints = self._normalize_keypoints(keypoints)
        
        # 角度を計算
        angles = self._calculate_angles(normalized_keypoints)
        
        # 整列スコアを計算
        alignment_scores = self._calculate_alignment_scores(normalized_keypoints)
        
        # 問題点を検出
        issues = self._detect_issues(normalized_keypoints, angles, alignment_scores, posture_type)
        
        # 総合スコアを計算
        overall_score = self._calculate_overall_score(alignment_scores, issues)
        
        # 改善提案を生成
        recommendations = self._generate_recommendations(issues, posture_type)
        
        # 詳細メトリクス
        detailed_metrics = self._calculate_detailed_metrics(normalized_keypoints, angles)
        
        # 筋肉評価を生成
        muscle_assessment = self._assess_muscles(issues, angles, alignment_scores, posture_type)
        
        analysis = PostureAnalysis(
            timestamp=datetime.now(),
            posture_type=posture_type,
            overall_score=overall_score,
            issues=issues,
            recommendations=recommendations,
            keypoint_angles=angles,
            alignment_scores=alignment_scores,
            detailed_metrics=detailed_metrics,
            muscle_assessment=muscle_assessment
        )
        
        self.analysis_history.append(analysis)
        return analysis
    
    def _normalize_keypoints(self, keypoints: Dict[str, Tuple[float, float, float]]) -> Dict[str, PostureKeypoint]:
        """キーポイントを正規化"""
        normalized = {}
        for name, (x, y, conf) in keypoints.items():
            normalized[name] = PostureKeypoint(x=x, y=y, confidence=conf, name=name)
        return normalized
    
    def _calculate_angles(self, keypoints: Dict[str, PostureKeypoint]) -> Dict[str, float]:
        """各関節の角度を計算"""
        angles = {}
        
        # 肩の角度（水平からの傾き）
        if all(k in keypoints for k in ["left_shoulder", "right_shoulder"]):
            ls = keypoints["left_shoulder"]
            rs = keypoints["right_shoulder"]
            shoulder_angle = math.degrees(math.atan2(rs.y - ls.y, rs.x - ls.x))
            angles["shoulder_tilt"] = abs(shoulder_angle)
        
        # 首の角度（前傾・後傾、医学的基準: 0-5度が正常、5度以上で問題）
        if all(k in keypoints for k in ["nose", "left_shoulder", "right_shoulder"]):
            # 耳の中心を計算（より正確な首の角度のため）
            le = keypoints.get("left_ear")
            re = keypoints.get("right_ear")
            if le and re:
                ear_center = ((le.x + re.x) / 2, (le.y + re.y) / 2)
            else:
                # 耳がない場合は鼻を使用
                nose = keypoints["nose"]
                ear_center = (nose.x, nose.y)
            
            ls = keypoints["left_shoulder"]
            rs = keypoints["right_shoulder"]
            shoulder_center = ((ls.x + rs.x) / 2, (ls.y + rs.y) / 2)
            
            # 首の角度を計算（垂直線からの角度）
            # 正の値: 前傾、負の値: 後傾
            neck_angle = math.degrees(math.atan2(
                ear_center[1] - shoulder_center[1],
                abs(ear_center[0] - shoulder_center[0])
            ))
            # 正常範囲: 0-5度、問題: 5度以上
            angles["neck_angle"] = neck_angle
        
        # 背骨の角度（猫背・反り腰の検出）
        if all(k in keypoints for k in ["left_shoulder", "right_shoulder", "left_hip", "right_hip"]):
            ls = keypoints["left_shoulder"]
            rs = keypoints["right_shoulder"]
            lh = keypoints["left_hip"]
            rh = keypoints["right_hip"]
            
            shoulder_center = ((ls.x + rs.x) / 2, (ls.y + rs.y) / 2)
            hip_center = ((lh.x + rh.x) / 2, (lh.y + rh.y) / 2)
            
            spine_angle = math.degrees(math.atan2(
                hip_center[1] - shoulder_center[1],
                abs(hip_center[0] - shoulder_center[0])
            ))
            angles["spine_angle"] = spine_angle
        
        # 膝の角度
        if all(k in keypoints for k in ["left_hip", "left_knee", "left_ankle"]):
            angles["left_knee_angle"] = self._calculate_joint_angle(
                keypoints["left_hip"],
                keypoints["left_knee"],
                keypoints["left_ankle"]
            )
        
        if all(k in keypoints for k in ["right_hip", "right_knee", "right_ankle"]):
            angles["right_knee_angle"] = self._calculate_joint_angle(
                keypoints["right_hip"],
                keypoints["right_knee"],
                keypoints["right_ankle"]
            )
        
        # 股関節の角度
        if all(k in keypoints for k in ["left_shoulder", "left_hip", "left_knee"]):
            angles["left_hip_angle"] = self._calculate_joint_angle(
                keypoints["left_shoulder"],
                keypoints["left_hip"],
                keypoints["left_knee"]
            )
        
        if all(k in keypoints for k in ["right_shoulder", "right_hip", "right_knee"]):
            angles["right_hip_angle"] = self._calculate_joint_angle(
                keypoints["right_shoulder"],
                keypoints["right_hip"],
                keypoints["right_knee"]
            )
        
        return angles
    
    def _calculate_joint_angle(
        self, 
        point1: PostureKeypoint, 
        point2: PostureKeypoint, 
        point3: PostureKeypoint
    ) -> float:
        """3点間の角度を計算"""
        # ベクトルを計算
        vec1 = (point1.x - point2.x, point1.y - point2.y)
        vec2 = (point3.x - point2.x, point3.y - point2.y)
        
        # 内積と外積を計算
        dot = vec1[0] * vec2[0] + vec1[1] * vec2[1]
        det = vec1[0] * vec2[1] - vec1[1] * vec2[0]
        
        # 角度を計算（ラジアン→度）
        angle = math.degrees(math.atan2(det, dot))
        return abs(angle)
    
    def _calculate_alignment_scores(self, keypoints: Dict[str, PostureKeypoint]) -> Dict[str, float]:
        """
        各部位の整列スコアを計算（0.0-1.0）
        
        専門的知識に基づく改善:
        - 医学的・運動学的基準を考慮
        - 画像サイズに応じた相対評価
        - より正確な閾値設定
        """
        scores = {}
        
        # 画像サイズを取得（相対評価のため）
        if keypoints:
            # 体の高さを推定（肩から足首まで）
            body_height = 0
            if "left_shoulder" in keypoints and "left_ankle" in keypoints:
                ls = keypoints["left_shoulder"]
                la = keypoints["left_ankle"]
                body_height = abs(la.y - ls.y)
            elif "right_shoulder" in keypoints and "right_ankle" in keypoints:
                rs = keypoints["right_shoulder"]
                ra = keypoints["right_ankle"]
                body_height = abs(ra.y - rs.y)
            
            # 体の高さが取得できない場合はデフォルト値を使用
            if body_height == 0:
                body_height = 500  # デフォルト値
            
            # 肩の水平度（医学的基準: 2cm以内が正常、体高の約2-3%）
            if all(k in keypoints for k in ["left_shoulder", "right_shoulder"]):
                ls = keypoints["left_shoulder"]
                rs = keypoints["right_shoulder"]
                shoulder_diff = abs(ls.y - rs.y)
                # 正常範囲: 体高の2%以内（約2cm相当）
                normal_threshold = body_height * 0.02
                # 許容範囲: 体高の5%以内
                acceptable_threshold = body_height * 0.05
                if shoulder_diff <= normal_threshold:
                    scores["shoulder_alignment"] = 1.0
                elif shoulder_diff <= acceptable_threshold:
                    scores["shoulder_alignment"] = max(0.7, 1.0 - ((shoulder_diff - normal_threshold) / (acceptable_threshold - normal_threshold)) * 0.3)
                else:
                    scores["shoulder_alignment"] = max(0.0, 0.7 - ((shoulder_diff - acceptable_threshold) / acceptable_threshold) * 0.7)
            
            # 骨盤の水平度（医学的基準: 1-2cm以内が正常）
            if all(k in keypoints for k in ["left_hip", "right_hip"]):
                lh = keypoints["left_hip"]
                rh = keypoints["right_hip"]
                hip_diff = abs(lh.y - rh.y)
                # 正常範囲: 体高の1.5%以内
                normal_threshold = body_height * 0.015
                # 許容範囲: 体高の4%以内
                acceptable_threshold = body_height * 0.04
                if hip_diff <= normal_threshold:
                    scores["hip_alignment"] = 1.0
                elif hip_diff <= acceptable_threshold:
                    scores["hip_alignment"] = max(0.7, 1.0 - ((hip_diff - normal_threshold) / (acceptable_threshold - normal_threshold)) * 0.3)
                else:
                    scores["hip_alignment"] = max(0.0, 0.7 - ((hip_diff - acceptable_threshold) / acceptable_threshold) * 0.7)
            
            # 頭部の位置（肩の中心との関係、医学的基準: 2cm以内が正常）
            # 改善: 耳の中心を使用（より正確な頭部の中心位置）
            if all(k in keypoints for k in ["left_shoulder", "right_shoulder"]):
                ls = keypoints["left_shoulder"]
                rs = keypoints["right_shoulder"]
                shoulder_center_x = (ls.x + rs.x) / 2
                shoulder_center_y = (ls.y + rs.y) / 2
                
                # 耳の中心を計算（より正確な頭部の中心位置）
                head_center_x = None
                head_center_y = None
                
                # 耳が検出されている場合は耳の中心を使用
                if "left_ear" in keypoints and "right_ear" in keypoints:
                    le = keypoints["left_ear"]
                    re = keypoints["right_ear"]
                    if le.confidence > 0.3 and re.confidence > 0.3:
                        head_center_x = (le.x + re.x) / 2
                        head_center_y = (le.y + re.y) / 2
                
                # 耳がない場合は、目と鼻の中心を使用
                if head_center_x is None:
                    head_points = []
                    if "left_eye" in keypoints and keypoints["left_eye"].confidence > 0.3:
                        head_points.append(keypoints["left_eye"])
                    if "right_eye" in keypoints and keypoints["right_eye"].confidence > 0.3:
                        head_points.append(keypoints["right_eye"])
                    if "nose" in keypoints and keypoints["nose"].confidence > 0.3:
                        head_points.append(keypoints["nose"])
                    
                    if len(head_points) >= 2:
                        head_center_x = sum(p.x for p in head_points) / len(head_points)
                        head_center_y = sum(p.y for p in head_points) / len(head_points)
                    elif len(head_points) == 1:
                        head_center_x = head_points[0].x
                        head_center_y = head_points[0].y
                
                # 頭部の中心が取得できた場合のみ評価
                if head_center_x is not None and head_center_y is not None:
                    # 左右のずれ（X方向）
                    horizontal_offset = abs(head_center_x - shoulder_center_x)
                    
                    # 前後のずれ（Y方向、頭部が肩より前にある場合を検出）
                    # 正常な頭部位置: 肩の中心より少し上（体高の約10-15%上）
                    expected_head_y = shoulder_center_y - body_height * 0.12  # 頭部は肩より約12%上
                    vertical_offset = abs(head_center_y - expected_head_y)
                    
                    # 左右のずれの評価（正常範囲: 体高の2%以内）
                    normal_threshold_h = body_height * 0.02
                    acceptable_threshold_h = body_height * 0.05
                    
                    # 前後のずれの評価（正常範囲: 体高の3%以内）
                    normal_threshold_v = body_height * 0.03
                    acceptable_threshold_v = body_height * 0.06
                    
                    # 左右と前後のずれを統合評価
                    # より厳しい方の評価を使用
                    score_h = 1.0
                    if horizontal_offset <= normal_threshold_h:
                        score_h = 1.0
                    elif horizontal_offset <= acceptable_threshold_h:
                        score_h = max(0.7, 1.0 - ((horizontal_offset - normal_threshold_h) / (acceptable_threshold_h - normal_threshold_h)) * 0.3)
                    else:
                        score_h = max(0.0, 0.7 - ((horizontal_offset - acceptable_threshold_h) / acceptable_threshold_h) * 0.7)
                    
                    score_v = 1.0
                    if vertical_offset <= normal_threshold_v:
                        score_v = 1.0
                    elif vertical_offset <= acceptable_threshold_v:
                        score_v = max(0.7, 1.0 - ((vertical_offset - normal_threshold_v) / (acceptable_threshold_v - normal_threshold_v)) * 0.3)
                    else:
                        score_v = max(0.0, 0.7 - ((vertical_offset - acceptable_threshold_v) / acceptable_threshold_v) * 0.7)
                    
                    # 左右と前後のスコアの平均（重み付け: 左右60%、前後40%）
                    scores["head_alignment"] = score_h * 0.6 + score_v * 0.4
            
            # 背骨の直線性（医学的基準: 2cm以内の偏差が正常）
            if all(k in keypoints for k in ["left_shoulder", "right_shoulder", "left_hip", "right_hip"]):
                ls = keypoints["left_shoulder"]
                rs = keypoints["right_shoulder"]
                lh = keypoints["left_hip"]
                rh = keypoints["right_hip"]
                
                shoulder_center = ((ls.x + rs.x) / 2, (ls.y + rs.y) / 2)
                hip_center = ((lh.x + rh.x) / 2, (lh.y + rh.y) / 2)
                
                # 垂直方向の偏差を計算
                vertical_alignment = abs(shoulder_center[0] - hip_center[0])
                # 正常範囲: 体高の2%以内
                normal_threshold = body_height * 0.02
                # 許容範囲: 体高の5%以内
                acceptable_threshold = body_height * 0.05
                if vertical_alignment <= normal_threshold:
                    scores["spine_alignment"] = 1.0
                elif vertical_alignment <= acceptable_threshold:
                    scores["spine_alignment"] = max(0.7, 1.0 - ((vertical_alignment - normal_threshold) / (acceptable_threshold - normal_threshold)) * 0.3)
                else:
                    scores["spine_alignment"] = max(0.0, 0.7 - ((vertical_alignment - acceptable_threshold) / acceptable_threshold) * 0.7)
            
            # 膝の位置（医学的基準: 1-2cm以内が正常）
            if all(k in keypoints for k in ["left_knee", "right_knee"]):
                lk = keypoints["left_knee"]
                rk = keypoints["right_knee"]
                knee_diff = abs(lk.y - rk.y)
                # 正常範囲: 体高の1.5%以内
                normal_threshold = body_height * 0.015
                # 許容範囲: 体高の4%以内
                acceptable_threshold = body_height * 0.04
                if knee_diff <= normal_threshold:
                    scores["knee_alignment"] = 1.0
                elif knee_diff <= acceptable_threshold:
                    scores["knee_alignment"] = max(0.7, 1.0 - ((knee_diff - normal_threshold) / (acceptable_threshold - normal_threshold)) * 0.3)
                else:
                    scores["knee_alignment"] = max(0.0, 0.7 - ((knee_diff - acceptable_threshold) / acceptable_threshold) * 0.7)
        
        return scores
    
    def _detect_issues(
        self, 
        keypoints: Dict[str, PostureKeypoint],
        angles: Dict[str, float],
        alignment_scores: Dict[str, float],
        posture_type: str
    ) -> List[Dict[str, Any]]:
        """姿勢の問題点を検出"""
        issues = []
        
        # 肩の高さの違い（精度向上：閾値を調整）
        if "shoulder_alignment" in alignment_scores and alignment_scores["shoulder_alignment"] < 0.85:
            issues.append({
                "type": "shoulder_imbalance",
                "severity": "high" if alignment_scores["shoulder_alignment"] < 0.5 else ("medium" if alignment_scores["shoulder_alignment"] < 0.7 else "low"),
                "description": "左右の肩の高さが異なります",
                "impact": "首や肩の痛みの原因になる可能性があります"
            })
        
        # 骨盤の傾き（精度向上：閾値を調整）
        if "hip_alignment" in alignment_scores and alignment_scores["hip_alignment"] < 0.85:
            issues.append({
                "type": "hip_imbalance",
                "severity": "high" if alignment_scores["hip_alignment"] < 0.5 else ("medium" if alignment_scores["hip_alignment"] < 0.7 else "low"),
                "description": "骨盤が傾いています",
                "impact": "腰痛や姿勢不良の原因になる可能性があります"
            })
        
        # 猫背（前傾姿勢）（医学的基準: 5度以上で問題）
        if "spine_angle" in angles:
            spine_angle = angles["spine_angle"]
            # 前傾（負の値）: 5度以上で問題
            if spine_angle < -5:
                severity = "high" if spine_angle < -15 else ("medium" if spine_angle < -10 else "low")
                issues.append({
                    "type": "forward_head_posture",
                    "severity": severity,
                    "description": f"猫背の傾向があります（前傾角度: {abs(spine_angle):.1f}度）",
                    "impact": "首や肩の痛み、頭痛、呼吸機能の低下の原因になる可能性があります"
                })
        
        # 反り腰（医学的基準: 5度以上で問題）
        if "spine_angle" in angles:
            spine_angle = angles["spine_angle"]
            # 後傾（正の値）: 5度以上で問題
            if spine_angle > 5:
                severity = "high" if spine_angle > 15 else ("medium" if spine_angle > 10 else "low")
                issues.append({
                    "type": "sway_back",
                    "severity": severity,
                    "description": f"反り腰の傾向があります（後傾角度: {spine_angle:.1f}度）",
                    "impact": "腰痛、骨盤の歪み、股関節の痛みの原因になる可能性があります"
                })
        
        # 首の前傾（医学的基準: 5度以上で問題）
        if "neck_angle" in angles:
            neck_angle = angles["neck_angle"]
            # 前傾（正の値）: 5度以上で問題
            if neck_angle > 5:
                severity = "high" if neck_angle > 15 else ("medium" if neck_angle > 10 else "low")
                issues.append({
                    "type": "forward_head",
                    "severity": severity,
                    "description": f"首が前に出ています（ストレートネックの可能性、前傾角度: {neck_angle:.1f}度）",
                    "impact": "首や肩の痛み、頭痛、めまい、眼精疲労の原因になる可能性があります"
                })
        
        # 頭部の位置（改善: より詳細な問題検出）
        if "head_alignment" in alignment_scores:
            head_score = alignment_scores["head_alignment"]
            if head_score < 0.5:
                issues.append({
                    "type": "head_misalignment",
                    "severity": "high",
                    "description": "頭部が大きく中心からずれています",
                    "impact": "首や肩の痛み、頭痛、めまいの原因になる可能性があります"
                })
            elif head_score < 0.7:
                issues.append({
                    "type": "head_misalignment",
                    "severity": "medium",
                    "description": "頭部が中心からずれています",
                    "impact": "首や肩の負担が増加する可能性があります"
                })
            elif head_score < 0.85:
                issues.append({
                    "type": "head_misalignment",
                    "severity": "low",
                    "description": "頭部がわずかに中心からずれています",
                    "impact": "長時間の姿勢不良の原因になる可能性があります"
                })
        
        # 背骨の歪み
        if "spine_alignment" in alignment_scores and alignment_scores["spine_alignment"] < 0.7:
            issues.append({
                "type": "spine_misalignment",
                "severity": "medium" if alignment_scores["spine_alignment"] < 0.5 else "low",
                "description": "背骨が一直線上にありません",
                "impact": "姿勢不良や痛みの原因になる可能性があります"
            })
        
        return issues
    
    def _calculate_overall_score(
        self, 
        alignment_scores: Dict[str, float],
        issues: List[Dict[str, Any]]
    ) -> float:
        """総合姿勢スコアを計算（0.0-1.0）"""
        if not alignment_scores:
            return 0.5  # デフォルト値
        
        # 整列スコアの平均
        avg_alignment = sum(alignment_scores.values()) / len(alignment_scores)
        
        # 問題点による減点
        issue_penalty = 0.0
        for issue in issues:
            if issue["severity"] == "high":
                issue_penalty += 0.15
            elif issue["severity"] == "medium":
                issue_penalty += 0.10
            else:
                issue_penalty += 0.05
        
        # 最終スコア
        overall_score = max(0.0, min(1.0, avg_alignment - issue_penalty))
        return round(overall_score, 2)
    
    def _generate_recommendations(
        self, 
        issues: List[Dict[str, Any]],
        posture_type: str
    ) -> List[str]:
        """改善提案を生成"""
        recommendations = []
        
        issue_types = [issue["type"] for issue in issues]
        
        if "forward_head_posture" in issue_types or "forward_head" in issue_types:
            recommendations.append("首と肩のストレッチを毎日行いましょう")
            recommendations.append("デスクワーク中は定期的に首を後ろに倒す運動をしましょう")
            recommendations.append("胸を開くストレッチ（胸筋ストレッチ）を推奨します")
        
        if "shoulder_imbalance" in issue_types:
            recommendations.append("左右の肩のバランスを整えるエクササイズを行いましょう")
            recommendations.append("片側だけに負担をかけないよう注意しましょう")
            recommendations.append("肩甲骨を動かすエクササイズを推奨します")
        
        if "hip_imbalance" in issue_types:
            recommendations.append("骨盤の歪みを改善するストレッチを行いましょう")
            recommendations.append("片足立ちのバランスエクササイズを推奨します")
            recommendations.append("股関節の柔軟性を高めるストレッチを行いましょう")
        
        if "sway_back" in issue_types:
            recommendations.append("腹筋と背筋のバランスを整えましょう")
            recommendations.append("骨盤底筋を鍛えるエクササイズを推奨します")
            recommendations.append("腰を支える筋肉を強化しましょう")
        
        if "spine_misalignment" in issue_types:
            recommendations.append("背骨の柔軟性を高めるストレッチを行いましょう")
            recommendations.append("体幹を強化するエクササイズを推奨します")
            recommendations.append("正しい姿勢を意識する習慣をつけましょう")
        
        # 問題がない場合の一般的な推奨事項
        if not recommendations:
            recommendations.append("現在の姿勢は良好です。この状態を維持しましょう")
            recommendations.append("定期的なストレッチとエクササイズを継続してください")
            recommendations.append("長時間同じ姿勢を取らないよう注意しましょう")
        
        return recommendations
    
    def _calculate_detailed_metrics(
        self, 
        keypoints: Dict[str, PostureKeypoint],
        angles: Dict[str, float]
    ) -> Dict[str, Any]:
        """詳細な測定値を計算"""
        metrics = {}
        
        # 各部位間の距離
        if all(k in keypoints for k in ["left_shoulder", "right_shoulder"]):
            ls = keypoints["left_shoulder"]
            rs = keypoints["right_shoulder"]
            metrics["shoulder_width"] = math.sqrt(
                (rs.x - ls.x) ** 2 + (rs.y - ls.y) ** 2
            )
        
        if all(k in keypoints for k in ["left_hip", "right_hip"]):
            lh = keypoints["left_hip"]
            rh = keypoints["right_hip"]
            metrics["hip_width"] = math.sqrt(
                (rh.x - lh.x) ** 2 + (rh.y - lh.y) ** 2
            )
        
        # 角度情報を追加
        metrics["angles"] = angles.copy()
        
        return metrics
    
    def _assess_muscles(
        self,
        issues: List[Dict[str, Any]],
        angles: Dict[str, float],
        alignment_scores: Dict[str, float],
        posture_type: str
    ) -> Dict[str, Any]:
        """
        筋肉の硬さ、ストレッチ、強化の必要性を専門的に評価
        
        Returns:
            {
                "tight_muscles": [{"name": "筋肉名", "reason": "理由", "severity": "high/medium/low"}],
                "stretch_needed": [{"muscle": "筋肉名", "method": "ストレッチ方法", "frequency": "頻度"}],
                "strengthen_needed": [{"muscle": "筋肉名", "exercise": "エクササイズ", "frequency": "頻度"}]
            }
        """
        tight_muscles = []
        stretch_needed = []
        strengthen_needed = []
        
        issue_types = [issue["type"] for issue in issues]
        
        # 猫背・前傾姿勢の場合
        if "forward_head_posture" in issue_types or "forward_head" in issue_types:
            tight_muscles.append({
                "name": "胸鎖乳突筋（きょうさにゅうとつきん）",
                "reason": "頭部が前方に突出しているため、首の前側の筋肉が短縮している可能性があります",
                "severity": "high" if any(i["type"] in ["forward_head_posture", "forward_head"] and i["severity"] == "high" for i in issues) else "medium"
            })
            tight_muscles.append({
                "name": "小胸筋（しょうきょうきん）",
                "reason": "肩が内転し、胸が閉じているため、前胸部の筋肉が短縮しています",
                "severity": "high" if any(i["type"] in ["forward_head_posture", "forward_head"] and i["severity"] == "high" for i in issues) else "medium"
            })
            tight_muscles.append({
                "name": "上腕二頭筋（じょうわんにとうきん）",
                "reason": "肩の内転により、上腕の前側の筋肉が短縮している可能性があります",
                "severity": "medium"
            })
            
            stretch_needed.append({
                "muscle": "胸鎖乳突筋",
                "method": "首を横に倒し、反対側に回旋させるストレッチ。30秒×3セット",
                "frequency": "毎日2回"
            })
            stretch_needed.append({
                "muscle": "小胸筋",
                "method": "壁に手をついて胸を開くストレッチ（ドアウェイストレッチ）。30秒×3セット",
                "frequency": "毎日2回"
            })
            stretch_needed.append({
                "muscle": "上腕二頭筋",
                "method": "壁に手をついて上腕を後方に引くストレッチ。30秒×3セット",
                "frequency": "毎日1回"
            })
            
            strengthen_needed.append({
                "muscle": "深部頸部屈筋（しんぶけいぶくっきん）",
                "exercise": "チンタック（あごを引く運動）。10回×3セット",
                "frequency": "毎日2回"
            })
            strengthen_needed.append({
                "muscle": "中・下部僧帽筋（ちゅう・かぶそうぼうきん）",
                "exercise": "肩甲骨を寄せる運動（肩甲骨プル）。15回×3セット",
                "frequency": "毎日2回"
            })
            strengthen_needed.append({
                "muscle": "菱形筋（りょうけいきん）",
                "exercise": "肩甲骨を寄せる運動。15回×3セット",
                "frequency": "毎日2回"
            })
        
        # 肩の高さの違い
        if "shoulder_imbalance" in issue_types:
            tight_muscles.append({
                "name": "上斜方筋（じょうしゃほうきん）",
                "reason": "片側の肩が上がっているため、その側の首から肩にかけての筋肉が過緊張しています",
                "severity": "high" if any(i["type"] == "shoulder_imbalance" and i["severity"] == "high" for i in issues) else "medium"
            })
            tight_muscles.append({
                "name": "肩甲挙筋（けんこうきょきん）",
                "reason": "肩が上がっている側の肩甲骨を引き上げる筋肉が短縮しています",
                "severity": "medium"
            })
            
            stretch_needed.append({
                "muscle": "上斜方筋（上がっている側）",
                "method": "首を横に倒し、反対側に回旋させるストレッチ。30秒×3セット",
                "frequency": "毎日2回"
            })
            stretch_needed.append({
                "muscle": "肩甲挙筋（上がっている側）",
                "method": "首を横に倒し、反対側に回旋させるストレッチ。30秒×3セット",
                "frequency": "毎日2回"
            })
            
            strengthen_needed.append({
                "muscle": "中・下部僧帽筋（下がっている側）",
                "exercise": "肩甲骨を下げる運動。15回×3セット",
                "frequency": "毎日2回"
            })
        
        # 骨盤の傾き
        if "hip_imbalance" in issue_types:
            tight_muscles.append({
                "name": "腰方形筋（ようほうけいきん）",
                "reason": "骨盤が傾いているため、片側の腰の筋肉が短縮しています",
                "severity": "high" if any(i["type"] == "hip_imbalance" and i["severity"] == "high" for i in issues) else "medium"
            })
            tight_muscles.append({
                "name": "腸腰筋（ちょうようきん）",
                "reason": "骨盤の前傾により、股関節の前側の筋肉が短縮している可能性があります",
                "severity": "medium"
            })
            
            stretch_needed.append({
                "muscle": "腰方形筋（上がっている側）",
                "method": "横向きに寝て、上側の脚を後ろに引くストレッチ。30秒×3セット",
                "frequency": "毎日2回"
            })
            stretch_needed.append({
                "muscle": "腸腰筋",
                "method": "ランジポジションで前脚の股関節を伸ばすストレッチ。30秒×3セット",
                "frequency": "毎日2回"
            })
            
            strengthen_needed.append({
                "muscle": "腹横筋（ふくおうきん）",
                "exercise": "ドローイン（お腹を引っ込める運動）。10回×3セット",
                "frequency": "毎日2回"
            })
            strengthen_needed.append({
                "muscle": "多裂筋（たれつきん）",
                "exercise": "バードドッグ（四つん這いで対角の手足を上げる）。10回×3セット",
                "frequency": "毎日2回"
            })
        
        # 反り腰
        if "sway_back" in issue_types:
            tight_muscles.append({
                "name": "腸腰筋（ちょうようきん）",
                "reason": "骨盤が前傾しているため、股関節の前側の筋肉が短縮しています",
                "severity": "high" if any(i["type"] == "sway_back" and i["severity"] == "high" for i in issues) else "medium"
            })
            tight_muscles.append({
                "name": "大腿直筋（だいたいちょっきん）",
                "reason": "骨盤の前傾により、太ももの前側の筋肉が短縮しています",
                "severity": "medium"
            })
            tight_muscles.append({
                "name": "腰背部伸筋群（ようはいぶしんきんぐん）",
                "reason": "腰が反っているため、腰の後ろ側の筋肉が過緊張しています",
                "severity": "high" if any(i["type"] == "sway_back" and i["severity"] == "high" for i in issues) else "medium"
            })
            
            stretch_needed.append({
                "muscle": "腸腰筋",
                "method": "ランジポジションで前脚の股関節を伸ばすストレッチ。30秒×3セット",
                "frequency": "毎日2回"
            })
            stretch_needed.append({
                "muscle": "大腿直筋",
                "method": "立位で膝を曲げ、かかとをお尻に近づけるストレッチ。30秒×3セット",
                "frequency": "毎日2回"
            })
            stretch_needed.append({
                "muscle": "腰背部伸筋群",
                "method": "膝を抱えて丸くなるストレッチ。30秒×3セット",
                "frequency": "毎日2回"
            })
            
            strengthen_needed.append({
                "muscle": "腹横筋（ふくおうきん）",
                "exercise": "ドローイン（お腹を引っ込める運動）。10回×3セット",
                "frequency": "毎日2回"
            })
            strengthen_needed.append({
                "muscle": "骨盤底筋群（こつばんていきんぐん）",
                "exercise": "ケーゲル運動（骨盤底筋を締める運動）。10回×3セット",
                "frequency": "毎日2回"
            })
            strengthen_needed.append({
                "muscle": "ハムストリングス（太もも裏）",
                "exercise": "ヒップリフト（お尻を持ち上げる運動）。15回×3セット",
                "frequency": "毎日2回"
            })
        
        # 背骨の歪み
        if "spine_misalignment" in issue_types:
            tight_muscles.append({
                "name": "多裂筋（たれつきん）",
                "reason": "背骨が一直線上にないため、背骨を支える深部の筋肉が不均衡です",
                "severity": "medium"
            })
            tight_muscles.append({
                "name": "回旋筋（かいせんきん）",
                "reason": "背骨の回旋により、片側の回旋筋が短縮しています",
                "severity": "medium"
            })
            
            stretch_needed.append({
                "muscle": "多裂筋・回旋筋",
                "method": "座位で体を回旋させるストレッチ。左右各30秒×3セット",
                "frequency": "毎日2回"
            })
            
            strengthen_needed.append({
                "muscle": "多裂筋",
                "exercise": "バードドッグ（四つん這いで対角の手足を上げる）。10回×3セット",
                "frequency": "毎日2回"
            })
            strengthen_needed.append({
                "muscle": "腹横筋",
                "exercise": "プランク（体幹を一直線に保つ）。30秒×3セット",
                "frequency": "毎日2回"
            })
        
        return {
            "tight_muscles": tight_muscles,
            "stretch_needed": stretch_needed,
            "strengthen_needed": strengthen_needed
        }
    
    def get_analysis_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """過去の分析結果のサマリーを取得"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_analyses = [
            a for a in self.analysis_history
            if a.timestamp >= cutoff_date
        ]
        
        if not recent_analyses:
            return {"message": f"過去{days}日間の姿勢診断記録がありません"}
        
        # 統計計算
        avg_score = sum(a.overall_score for a in recent_analyses) / len(recent_analyses)
        
        # よく見られる問題点
        issue_counts = {}
        for analysis in recent_analyses:
            for issue in analysis.issues:
                issue_type = issue["type"]
                issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        most_common_issues = sorted(
            issue_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        return {
            "period_days": days,
            "total_analyses": len(recent_analyses),
            "average_score": round(avg_score, 2),
            "most_common_issues": [
                {"type": issue_type, "count": count}
                for issue_type, count in most_common_issues
            ],
            "improvement_trend": self._calculate_improvement_trend(recent_analyses)
        }
    
    def _calculate_improvement_trend(self, analyses: List[PostureAnalysis]) -> str:
        """改善傾向を計算"""
        if len(analyses) < 2:
            return "データ不足"
        
        # 最初の1/3と最後の1/3を比較
        first_third = analyses[:len(analyses)//3]
        last_third = analyses[-len(analyses)//3:]
        
        first_avg = sum(a.overall_score for a in first_third) / len(first_third)
        last_avg = sum(a.overall_score for a in last_third) / len(last_third)
        
        diff = last_avg - first_avg
        
        if diff > 0.1:
            return "改善傾向"
        elif diff < -0.1:
            return "悪化傾向"
        else:
            return "安定"
    
    def save_analysis(self, user_id: str, analysis: PostureAnalysis, filepath: str = "posture_analyses.json"):
        """分析結果を保存"""
        data = {
            "user_id": user_id,
            "analysis": asdict(analysis),
            "timestamp": analysis.timestamp.isoformat()
        }
        
        # 既存データを読み込み
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
        else:
            all_data = []
        
        all_data.append(data)
        
        # 保存
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2, default=str)
    
    def load_analyses(self, user_id: str, filepath: str = "posture_analyses.json") -> List[PostureAnalysis]:
        """分析結果を読み込み"""
        if not os.path.exists(filepath):
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        
        user_analyses = [
            data for data in all_data
            if data.get("user_id") == user_id
        ]
        
        # PostureAnalysisオブジェクトに変換
        analyses = []
        for data in user_analyses:
            analysis_dict = data["analysis"]
            analysis_dict["timestamp"] = datetime.fromisoformat(analysis_dict["timestamp"])
            # 古いデータにmuscle_assessmentがない場合のデフォルト値
            if "muscle_assessment" not in analysis_dict:
                analysis_dict["muscle_assessment"] = {"tight_muscles": [], "stretch_needed": [], "strengthen_needed": []}
            analyses.append(PostureAnalysis(**analysis_dict))
        
        return analyses

