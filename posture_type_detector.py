#!/usr/bin/env python3
"""
姿勢タイプ自動判定モジュール
キーポイントの配置から正面、横向き、背面を自動判定
"""

import math
from typing import Dict, Tuple, Optional


class PostureTypeDetector:
    """姿勢タイプを自動判定するクラス"""
    
    def __init__(self):
        """姿勢タイプ検出器を初期化"""
        pass
    
    def detect_posture_type(
        self, 
        keypoints: Dict[str, Tuple[float, float, float]]
    ) -> str:
        """
        キーポイントから姿勢タイプを自動判定
        
        Args:
            keypoints: キーポイント辞書 {name: (x, y, confidence)}
        
        Returns:
            姿勢タイプ: 'standing_front', 'standing_side', 'standing_back', 'unknown'
        """
        if not keypoints:
            return 'unknown'
        
        # 必須キーポイントの確認
        required_keypoints = ['left_shoulder', 'right_shoulder', 'left_hip', 'right_hip']
        if not all(kp in keypoints for kp in required_keypoints):
            return 'unknown'
        
        # 肩の位置関係を分析
        ls = keypoints['left_shoulder']
        rs = keypoints['right_shoulder']
        lh = keypoints['left_hip']
        rh = keypoints['right_hip']
        
        # 肩の水平距離（X方向の距離）
        shoulder_horizontal_distance = abs(rs[0] - ls[0])
        
        # 肩の垂直距離（Y方向の距離）
        shoulder_vertical_distance = abs(rs[1] - ls[1])
        
        # 骨盤の水平距離
        hip_horizontal_distance = abs(rh[0] - lh[0])
        
        # 骨盤の垂直距離
        hip_vertical_distance = abs(rh[1] - lh[1])
        
        # 肩と骨盤の中心点
        shoulder_center_x = (ls[0] + rs[0]) / 2
        hip_center_x = (lh[0] + rh[0]) / 2
        
        # 体の幅（肩と骨盤の平均幅）
        body_width = (shoulder_horizontal_distance + hip_horizontal_distance) / 2
        
        # 体の高さ（肩から骨盤までの距離）
        shoulder_center_y = (ls[1] + rs[1]) / 2
        hip_center_y = (lh[1] + rh[1]) / 2
        body_height = abs(hip_center_y - shoulder_center_y)
        
        # アスペクト比（幅/高さ）
        if body_height > 0:
            aspect_ratio = body_width / body_height
        else:
            aspect_ratio = 1.0
        
        # 判定ロジック
        # 1. 正面判定: 肩と骨盤の水平距離が大きく、垂直距離が小さい
        # 2. 横向き判定: 肩と骨盤の水平距離が小さく、体が横を向いている
        # 3. 背面判定: 顔のキーポイント（nose, eyes）が検出されない、または信頼度が低い
        
        # 顔のキーポイントの確認
        face_keypoints = ['nose', 'left_eye', 'right_eye']
        face_detected = sum(1 for kp in face_keypoints if kp in keypoints and keypoints[kp][2] > 0.3)
        
        # 肩の水平度（水平距離が大きいほど正面）
        shoulder_horizontal_ratio = shoulder_horizontal_distance / max(body_height, 1.0)
        
        # 骨盤の水平度
        hip_horizontal_ratio = hip_horizontal_distance / max(body_height, 1.0)
        
        # 判定スコア
        front_score = 0
        side_score = 0
        back_score = 0
        
        # 正面スコア: 肩と骨盤の水平距離が大きく、顔が検出されている
        if shoulder_horizontal_ratio > 0.3 and hip_horizontal_ratio > 0.3:
            front_score += 2
        if face_detected >= 2:
            front_score += 2
        if aspect_ratio > 0.4:  # 体の幅が広い（正面から見た場合）
            front_score += 1
        
        # 横向きスコア: 肩と骨盤の水平距離が小さく、体が縦長
        if shoulder_horizontal_ratio < 0.2 and hip_horizontal_ratio < 0.2:
            side_score += 3
        if aspect_ratio < 0.3:  # 体が縦長（横から見た場合）
            side_score += 2
        if face_detected == 1:  # 顔が一部しか見えない
            side_score += 1
        
        # 背面スコア: 顔のキーポイントが検出されない、または信頼度が低い
        if face_detected == 0:
            back_score += 3
        elif face_detected == 1 and keypoints.get('nose', (0, 0, 0))[2] < 0.3:
            back_score += 2
        if shoulder_horizontal_ratio > 0.25 and hip_horizontal_ratio > 0.25:
            back_score += 1  # 肩と骨盤が水平（背面から見た場合も同様）
        
        # 最も高いスコアの姿勢タイプを返す
        if front_score >= side_score and front_score >= back_score:
            return 'standing_front'
        elif side_score >= back_score:
            return 'standing_side'
        elif back_score > 0:
            return 'standing_back'
        else:
            # デフォルトは正面
            return 'standing_front'
    
    def get_posture_type_confidence(
        self,
        keypoints: Dict[str, Tuple[float, float, float]]
    ) -> Tuple[str, float]:
        """
        姿勢タイプと信頼度を返す
        
        Args:
            keypoints: キーポイント辞書
        
        Returns:
            (姿勢タイプ, 信頼度 0.0-1.0)
        """
        posture_type = self.detect_posture_type(keypoints)
        
        # 信頼度の計算（簡易版）
        required_keypoints = ['left_shoulder', 'right_shoulder', 'left_hip', 'right_hip']
        detected_count = sum(1 for kp in required_keypoints if kp in keypoints)
        confidence = detected_count / len(required_keypoints)
        
        return (posture_type, confidence)



