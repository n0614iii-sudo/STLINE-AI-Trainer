# 🔧 Railwayイメージサイズ削減

## 🔴 エラー内容

```
Image of size 8.5 GB exceeded limit of 4.0 GB. 
Upgrade your plan to increase the image size limit.
```

## ✅ 修正内容

### 1. torchとtorchvisionをCPU版に変更

- GPU版のtorchは非常に大きい（数GB）
- CPU版は約500MB程度に削減可能

### 2. .dockerignoreを最適化

- 不要なファイルを除外
- ドキュメント、テストファイル、スクリプトを除外

### 3. Dockerfileを最適化

- torchとtorchvisionをCPU版でインストール
- 依存関係のインストール順序を最適化

## 🚀 次のステップ

### ステップ1: 変更をGitHubにプッシュ

```bash
cd /Users/hikarunejikane/Downloads/STLINE-AI-Trainer
git add .
git commit -m "Reduce Docker image size: Use CPU-only torch"
git push
```

### ステップ2: Railwayで再デプロイ

1. Railwayのダッシュボードで「Redeploy」をクリック
2. ビルドが成功するまで待つ
3. イメージサイズが4GB以下になることを確認

## 📊 期待される結果

- **修正前**: 8.5 GB
- **修正後**: 約2-3 GB（CPU版torch使用）

## ⚠️ 注意事項

- CPU版のtorchを使用するため、GPU機能は使用できません
- Railwayの無料プランではGPUは使用できないため、問題ありません
- より高度な機能が必要な場合は、VPSを使用してください

## 🔄 もしまだサイズが大きい場合

### オプション1: さらに依存関係を削減

`requirements.txt`から不要なパッケージを削除：

```txt
# 最小限の依存関係のみ
flask>=2.3.0
python-dotenv>=1.0.0
vision-agents>=0.2.0
ultralytics>=8.0.0
opencv-python-headless>=4.8.0  # headless版（GUI不要）
numpy>=1.24.0
pillow>=10.0.0
torch>=2.0.0+cpu
torchvision>=0.15.0+cpu
requests>=2.31.0
```

### オプション2: マルチステージビルドを使用

より高度な最適化が必要な場合。

## 🎯 まとめ

1. **torchをCPU版に変更**: サイズを大幅に削減
2. **.dockerignoreを最適化**: 不要なファイルを除外
3. **GitHubにプッシュ**: 変更を反映
4. **Railwayで再デプロイ**: ビルドを再実行

これでイメージサイズが4GB以下になるはずです！



