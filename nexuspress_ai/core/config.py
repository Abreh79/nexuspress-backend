import os
from pathlib import Path
from typing import Optional, Dict
from pydantic import BaseModel, Field


def load_env_file(file_path: str = ".env") -> Dict[str, str]:
    """Parse a .env file and set environment variables if not already set."""
    env_vars = {}
    path = Path(file_path)
    if path.exists() and path.is_file():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip("'\"")
                env_vars[key] = val
    return env_vars


class Settings(BaseModel):
    """Global configuration settings for NexusPress AI."""
    
    app_name: str = "NexusPress AI"
    environment: str = "development"
    
    # LLM Settings
    openai_api_key: Optional[str] = None
    default_model: str = "gpt-4o"
    
    # CMS Settings
    wordpress_url: Optional[str] = None
    wordpress_user: Optional[str] = None
    wordpress_app_password: Optional[str] = None

    @classmethod
    def from_env(cls, env_file: Optional[str] = ".env", **overrides) -> "Settings":
        """Load settings from .env file, OS environment variables, and manual overrides."""
        file_vars = load_env_file(env_file) if env_file else {}

        def get_val(key: str, default: Optional[str] = None) -> Optional[str]:
            if key in overrides and overrides[key] is not None:
                return overrides[key]
            if key in os.environ:
                return os.environ[key]
            if key in file_vars:
                return file_vars[key]
            return default

        return cls(
            environment=get_val("NEXUSPRESS_ENV", "development") or "development",
            openai_api_key=get_val("OPENAI_API_KEY"),
            default_model=get_val("NEXUSPRESS_MODEL", "gpt-4o") or "gpt-4o",
            wordpress_url=get_val("WP_URL"),
            wordpress_user=get_val("WP_USER"),
            wordpress_app_password=get_val("WP_APP_PASSWORD")
        )


settings = Settings.from_env()
