from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent  # points to backend/


class Settings(BaseSettings):
    # LLM (must be a model that supports tool calling)
    groq_api_key: str = ""
    llm_model: str = "openai/gpt-oss-120b"

    # Agent safety limits
    max_agent_steps: int = 8           # stop the loop after this many LLM calls
    max_tool_output_chars: int = 3000  # cut long tool results to save tokens

    # Folders
    upload_dir: Path = BASE_DIR / "data" / "uploads"
    charts_dir: Path = BASE_DIR / "data" / "charts"

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")


settings = Settings()