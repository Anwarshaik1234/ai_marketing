import sys
import warnings
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./marketing.db"
    openai_api_key: str = ""
    # Optional: e.g. https://openrouter.ai/api/v1 for OpenRouter (OpenAI-compatible)
    openai_base_url: str = ""
    openai_model: str = "gpt-4o-mini"
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    # auto: OpenAI if OPENAI_API_KEY set, else Groq if GROQ_API_KEY set, else Ollama
    llm_provider: str = "auto"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    ollama_only: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.openai_api_key or self.openai_api_key == "sk-proj-your-api-key-here":
            self.openai_api_key = ""
        if not self.groq_api_key or self.groq_api_key.startswith("gsk-your-"):
            self.groq_api_key = ""
        self._check_config()
    
    def _check_config(self):
        """Check if LLM provider is configured."""
        has_openai = bool(self.openai_api_key)
        has_groq = bool(self.groq_api_key)
        has_cloud = has_openai or has_groq
        
        if not has_cloud and not self.ollama_only:
            warnings.warn(
                "\n⚠️  No cloud LLM API key configured!\n"
                "  • Free (Groq): https://console.groq.com/keys → GROQ_API_KEY=gsk_...\n"
                "  • OpenAI: https://platform.openai.com/api-keys → OPENAI_API_KEY=sk-...\n"
                "  • Local: install Ollama + run a model, or set OLLAMA_ONLY=true in backend/.env\n"
                "Note: ChatGPT (free web) is not an API key — use Groq or OpenAI platform keys.\n",
                RuntimeWarning,
                stacklevel=2
            )


settings = Settings()
