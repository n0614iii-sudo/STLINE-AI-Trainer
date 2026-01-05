#!/usr/bin/env python3
"""
PDF生成モジュール
姿勢診断結果をPDF形式で出力
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.units import cm, mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    REPORTLAB_AVAILABLE = True
except ImportError as e:
    logger.warning(f"reportlabのインポートに失敗しました: {e}")
    REPORTLAB_AVAILABLE = False
    # ダミーオブジェクトを定義
    colors = None
    A4 = None
    cm = None
    ParagraphStyle = None
    SimpleDocTemplate = None
    Paragraph = None
    Spacer = None
    Image = None
    Table = None
    TableStyle = None

from PIL import Image as PILImage
import io

logger = logging.getLogger(__name__)


class PDFGenerator:
    """PDF生成クラス"""
    
    def __init__(self):
        """PDF生成器を初期化"""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlabがインストールされていません。pip install reportlabを実行してください。")
        
        self.styles = getSampleStyleSheet()
        self._setup_fonts()
        self._setup_custom_styles()
    
    def _setup_fonts(self):
        """日本語フォントを設定"""
        self.japanese_font_name = None
        
        try:
            # システムフォントを試す
            font_paths = [
                # Linux (Noto Sans CJK - インストール済み)
                '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
                '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
                '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.otf',
                # macOS
                '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
                '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc',
                '/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
                # Windows
                'C:/Windows/Fonts/msgothic.ttc',
                'C:/Windows/Fonts/msmincho.ttc',
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        # TTFontで登録を試みる
                        pdfmetrics.registerFont(TTFont('Japanese', font_path))
                        self.japanese_font_name = 'Japanese'
                        logger.info(f"日本語フォントを登録しました: {font_path}")
                        return
                    except Exception as e:
                        logger.debug(f"フォント登録失敗 ({font_path}): {e}")
                        continue
            
            # フォールバック: UnicodeCIDFontを使用
            try:
                # HeiseiKakuGo-W5 (平成角ゴシック) を試す
                pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
                self.japanese_font_name = 'HeiseiKakuGo-W5'
                logger.info("UnicodeCIDFont (HeiseiKakuGo-W5) を使用します")
                return
            except Exception as e1:
                logger.debug(f"UnicodeCIDFont (HeiseiKakuGo-W5) の登録に失敗: {e1}")
                try:
                    # HeiseiMin-W3 (平成明朝) を試す
                    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))
                    self.japanese_font_name = 'HeiseiMin-W3'
                    logger.info("UnicodeCIDFont (HeiseiMin-W3) を使用します")
                    return
                except Exception as e2:
                    logger.debug(f"UnicodeCIDFont (HeiseiMin-W3) の登録に失敗: {e2}")
            
            logger.warning("日本語フォントの登録に失敗しました。デフォルトフォントを使用します。")
            self.japanese_font_name = 'Helvetica'
        except Exception as e:
            logger.warning(f"フォント設定エラー: {e}")
            self.japanese_font_name = 'Helvetica'
    
    def _setup_custom_styles(self):
        """カスタムスタイルを設定"""
        # タイトルスタイル
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName=self.japanese_font_name if self.japanese_font_name and self.japanese_font_name != 'Helvetica' else 'Helvetica-Bold'
        )
        
        # 見出しスタイル
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            spaceBefore=12,
            fontName=self.japanese_font_name if self.japanese_font_name and self.japanese_font_name != 'Helvetica' else 'Helvetica-Bold'
        )
        
        # 本文スタイル
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=6,
            fontName=self.japanese_font_name if self.japanese_font_name and self.japanese_font_name != 'Helvetica' else 'Helvetica'
        )
        
        # スコアスタイル
        self.score_style = ParagraphStyle(
            'ScoreStyle',
            parent=self.styles['Normal'],
            fontSize=48,
            textColor=colors.HexColor('#10b981'),
            alignment=TA_CENTER,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )
    
    def generate_diagnosis_pdf(
        self,
        output_path: str,
        analysis: Dict[str, Any],
        user_id: str,
        user_name: Optional[str] = None,
        report_image_path: Optional[str] = None,
        xray_image_path: Optional[str] = None,
        visualized_image_path: Optional[str] = None
    ) -> bool:
        """
        診断結果をPDF形式で生成
        
        Args:
            output_path: PDF出力パス
            analysis: 姿勢分析結果
            user_id: ユーザーID
            user_name: ユーザー名（オプション）
            report_image_path: 診断結果レポート画像のパス（オプション）
            xray_image_path: X線透視風画像のパス（オプション）
            visualized_image_path: 可視化画像のパス（オプション）
        
        Returns:
            成功した場合True
        """
        try:
            # PDFドキュメントを作成
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # ストーリー（コンテンツ）を構築
            story = []
            
            # タイトル
            story.append(Paragraph("姿勢診断結果レポート", self.title_style))
            story.append(Spacer(1, 0.5*cm))
            
            # ユーザー情報
            if user_name:
                story.append(Paragraph(f"<b>ユーザー名:</b> {user_name}", self.body_style))
            story.append(Paragraph(f"<b>ユーザーID:</b> {user_id}", self.body_style))
            
            # 診断日時
            timestamp = analysis.get('timestamp', datetime.now().isoformat())
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except:
                    timestamp = datetime.now()
            
            story.append(Paragraph(f"<b>診断日時:</b> {timestamp.strftime('%Y年%m月%d日 %H:%M:%S')}", self.body_style))
            
            # 姿勢タイプ
            posture_type = analysis.get('posture_type', 'unknown')
            posture_type_names = {
                'standing_front': '立位（正面）',
                'standing_side': '立位（横向き）',
                'standing_back': '立位（背面）',
                'sitting': '座位',
                'walking': '歩行中',
                'auto': '自動判定'
            }
            posture_type_name = posture_type_names.get(posture_type, posture_type)
            story.append(Paragraph(f"<b>姿勢タイプ:</b> {posture_type_name}", self.body_style))
            
            story.append(Spacer(1, 0.5*cm))
            
            # 総合スコア
            overall_score = analysis.get('overall_score', 0.0)
            score_percent = int(overall_score * 100)
            score_color = colors.HexColor('#10b981') if score_percent >= 80 else (colors.HexColor('#f59e0b') if score_percent >= 60 else colors.HexColor('#ef4444'))
            
            score_style = ParagraphStyle(
                'ScoreStyle',
                parent=self.styles['Normal'],
                fontSize=48,
                textColor=score_color,
                alignment=TA_CENTER,
                spaceAfter=10,
                fontName='Helvetica-Bold'
            )
            
            story.append(Paragraph(f"{score_percent}", score_style))
            score_label_font = self.japanese_font_name if self.japanese_font_name and self.japanese_font_name != 'Helvetica' else 'Helvetica'
            story.append(Paragraph("<b>総合姿勢スコア</b>", ParagraphStyle('ScoreLabel', parent=self.styles['Normal'], fontSize=14, alignment=TA_CENTER, spaceAfter=20, fontName=score_label_font)))
            
            story.append(Spacer(1, 0.5*cm))
            
            # 画像を追加
            image_added = False
            
            # 診断結果レポート画像
            if report_image_path and os.path.exists(report_image_path):
                try:
                    img = self._prepare_image(report_image_path, max_width=16*cm)
                    if img:
                        story.append(KeepTogether([
                            Paragraph("<b>診断結果レポート画像</b>", self.heading_style),
                            img,
                            Spacer(1, 0.3*cm)
                        ]))
                        image_added = True
                except Exception as e:
                    logger.warning(f"診断結果レポート画像の追加エラー: {e}")
            
            # X線透視風画像
            if xray_image_path and os.path.exists(xray_image_path):
                try:
                    img = self._prepare_image(xray_image_path, max_width=16*cm)
                    if img:
                        story.append(KeepTogether([
                            Paragraph("<b>X線透視風 姿勢診断</b>", self.heading_style),
                            img,
                            Spacer(1, 0.3*cm)
                        ]))
                        image_added = True
                except Exception as e:
                    logger.warning(f"X線透視風画像の追加エラー: {e}")
            
            # 可視化画像（レポート画像がない場合）
            if not image_added and visualized_image_path and os.path.exists(visualized_image_path):
                try:
                    img = self._prepare_image(visualized_image_path, max_width=16*cm)
                    if img:
                        story.append(KeepTogether([
                            Paragraph("<b>姿勢分析結果画像</b>", self.heading_style),
                            img,
                            Spacer(1, 0.3*cm)
                        ]))
                except Exception as e:
                    logger.warning(f"可視化画像の追加エラー: {e}")
            
            story.append(Spacer(1, 0.5*cm))
            
            # 整列スコア
            alignment_scores = analysis.get('alignment_scores', {})
            if alignment_scores:
                story.append(Paragraph("<b>整列スコア</b>", self.heading_style))
                
                # テーブルデータを作成
                table_data = [['部位', 'スコア']]
                alignment_labels = {
                    'shoulder_alignment': '肩の水平度',
                    'hip_alignment': '骨盤の水平度',
                    'head_alignment': '頭部の位置',
                    'spine_alignment': '背骨の整列',
                    'knee_alignment': '膝の位置'
                }
                
                for key, value in alignment_scores.items():
                    label = alignment_labels.get(key, key)
                    score_percent = int(value * 100)
                    table_data.append([label, f"{score_percent}%"])
                
                # テーブルを作成
                table = Table(table_data, colWidths=[10*cm, 4*cm])
                table_font_name = self.japanese_font_name if self.japanese_font_name and self.japanese_font_name != 'Helvetica' else 'Helvetica-Bold'
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), table_font_name),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('FONTNAME', (0, 1), (-1, -1), self.japanese_font_name if self.japanese_font_name and self.japanese_font_name != 'Helvetica' else 'Helvetica'),
                ]))
                
                story.append(table)
                story.append(Spacer(1, 0.5*cm))
            
            # 検出された問題
            issues = analysis.get('issues', [])
            if issues:
                story.append(Paragraph("<b>検出された問題</b>", self.heading_style))
                
                severity_colors = {
                    'high': colors.HexColor('#ef4444'),
                    'medium': colors.HexColor('#f59e0b'),
                    'low': colors.HexColor('#3b82f6')
                }
                
                for issue in issues:
                    severity = issue.get('severity', 'medium')
                    description = issue.get('description', '')
                    impact = issue.get('impact', '')
                    
                    severity_text = severity.upper()
                    severity_color = severity_colors.get(severity, colors.grey)
                    
                    issue_font = self.japanese_font_name if self.japanese_font_name and self.japanese_font_name != 'Helvetica' else 'Helvetica'
                    story.append(Paragraph(
                        f"<b>[{severity_text}]</b> {description}",
                        ParagraphStyle('IssueStyle', parent=self.body_style, textColor=severity_color, leftIndent=20, fontName=issue_font)
                    ))
                    if impact:
                        story.append(Paragraph(
                            f"<i>{impact}</i>",
                            ParagraphStyle('ImpactStyle', parent=self.body_style, leftIndent=40, textColor=colors.HexColor('#6b7280'), fontName=issue_font)
                        ))
                    story.append(Spacer(1, 0.2*cm))
                
                story.append(Spacer(1, 0.3*cm))
            
            # 改善提案
            recommendations = analysis.get('recommendations', [])
            if recommendations:
                story.append(Paragraph("<b>改善提案</b>", self.heading_style))
                rec_font = self.japanese_font_name if self.japanese_font_name and self.japanese_font_name != 'Helvetica' else 'Helvetica'
                for rec in recommendations:
                    story.append(Paragraph(f"• {rec}", ParagraphStyle('RecStyle', parent=self.body_style, leftIndent=20, fontName=rec_font)))
                    story.append(Spacer(1, 0.2*cm))
                story.append(Spacer(1, 0.3*cm))
            
            # 筋肉評価
            muscle_assessment = analysis.get('muscle_assessment', {})
            if muscle_assessment:
                # 硬い可能性のある筋肉
                tight_muscles = muscle_assessment.get('tight_muscles', [])
                if tight_muscles:
                    story.append(Paragraph("<b>硬い可能性のある筋肉</b>", self.heading_style))
                    for muscle in tight_muscles:
                        name = muscle.get('name', '')
                        reason = muscle.get('reason', '')
                        severity = muscle.get('severity', 'medium')
                        muscle_font = self.japanese_font_name if self.japanese_font_name and self.japanese_font_name != 'Helvetica' else 'Helvetica'
                        story.append(Paragraph(
                            f"<b>• {name}</b>",
                            ParagraphStyle('MuscleStyle', parent=self.body_style, leftIndent=20, fontName=muscle_font)
                        ))
                        if reason:
                            story.append(Paragraph(
                                f"  {reason}",
                                ParagraphStyle('ReasonStyle', parent=self.body_style, leftIndent=40, textColor=colors.HexColor('#6b7280'), fontName=muscle_font)
                            ))
                        story.append(Spacer(1, 0.2*cm))
                    story.append(Spacer(1, 0.3*cm))
                
                # ストレッチが必要な筋肉
                stretch_needed = muscle_assessment.get('stretch_needed', [])
                if stretch_needed:
                    story.append(Paragraph("<b>ストレッチが必要な筋肉</b>", self.heading_style))
                    for stretch in stretch_needed:
                        muscle = stretch.get('muscle', '')
                        method = stretch.get('method', '')
                        frequency = stretch.get('frequency', '')
                        stretch_font = self.japanese_font_name if self.japanese_font_name and self.japanese_font_name != 'Helvetica' else 'Helvetica'
                        story.append(Paragraph(
                            f"<b>• {muscle}</b>: {method}",
                            ParagraphStyle('StretchStyle', parent=self.body_style, leftIndent=20, fontName=stretch_font)
                        ))
                        if frequency:
                            story.append(Paragraph(
                                f"  頻度: {frequency}",
                                ParagraphStyle('FreqStyle', parent=self.body_style, leftIndent=40, textColor=colors.HexColor('#6b7280'), fontName=stretch_font)
                            ))
                        story.append(Spacer(1, 0.2*cm))
                    story.append(Spacer(1, 0.3*cm))
                
                # 強化が必要な筋肉
                strengthen_needed = muscle_assessment.get('strengthen_needed', [])
                if strengthen_needed:
                    story.append(Paragraph("<b>強化が必要な筋肉</b>", self.heading_style))
                    for strengthen in strengthen_needed:
                        muscle = strengthen.get('muscle', '')
                        exercise = strengthen.get('exercise', '')
                        frequency = strengthen.get('frequency', '')
                        strengthen_font = self.japanese_font_name if self.japanese_font_name and self.japanese_font_name != 'Helvetica' else 'Helvetica'
                        story.append(Paragraph(
                            f"<b>• {muscle}</b>: {exercise}",
                            ParagraphStyle('StrengthenStyle', parent=self.body_style, leftIndent=20, fontName=strengthen_font)
                        ))
                        if frequency:
                            story.append(Paragraph(
                                f"  頻度: {frequency}",
                                ParagraphStyle('FreqStyle', parent=self.body_style, leftIndent=40, textColor=colors.HexColor('#6b7280'), fontName=strengthen_font)
                            ))
                        story.append(Spacer(1, 0.2*cm))
                    story.append(Spacer(1, 0.3*cm))
            
            # フッター
            story.append(Spacer(1, 1*cm))
            footer_font = self.japanese_font_name if self.japanese_font_name and self.japanese_font_name != 'Helvetica' else 'Helvetica'
            story.append(Paragraph(
                f"<i>このレポートは {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')} に生成されました。</i>",
                ParagraphStyle('FooterStyle', parent=self.styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey, fontName=footer_font)
            ))
            
            # PDFを生成
            doc.build(story)
            logger.info(f"PDFを生成しました: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"PDF生成エラー: {e}", exc_info=True)
            return False
    
    def _prepare_image(self, image_path: str, max_width: float = 16*cm) -> Optional[Image]:
        """
        画像をPDF用に準備
        
        Args:
            image_path: 画像パス
            max_width: 最大幅
        
        Returns:
            ImageオブジェクトまたはNone
        """
        try:
            # 画像を開いてサイズを確認
            pil_img = PILImage.open(image_path)
            img_width, img_height = pil_img.size
            
            # アスペクト比を保持してリサイズ
            aspect_ratio = img_height / img_width
            if img_width > max_width:
                width = max_width
                height = width * aspect_ratio
            else:
                width = img_width * 0.035  # cmに変換（1ピクセル ≈ 0.035cm）
                height = img_height * 0.035
            
            # 最大高さを制限（A4用紙の高さを考慮）
            max_height = 20*cm
            if height > max_height:
                height = max_height
                width = height / aspect_ratio
            
            return Image(image_path, width=width, height=height)
        except Exception as e:
            logger.warning(f"画像準備エラー ({image_path}): {e}")
            return None

