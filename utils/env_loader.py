import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError


class SettingsError(Exception):
    pass


class AppSettings(BaseModel):
    gemini_api_key: str
    techletter_base_url: str
    vector_db_path: str
    gemini_model: str = "gemini-2.5-flash"
    embedding_model: str = "models/text-embedding-004"


def _read_config_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_settings(config_path: str | Path = "config.yaml") -> AppSettings:
    """왜: .env와 config.yaml을 병합해 단일 설정 소스로 사용한다."""
    load_dotenv()

    cfg = _read_config_file(Path(config_path))

    env = os.environ
    # env 우선, 없으면 config.yaml
    values: Dict[str, Any] = {
        "gemini_api_key": env.get("GEMINI_API_KEY") or (cfg.get("gemini", {}) or {}).get("api_key"),
        "techletter_base_url": env.get("TECHLETTER_BASE_URL") or (cfg.get("techletter", {}) or {}).get("base_url"),
        "vector_db_path": env.get("VECTOR_DB_PATH") or (cfg.get("vector_store", {}) or {}).get("path"),
        "gemini_model": env.get("GEMINI_MODEL") or (cfg.get("gemini", {}) or {}).get("model", "gemini-2.5-flash"),
        "embedding_model": env.get("EMBEDDING_MODEL") or (cfg.get("gemini", {}) or {}).get("embedding_model", "models/text-embedding-004"),
    }

    try:
        settings = AppSettings(**values)
    except ValidationError as e:
        raise SettingsError(f"설정 로드 실패: {e}") from e

    # 왜: google-generativeai SDK는 GOOGLE_API_KEY를 기대하므로 매핑한다.
    os.environ.setdefault("GOOGLE_API_KEY", settings.gemini_api_key)

    # 벡터 DB 경로 보장
    Path(settings.vector_db_path).mkdir(parents=True, exist_ok=True)
    return settings
