# 🔧 Railway OpenCVエラー解決

## 🔴 エラー内容

```
ImportError: libGL.so.1: cannot open shared object file: No such file or directory
```

このエラーは、OpenCV（cv2）がGUI関連のライブラリ（libGL.so.1）を必要としているが、Dockerイメージに含まれていないために発生しています。

## ✅ 解決方法

### opencv-python-headlessを使用

- **opencv-python**: GUI関連のライブラリが必要（libGL.so.1など）
- **opencv-python-headless**: GUI関連のライブラリが不要（サーバー環境に最適）

### 修正内容

`requirements-railway.txt`で`opencv-python`を`opencv-python-headless`に変更しました。

## 🚀 次のステップ

Railwayが自動的に再ビルドを開始します。

1. **ビルドログを確認**
   - Build Logsでビルドが成功するか確認

2. **デプロイログを確認**
   - Deploy LogsでOpenCVが正しくインポートされているか確認

3. **アプリケーションにアクセス**
   - 生成されたURLでアプリにアクセス
   - ダッシュボードが表示されれば成功です

## 📋 確認事項

- [ ] ビルドが成功しているか（Build Logs）
- [ ] OpenCVが正しくインストールされているか（Deploy Logs）
- [ ] アプリケーションが起動しているか（Deploy Logs）

## 🎯 まとめ

- **問題**: OpenCVがlibGL.so.1を必要としている
- **解決**: opencv-python-headlessを使用（GUI不要）
- **結果**: サーバー環境で動作可能

これでアプリケーションが正常に起動するはずです！

