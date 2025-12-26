# 📄 診断結果PDF出力機能

## ✅ 実装完了

診断結果全体をPDF形式で出力する機能を追加しました！

## 🎯 機能概要

姿勢診断の結果を包括的なPDFレポートとして出力できます。

### 含まれる内容

1. **基本情報**
   - ユーザー名
   - ユーザーID
   - 診断日時
   - 姿勢タイプ

2. **総合スコア**
   - 大きな数字で表示
   - スコアに応じた色分け（緑/オレンジ/赤）

3. **画像**
   - 診断結果レポート画像（優先）
   - X線透視風画像
   - 可視化画像（レポート画像がない場合）

4. **整列スコア**
   - テーブル形式で表示
   - 各部位のスコア（%）

5. **検出された問題**
   - 深刻度別に色分け
   - 問題の説明
   - 影響の説明

6. **改善提案**
   - 具体的な改善方法

7. **筋肉評価**
   - 硬い可能性のある筋肉
   - ストレッチが必要な筋肉
   - 強化が必要な筋肉

## 🚀 使用方法

### フロントエンド

1. **姿勢診断を実行**
   - 画像または動画をアップロード
   - 診断結果が表示される

2. **PDFダウンロードボタンをクリック**
   - 「診断結果をPDFでダウンロード」ボタンをクリック
   - PDFが自動的に生成され、ダウンロードされます

### API

```javascript
// PDF生成APIを呼び出し
const response = await fetch('/api/posture/pdf/' + userId, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        analysis: analysis,
        user_name: userName,
        report_image_url: reportImageUrl,
        xray_image_url: xrayImageUrl,
        visualized_image_url: visualizedImageUrl
    })
});
```

## 📋 技術詳細

### PDF生成ライブラリ

- **reportlab**: PDF生成ライブラリ
- **Pillow**: 画像処理（画像のリサイズなど）

### PDF生成プロセス

1. **データの準備**
   - 分析結果、画像パス、ユーザー情報を収集

2. **PDFドキュメントの作成**
   - A4サイズ
   - 適切なマージン設定

3. **コンテンツの追加**
   - タイトル
   - 基本情報
   - 総合スコア
   - 画像（リサイズ済み）
   - テーブル（整列スコア）
   - 問題点、改善提案、筋肉評価

4. **PDFの生成**
   - `doc.build(story)`でPDFを生成

### 画像の処理

- 画像をリサイズしてPDFに含める
- 最大幅: 16cm（A4用紙に収まるサイズ）
- アスペクト比を保持

### 日本語フォント

- システムフォントを自動検出
- macOS: ヒラギノ角ゴシック
- Linux: Noto Sans CJK
- Windows: MS Gothic / MS Mincho
- フォールバック: UnicodeCIDFont

## 🎨 PDFのデザイン

### 色使い

- **タイトル**: 青（#1e40af）
- **見出し**: 青（#1e40af）
- **総合スコア**: 
  - 80点以上: 緑（#10b981）
  - 60-79点: オレンジ（#f59e0b）
  - 60点未満: 赤（#ef4444）
- **問題の深刻度**:
  - High: 赤（#ef4444）
  - Medium: オレンジ（#f59e0b）
  - Low: 青（#3b82f6）

### レイアウト

- A4サイズ
- マージン: 2cm
- 適切なスペーシング
- テーブル形式の整列スコア

## 📁 ファイル構造

```
uploads/
  ├── pdfs/
  │   └── posture_report_{user_id}_{timestamp}.pdf
  ├── visualizations/
  │   ├── report_*.png
  │   ├── xray_*.png
  │   └── analyzed_*.png
  ├── images/
  └── videos/
```

## 🔧 実装ファイル

- `pdf_generator.py`: PDF生成クラス
- `gym_dashboard.py`: PDF生成APIエンドポイント
- `templates/posture_diagnosis_user.html`: PDFダウンロードボタン

## 🚀 次のステップ

1. **Railwayで再デプロイ**
   - `reportlab`がインストールされます
   - PDF生成機能が利用可能になります

2. **姿勢診断を実行**
   - 診断結果が表示されたら
   - 「診断結果をPDFでダウンロード」ボタンをクリック
   - PDFが生成・ダウンロードされることを確認

3. **確認事項**
   - PDFが正常に生成される
   - すべての情報が含まれている
   - 画像が正しく表示される
   - 日本語が正しく表示される

## 🎉 まとめ

診断結果全体をPDF形式で出力する機能を追加しました：

- ✅ PDF生成ライブラリ（reportlab）の追加
- ✅ PDF生成関数の実装
- ✅ PDFダウンロードAPIエンドポイントの追加
- ✅ フロントエンドにPDFダウンロードボタンを追加
- ✅ 診断結果、画像、評価情報を含む包括的なPDF

Railwayで再デプロイが完了したら、PDF出力機能が利用可能になります！

