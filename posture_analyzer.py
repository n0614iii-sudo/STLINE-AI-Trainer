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
    posture_type: str  # standing, sitting, walking, etc.
    overall_score: float  # 0.0-1.0
    issues: List[Dict[str, Any]]  # 検出された問題点
    recommendations: List[str]  # 改善提案
    keypoint_angles: Dict[str, float]  # 各関節の角度
    alignment_scores: Dict[str, float]  # 各部位の整列スコア
    detailed_metrics: Dict[str, Any]  # 詳細な測定値


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
        
        analysis = PostureAnalysis(
            timestamp=datetime.now(),
            posture_type=posture_type,
            overall_score=overall_score,
            issues=issues,
            recommendations=recommendations,
            keypoint_angles=angles,
            alignment_scores=alignment_scores,
            detailed_metrics=detailed_metrics
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
        
        # 首の角度（前傾・後傾）
        if all(k in keypoints for k in ["nose", "left_shoulder", "right_shoulder"]):
            nose = keypoints["nose"]
            ls = keypoints["left_shoulder"]
            rs = keypoints["right_shoulder"]
            shoulder_center_y = (ls.y + rs.y) / 2
            neck_angle = math.degrees(math.atan2(nose.y - shoulder_center_y, abs(nose.x - (ls.x + rs.x) / 2)))
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
        """各部位の整列スコアを計算（0.0-1.0）"""
        scores = {}
        
        # 肩の水平度
        if all(k in keypoints for k in ["left_shoulder", "right_shoulder"]):
            ls = keypoints["left_shoulder"]
            rs = keypoints["right_shoulder"]
            shoulder_diff = abs(ls.y - rs.y)
            # 差が小さいほど良い（最大50ピクセルを想定）
            scores["shoulder_alignment"] = max(0.0, 1.0 - (shoulder_diff / 50.0))
        
        # 骨盤の水平度
        if all(k in keypoints for k in ["left_hip", "right_hip"]):
            lh = keypoints["left_hip"]
            rh = keypoints["right_hip"]
            hip_diff = abs(lh.y - rh.y)
            scores["hip_alignment"] = max(0.0, 1.0 - (hip_diff / 50.0))
        
        # 頭部の位置（肩の中心との関係）
        if all(k in keypoints for k in ["nose", "left_shoulder", "right_shoulder"]):
            nose = keypoints["nose"]
            ls = keypoints["left_shoulder"]
            rs = keypoints["right_shoulder"]
            shoulder_center_x = (ls.x + rs.x) / 2
            head_offset = abs(nose.x - shoulder_center_x)
            scores["head_alignment"] = max(0.0, 1.0 - (head_offset / 50.0))
        
        # 背骨の直線性
        if all(k in keypoints for k in ["nose", "left_shoulder", "right_shoulder", "left_hip", "right_hip"]):
            ls = keypoints["left_shoulder"]
            rs = keypoints["right_shoulder"]
            lh = keypoints["left_hip"]
            rh = keypoints["right_hip"]
            
            shoulder_center = ((ls.x + rs.x) / 2, (ls.y + rs.y) / 2)
            hip_center = ((lh.x + rh.x) / 2, (lh.y + rh.y) / 2)
            
            # 理想的な背骨の位置からの偏差を計算
            # 簡易版：肩と骨盤の中心が一直線上にあるかを評価
            vertical_alignment = abs(shoulder_center[0] - hip_center[0])
            scores["spine_alignment"] = max(0.0, 1.0 - (vertical_alignment / 50.0))
        
        # 膝の位置
        if all(k in keypoints for k in ["left_knee", "right_knee"]):
            lk = keypoints["left_knee"]
            rk = keypoints["right_knee"]
            knee_diff = abs(lk.y - rk.y)
            scores["knee_alignment"] = max(0.0, 1.0 - (knee_diff / 50.0))
        
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
        
        # 肩の高さの違い
        if "shoulder_alignment" in alignment_scores and alignment_scores["shoulder_alignment"] < 0.8:
            issues.append({
                "type": "shoulder_imbalance",
                "severity": "medium" if alignment_scores["shoulder_alignment"] < 0.6 else "low",
                "description": "左右の肩の高さが異なります",
                "impact": "首や肩の痛みの原因になる可能性があります"
            })
        
        # 骨盤の傾き
        if "hip_alignment" in alignment_scores and alignment_scores["hip_alignment"] < 0.8:
            issues.append({
                "type": "hip_imbalance",
                "severity": "medium" if alignment_scores["hip_alignment"] < 0.6 else "low",
                "description": "骨盤が傾いています",
                "impact": "腰痛や姿勢不良の原因になる可能性があります"
            })
        
        # 猫背（前傾姿勢）
        if "spine_angle" in angles:
            if angles["spine_angle"] < -10:  # 前傾
                issues.append({
                    "type": "forward_head_posture",
                    "severity": "high" if angles["spine_angle"] < -20 else "medium",
                    "description": "猫背の傾向があります",
                    "impact": "首や肩の痛み、頭痛の原因になる可能性があります"
                })
        
        # 反り腰
        if "spine_angle" in angles:
            if angles["spine_angle"] > 15:  # 後傾
                issues.append({
                    "type": "sway_back",
                    "severity": "medium" if angles["spine_angle"] > 25 else "low",
                    "description": "反り腰の傾向があります",
                    "impact": "腰痛の原因になる可能性があります"
                })
        
        # 首の前傾
        if "neck_angle" in angles:
            if angles["neck_angle"] < -10:
                issues.append({
                    "type": "forward_head",
                    "severity": "high" if angles["neck_angle"] < -20 else "medium",
                    "description": "首が前に出ています（ストレートネックの可能性）",
                    "impact": "首や肩の痛み、頭痛の原因になる可能性があります"
                })
        
        # 頭部の位置
        if "head_alignment" in alignment_scores and alignment_scores["head_alignment"] < 0.7:
            issues.append({
                "type": "head_misalignment",
                "severity": "medium",
                "description": "頭部が中心からずれています",
                "impact": "首や肩の負担が増加する可能性があります"
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
            analyses.append(PostureAnalysis(**analysis_dict))
        
        return analyses

