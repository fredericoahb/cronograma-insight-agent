from __future__ import annotations

import os


class Settings:
    app_name: str = "Cronograma Insight Agent API"
    frontend_title: str = "Cronograma Insight Agent"
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "20"))


settings = Settings()
