"""
STLINE AI Personal Trainer System
株式会社STLINE提供 - システム設定ファイル

開発: HIKARU NEJIKANE
バージョン: 1.0.0
リリース日: 2025年12月
"""

# 企業情報
COMPANY_INFO = {
    "name": "株式会社STLINE",
    "name_en": "STLINE Corporation",
    "developer": "HIKARU NEJIKANE",
    "product_name": "STLINE AI Personal Trainer",
    "version": "1.0.0",
    "release_date": "2025-12",
    "website": "https://stline.co.jp",
    "support_email": "support@stline.co.jp",
    "support_phone": "03-XXXX-XXXX",
    "copyright": "Copyright © 2025 STLINE Corporation. All Rights Reserved."
}

# ブランドカラー
BRAND_COLORS = {
    "primary": "#667eea",
    "secondary": "#764ba2",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "info": "#3b82f6",
    "light": "#f3f4f6",
    "dark": "#1f2937"
}

# UIテーマ設定
UI_THEME = {
    "company_logo_url": "/static/images/stline_logo.png",
    "favicon_url": "/static/images/favicon.ico",
    "primary_color": BRAND_COLORS["primary"],
    "secondary_color": BRAND_COLORS["secondary"],
    "sidebar_gradient": f"linear-gradient(135deg, {BRAND_COLORS['primary']} 0%, {BRAND_COLORS['secondary']} 100%)",
    "font_family": "'Noto Sans JP', sans-serif",
    "header_text": "STLINE AI Personal Trainer",
    "footer_text": f"Powered by Vision Agents | Designed by {COMPANY_INFO['developer']}"
}

# システム設定
SYSTEM_CONFIG = {
    "default_language": "ja",
    "supported_languages": ["ja", "en"],
    "timezone": "Asia/Tokyo",
    "date_format": "%Y年%m月%d日",
    "time_format": "%H:%M",
    "datetime_format": "%Y年%m月%d日 %H:%M"
}

# AI設定
AI_CONFIG = {
    "default_llm": "gemini",
    "default_fps": 5,
    "yolo_model": "yolo11n-pose.pt",
    "yolo_confidence": 0.3,
    "yolo_device": "cuda",  # または "cpu"
    "max_session_duration": 3600,  # 秒
    "auto_save_interval": 60  # 秒
}

# 運動メニュー拡張設定
EXERCISE_CONFIG = {
    "default_exercises": ["squat", "push_up", "deadlift", "plank"],
    "advanced_exercises": [],  # 将来の拡張用
    "custom_exercises": []  # カスタマイズ用
}

# データベース設定
DATABASE_CONFIG = {
    "type": "json",  # または "sqlite"
    "json_path": "stline_gym_data.json",
    "sqlite_path": "stline_gym_data.db",
    "backup_enabled": True,
    "backup_interval": 86400,  # 24時間
    "backup_retention": 30  # 日
}

# セキュリティ設定
SECURITY_CONFIG = {
    "session_timeout": 3600,  # 秒
    "max_login_attempts": 5,
    "password_min_length": 8,
    "require_strong_password": False,
    "enable_2fa": False,  # 将来の機能
    "api_rate_limit": 100  # リクエスト/分
}

# ライセンス設定
LICENSE_CONFIG = {
    "license_type": "commercial",
    "license_holder": "",  # 顧客名を設定
    "license_key": "",  # ライセンスキーを設定
    "expiry_date": None,  # None = 無期限
    "max_users": None,  # None = 無制限
    "max_concurrent_sessions": 5,  # スタータープランのデフォルト
    "features_enabled": {
        "web_dashboard": True,
        "ai_trainer": True,
        "data_export": True,
        "custom_exercises": False,  # 上位プランのみ
        "api_access": False,  # 上位プランのみ
        "white_label": False  # エンタープライズのみ
    }
}

# 通知設定
NOTIFICATION_CONFIG = {
    "email_enabled": True,
    "smtp_server": "smtp.stline.co.jp",
    "smtp_port": 587,
    "smtp_user": "noreply@stline.co.jp",
    "smtp_password": "",  # 環境変数から読み込み
    "from_address": "STLINE AI Trainer <noreply@stline.co.jp>",
    "admin_email": "support@stline.co.jp"
}

# ロギング設定
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - [STLINE] %(name)s - %(levelname)s - %(message)s",
    "file_path": "logs/stline_ai_trainer.log",
    "max_bytes": 10485760,  # 10MB
    "backup_count": 5,
    "enable_console": True,
    "enable_file": True
}

