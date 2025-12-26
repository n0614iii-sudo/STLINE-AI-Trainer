#!/usr/bin/env python3
"""
姿勢検出モジュール
YOLO11-Poseを使用したリアルタイム姿勢検出
"""

import numpy as np
from typing import Dict, Tuple, Optional, List
import logging

logger = logging.getLogger(__name__)


class PostureDetector:
    """YOLO11-Poseを使用した姿勢検出器"""
    
    KEYPOINT_NAMES = [
        "nose", "left_eye", "right_eye", "left_ear", "right_ear",
        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_hip", "right_hip",
        "left_knee", "right_knee", "left_ankle", "right_ankle"
    ]
    
    def __init__(self, model_path: str = "yolo11n-pose.pt", device: str = "cpu"):
        """
        姿勢検出器を初期化
        
        Args:
            model_path: YOLOモデルのパス
            device: 使用デバイス ('cpu' または 'cuda')
        """
        self.model_path = model_path
        self.device = device
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """YOLOモデルをロード"""
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.model_path)
            logger.info(f"YOLOモデルをロードしました: {self.model_path}")
        except ImportError:
            logger.warning("ultralyticsがインストールされていません。ダミーモードで動作します。")
            self.model = None
        except Exception as e:
            logger.error(f"YOLOモデルのロードに失敗しました: {e}")
            self.model = None
    
    def detect_keypoints(self, image: np.ndarray) -> Optional[Dict[str, Tuple[float, float, float]]]:
        """
        画像からキーポイントを検出
        
        Args:
            image: 入力画像 (numpy array, BGR形式)
        
        Returns:
            キーポイント辞書 {name: (x, y, confidence)} または None
        """
        if self.model is None:
            # ダミーモード: ダミーデータを返す
            return self._generate_dummy_keypoints(image.shape)
        
        try:
            # YOLOで推論
            results = self.model(image, conf=0.3, verbose=False)
            
            if not results or len(results) == 0:
                return None
            
            # 最初の検出結果を使用
            result = results[0]
            
            # キーポイントを抽出
            if result.keypoints is None or len(result.keypoints.data) == 0:
                return None
            
            keypoints_data = result.keypoints.data[0].cpu().numpy()
            keypoints_conf = result.keypoints.conf[0].cpu().numpy() if result.keypoints.conf is not None else None
            
            # キーポイント辞書を作成
            keypoints = {}
            for i, name in enumerate(self.KEYPOINT_NAMES):
                if i < len(keypoints_data):
                    x, y = float(keypoints_data[i][0]), float(keypoints_data[i][1])
                    conf = float(keypoints_conf[i]) if keypoints_conf is not None and i < len(keypoints_conf) else 1.0
                    
                    # 有効なキーポイントのみ追加（座標が0でない場合）
                    if x > 0 and y > 0:
                        keypoints[name] = (x, y, conf)
            
            return keypoints if keypoints else None
        
        except Exception as e:
            logger.error(f"キーポイント検出エラー: {e}")
            return None
    
    def _generate_dummy_keypoints(self, image_shape: Tuple[int, ...]) -> Dict[str, Tuple[float, float, float]]:
        """ダミーキーポイントを生成（テスト用）"""
        height, width = image_shape[:2] if len(image_shape) >= 2 else (480, 640)
        
        # 画像の中心を基準にダミーキーポイントを生成
        center_x, center_y = width / 2, height / 2
        
        return {
            "nose": (center_x, center_y - 100, 0.9),
            "left_eye": (center_x - 10, center_y - 110, 0.9),
            "right_eye": (center_x + 10, center_y - 110, 0.9),
            "left_ear": (center_x - 30, center_y - 100, 0.8),
            "right_ear": (center_x + 30, center_y - 100, 0.8),
            "left_shoulder": (center_x - 60, center_y, 0.9),
            "right_shoulder": (center_x + 60, center_y, 0.9),
            "left_elbow": (center_x - 80, center_y + 80, 0.8),
            "right_elbow": (center_x + 80, center_y + 80, 0.8),
            "left_wrist": (center_x - 100, center_y + 160, 0.7),
            "right_wrist": (center_x + 100, center_y + 160, 0.7),
            "left_hip": (center_x - 30, center_y + 120, 0.9),
            "right_hip": (center_x + 30, center_y + 120, 0.9),
            "left_knee": (center_x - 20, center_y + 220, 0.8),
            "right_knee": (center_x + 20, center_y + 220, 0.8),
            "left_ankle": (center_x - 30, center_y + 320, 0.7),
            "right_ankle": (center_x + 30, center_y + 320, 0.7)
        }

