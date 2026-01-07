#!/usr/bin/env python3
"""
LINE通知モジュール
姿勢診断結果をLINE Messaging APIで送信
"""

import os
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class LINENotifier:
    """LINE通知クラス"""
    
    def __init__(self):
        """LINE通知器を初期化"""
        self.channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
        self.line_api_url = 'https://api.line.me/v2/bot/message/push'
        
        if not self.channel_access_token:
            logger.warning("LINE_CHANNEL_ACCESS_TOKENが設定されていません。LINE通知機能は利用できません。")
    
    def is_available(self) -> bool:
        """LINE通知が利用可能か確認"""
        return self.channel_access_token is not None
    
    def send_posture_diagnosis(
        self,
        line_user_id: str,
        user_name: str,
        analysis: Dict[str, Any],
        report_image_url: Optional[str] = None,
        xray_image_url: Optional[str] = None,
        visualized_image_url: Optional[str] = None,
        base_url: str = ""
    ) -> bool:
        """
        姿勢診断結果をLINEで送信
        
        Args:
            line_user_id: LINEユーザーID
            user_name: ユーザー名
            analysis: 姿勢分析結果
            report_image_url: 診断結果レポート画像のURL
            xray_image_url: X線透視風画像のURL
            visualized_image_url: 可視化画像のURL
            base_url: ベースURL（画像URLが相対パスの場合）
        
        Returns:
            成功した場合True
        """
        if not self.is_available():
            logger.error("LINE通知機能が利用できません（チャネルアクセストークンが設定されていません）")
            return False
        
        try:
            # メッセージを構築
            messages = []
            
            # 1. タイトルメッセージ
            overall_score = int(analysis.get('overall_score', 0.0) * 100)
            score_emoji = "🟢" if overall_score >= 80 else ("🟡" if overall_score >= 60 else "🔴")
            
            title_message = f"""
{score_emoji} 姿勢診断結果レポート

{user_name}様の姿勢診断が完了しました。

📊 総合スコア: {overall_score}/100点
📅 診断日時: {self._format_timestamp(analysis.get('timestamp'))}
            """.strip()
            
            messages.append({
                "type": "text",
                "text": title_message
            })
            
            # 2. 整列スコア
            alignment_scores = analysis.get('alignment_scores', {})
            if alignment_scores:
                alignment_text = "📐 整列スコア:\n"
                alignment_labels = {
                    'shoulder_alignment': '肩の水平度',
                    'hip_alignment': '骨盤の水平度',
                    'head_alignment': '頭部の位置',
                    'spine_alignment': '背骨の整列',
                    'knee_alignment': '膝の位置'
                }
                
                for key, value in alignment_scores.items():
                    label = alignment_labels.get(key, key)
                    score = int(value * 100)
                    emoji = "🟢" if score >= 80 else ("🟡" if score >= 60 else "🔴")
                    alignment_text += f"{emoji} {label}: {score}点\n"
                
                messages.append({
                    "type": "text",
                    "text": alignment_text.strip()
                })
            
            # 3. 検出された問題
            issues = analysis.get('issues', [])
            if issues:
                issues_text = "⚠️ 検出された問題:\n\n"
                for issue in issues[:5]:  # 最大5件
                    severity = issue.get('severity', 'medium')
                    description = issue.get('description', '')
                    impact = issue.get('impact', '')
                    
                    severity_emoji = {
                        'high': '🔴',
                        'medium': '🟡',
                        'low': '🔵'
                    }.get(severity, '⚪')
                    
                    issues_text += f"{severity_emoji} {description}\n"
                    if impact:
                        issues_text += f"   → {impact}\n"
                    issues_text += "\n"
                
                messages.append({
                    "type": "text",
                    "text": issues_text.strip()
                })
            
            # 4. 改善提案
            recommendations = analysis.get('recommendations', [])
            if recommendations:
                rec_text = "💡 改善提案:\n\n"
                for i, rec in enumerate(recommendations[:5], 1):  # 最大5件
                    rec_text += f"{i}. {rec}\n"
                
                messages.append({
                    "type": "text",
                    "text": rec_text.strip()
                })
            
            # 5. 筋肉評価
            muscle_assessment = analysis.get('muscle_assessment', {})
            if muscle_assessment:
                muscle_text = "💪 筋肉評価:\n\n"
                
                tight_muscles = muscle_assessment.get('tight_muscles', [])
                if tight_muscles:
                    muscle_text += "🔴 硬い可能性のある筋肉:\n"
                    for muscle in tight_muscles[:3]:  # 最大3件
                        name = muscle.get('name', '')
                        muscle_text += f"  • {name}\n"
                    muscle_text += "\n"
                
                stretch_needed = muscle_assessment.get('stretch_needed', [])
                if stretch_needed:
                    muscle_text += "🟢 ストレッチが必要:\n"
                    for stretch in stretch_needed[:3]:  # 最大3件
                        muscle = stretch.get('muscle', '')
                        method = stretch.get('method', '')
                        muscle_text += f"  • {muscle}: {method}\n"
                    muscle_text += "\n"
                
                strengthen_needed = muscle_assessment.get('strengthen_needed', [])
                if strengthen_needed:
                    muscle_text += "🔵 強化が必要:\n"
                    for strengthen in strengthen_needed[:3]:  # 最大3件
                        muscle = strengthen.get('muscle', '')
                        exercise = strengthen.get('exercise', '')
                        muscle_text += f"  • {muscle}: {exercise}\n"
                
                if muscle_text.strip() != "💪 筋肉評価:":
                    messages.append({
                        "type": "text",
                        "text": muscle_text.strip()
                    })
            
            # 6. 画像を追加（診断結果レポート画像を優先）
            if report_image_url:
                image_url = self._get_full_url(report_image_url, base_url)
                if image_url:
                    messages.append({
                        "type": "image",
                        "originalContentUrl": image_url,
                        "previewImageUrl": image_url
                    })
            elif visualized_image_url:
                image_url = self._get_full_url(visualized_image_url, base_url)
                if image_url:
                    messages.append({
                        "type": "image",
                        "originalContentUrl": image_url,
                        "previewImageUrl": image_url
                    })
            
            # 7. フッターメッセージ
            footer_message = """
━━━━━━━━━━━━━━━━
📱 STLINE AI パーソナルトレーナー
姿勢診断結果レポート

詳細はWebダッシュボードで確認できます。
            """.strip()
            
            messages.append({
                "type": "text",
                "text": footer_message
            })
            
            # LINE APIに送信
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.channel_access_token}'
            }
            
            payload = {
                "to": line_user_id,
                "messages": messages
            }
            
            response = requests.post(self.line_api_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"LINE通知を送信しました: user_id={line_user_id}")
                return True
            else:
                logger.error(f"LINE通知送信エラー: {response.status_code} - {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"LINE通知送信エラー: {e}", exc_info=True)
            return False
    
    def _format_timestamp(self, timestamp: Any) -> str:
        """タイムスタンプをフォーマット"""
        try:
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            elif isinstance(timestamp, datetime):
                dt = timestamp
            else:
                return "不明"
            
            return dt.strftime('%Y年%m月%d日 %H:%M')
        except:
            return "不明"
    
    def _get_full_url(self, url: str, base_url: str) -> Optional[str]:
        """完全なURLを取得"""
        if not url:
            return None
        
        if url.startswith('http://') or url.startswith('https://'):
            return url
        
        if base_url:
            # base_urlの末尾にスラッシュがあるか確認
            if not base_url.endswith('/'):
                base_url += '/'
            
            # urlの先頭のスラッシュを削除
            if url.startswith('/'):
                url = url[1:]
            
            full_url = base_url + url
            
            # Railway環境の場合、HTTPSを使用
            if 'railway.app' in base_url and full_url.startswith('http://'):
                full_url = full_url.replace('http://', 'https://')
            
            return full_url
        
        return None