# パフォーマンス設定
PERFORMANCE_CONFIG = {
    "enable_caching": True,
    "cache_ttl": 300,  # 秒
    "enable_compression": True,
    "max_upload_size": 52428800,  # 50MB
    "enable_cdn": False,
    "cdn_url": ""
}

# 分析・レポート設定
ANALYTICS_CONFIG = {
    "enable_analytics": True,
    "tracking_id": "",  # Google Analytics等
    "report_generation": True,
    "report_formats": ["pdf", "excel", "json"],
    "auto_report_schedule": "weekly",  # daily, weekly, monthly
    "report_recipients": []
}

# カスタマイズ設定
CUSTOMIZATION_CONFIG = {
    "allow_custom_branding": False,  # エンタープライズプランのみ
    "custom_logo_path": None,
    "custom_colors": None,
    "custom_footer": None,
    "custom_welcome_message": None
}

def get_config(section=None):
    """設定を取得"""
    if section is None:
        return {
            "company": COMPANY_INFO,
            "brand_colors": BRAND_COLORS,
            "ui_theme": UI_THEME,
            "system": SYSTEM_CONFIG,
            "ai": AI_CONFIG,
            "exercise": EXERCISE_CONFIG,
            "database": DATABASE_CONFIG,
            "security": SECURITY_CONFIG,
            "license": LICENSE_CONFIG,
            "notification": NOTIFICATION_CONFIG,
            "logging": LOGGING_CONFIG,
            "performance": PERFORMANCE_CONFIG,
            "analytics": ANALYTICS_CONFIG,
            "customization": CUSTOMIZATION_CONFIG
        }
    
    configs = {
        "company": COMPANY_INFO,
        "brand_colors": BRAND_COLORS,
        "ui_theme": UI_THEME,
        "system": SYSTEM_CONFIG,
        "ai": AI_CONFIG,
        "exercise": EXERCISE_CONFIG,
        "database": DATABASE_CONFIG,
        "security": SECURITY_CONFIG,
        "license": LICENSE_CONFIG,
        "notification": NOTIFICATION_CONFIG,
        "logging": LOGGING_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "analytics": ANALYTICS_CONFIG,
        "customization": CUSTOMIZATION_CONFIG
    }
    
    return configs.get(section, {})

def validate_license():
    """ライセンスを検証"""
    # 実際の実装ではライセンスサーバーと通信
    license_config = LICENSE_CONFIG
    
    if not license_config["license_key"]:
        return {
            "valid": True,  # デモモード
            "type": "trial",
            "message": "トライアルモードで実行中"
        }
    
    # ここにライセンス検証ロジックを実装
    return {
        "valid": True,
        "type": license_config["license_type"],
        "message": "ライセンス有効"
    }

def get_feature_availability(feature_name):
    """機能の利用可否を確認"""
    return LICENSE_CONFIG["features_enabled"].get(feature_name, False)

def update_custom_branding(logo_path=None, colors=None, footer=None):
    """カスタムブランディングを更新（エンタープライズのみ）"""
    if not get_feature_availability("white_label"):
        return {
            "success": False,
            "message": "この機能はエンタープライズプランでのみ利用可能です"
        }
    
    if logo_path:
        CUSTOMIZATION_CONFIG["custom_logo_path"] = logo_path
    if colors:
        CUSTOMIZATION_CONFIG["custom_colors"] = colors
    if footer:
        CUSTOMIZATION_CONFIG["custom_footer"] = footer
    
    return {
        "success": True,
        "message": "カスタムブランディングを更新しました"
    }

# システム起動時のバナー表示
def print_startup_banner():
    """起動バナー表示"""
    banner = f"""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║          STLINE AI Personal Trainer System                ║
║                                                           ║
║  株式会社STLINE - 次世代パーソナルジムソリューション         ║
║                                                           ║
║  Designed by: {COMPANY_INFO['developer']}                           ║
║  Version: {COMPANY_INFO['version']}                                    ║
║  Release: {COMPANY_INFO['release_date']}                             ║
║                                                           ║
║  Powered by Vision Agents & YOLO11                        ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

{COMPANY_INFO['copyright']}
Support: {COMPANY_INFO['support_email']}
Website: {COMPANY_INFO['website']}
"""
    print(banner)

if __name__ == "__main__":
    # 設定表示
    print_startup_banner()
    
    # ライセンス検証
    license_info = validate_license()
    print(f"\n[ライセンス] {license_info['message']}")
    print(f"[タイプ] {license_info['type']}")
    
    # 利用可能機能表示
    print("\n[利用可能機能]")
    for feature, enabled in LICENSE_CONFIG["features_enabled"].items():
        status = "✓ 有効" if enabled else "✗ 無効"
        print(f"  {feature}: {status}")