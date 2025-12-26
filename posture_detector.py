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
    
    def __init__(self, model_path: str = "yolo11n-pose.pt", device: str = "cpu", conf_threshold: float = 0.25):
        """
        姿勢検出器を初期化
        
        Args:
            model_path: YOLOモデルのパス
            device: 使用デバイス ('cpu' または 'cuda')
            conf_threshold: 信頼度閾値（デフォルト: 0.25、より敏感な検出）
        """
        self.model_path = model_path
        self.device = device
        self.conf_threshold = conf_threshold
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
            # 画像の前処理（精度向上のため）
            processed_image = self._preprocess_image(image)
            
            # YOLOで推論（信頼度閾値を下げてより敏感に検出）
            results = self.model(
                processed_image, 
                conf=self.conf_threshold,  # より敏感な検出
                iou=0.45,  # NMS閾値
                imgsz=640,  # 入力画像サイズ（大きいほど精度向上）
                verbose=False
            )
            
            if not results or len(results) == 0:
                return None
            
            # 最も信頼度の高い検出結果を選択
            best_result = None
            best_conf = 0.0
            
            for result in results:
                if result.keypoints is not None and len(result.keypoints.data) > 0:
                    # キーポイントの平均信頼度を計算
                    if result.keypoints.conf is not None and len(result.keypoints.conf) > 0:
                        avg_conf = float(result.keypoints.conf[0].cpu().numpy().mean())
                        if avg_conf > best_conf:
                            best_conf = avg_conf
                            best_result = result
            
            if best_result is None:
                return None
            
            result = best_result
            
            # キーポイントを抽出
            if result.keypoints is None or len(result.keypoints.data) == 0:
                return None
            
            keypoints_data = result.keypoints.data[0].cpu().numpy()
            keypoints_conf = result.keypoints.conf[0].cpu().numpy() if result.keypoints.conf is not None else None
            
            # キーポイント辞書を作成（信頼度フィルタリングを緩和）
            keypoints = {}
            for i, name in enumerate(self.KEYPOINT_NAMES):
                if i < len(keypoints_data):
                    x, y = float(keypoints_data[i][0]), float(keypoints_data[i][1])
                    conf = float(keypoints_conf[i]) if keypoints_conf is not None and i < len(keypoints_conf) else 0.5
                    
                    # 有効なキーポイントのみ追加（信頼度が0.2以上、または座標が有効）
                    if (x > 0 and y > 0) and (conf >= 0.2 or (x > 10 and y > 10)):
                        keypoints[name] = (x, y, max(conf, 0.3))  # 最小信頼度を0.3に設定
            
            # 最低限のキーポイントが検出されているか確認
            essential_keypoints = ['left_shoulder', 'right_shoulder', 'left_hip', 'right_hip']
            detected_essential = sum(1 for kp in essential_keypoints if kp in keypoints)
            
            if detected_essential < 2:  # 最低2つの必須キーポイントが必要
                return None
            
            return keypoints if keypoints else None
        
        except Exception as e:
            logger.error(f"キーポイント検出エラー: {e}")
            return None
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        画像の前処理（精度向上のため）
        
        Args:
            image: 入力画像
        
        Returns:
            前処理された画像
        """
        try:
            import cv2
            # 画像のサイズを調整（640x640にリサイズ、アスペクト比を保持）
            h, w = image.shape[:2]
            target_size = 640
            
            # アスペクト比を保持してリサイズ
            scale = min(target_size / w, target_size / h)
            new_w = int(w * scale)
            new_h = int(h * scale)
            
            resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
            
            # パディングを追加して640x640にする
            pad_w = (target_size - new_w) // 2
            pad_h = (target_size - new_h) // 2
            
            padded = cv2.copyMakeBorder(
                resized, pad_h, target_size - new_h - pad_h,
                pad_w, target_size - new_w - pad_w,
                cv2.BORDER_CONSTANT, value=[0, 0, 0]
            )
            
            return padded
        except Exception as e:
            logger.warning(f"画像前処理エラー: {e}")
            return image
    
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

