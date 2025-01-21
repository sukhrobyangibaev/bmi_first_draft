import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

@dataclass
class Config:
    """Configuration settings for the thesis generator."""
    API_KEY: str
    BASE_URL: str
    MODEL: str
    LOW_RATE_LIMITS: bool
    PROJECT_FILES_DIR: str
    TRANSLATION_LANG: Optional[str]

    @classmethod
    def from_env(cls) -> 'Config':
        """Create Config instance from environment variables."""
        load_dotenv()
        
        return cls(
            API_KEY=os.environ.get("API_KEY", ""),
            BASE_URL=os.environ.get("BASE_URL", ""),
            MODEL=os.environ.get("MODEL", ""),
            LOW_RATE_LIMITS=os.environ.get("LOW_RATE_LIMITS") == "true",
            PROJECT_FILES_DIR=os.environ.get("PROJECT_FILES_DIR", ""),
            TRANSLATION_LANG=os.environ.get("TRANSLATION_LANG")
        ) 