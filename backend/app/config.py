from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    arc_rpc_url: str = ""
    arc_chain_id: int = 0
    private_key_agent: str = ""
    private_key_reputation_recorder: str = ""

    erc8183_contract_address: str = ""
    identity_registry_address: str = ""
    reputation_registry_address: str = ""
    validation_registry_address: str = ""
    usdc_address: str = ""

    alphatrace_agent_address: str = "0x0000000000000000000000000000000000000000"
    alphatrace_agent_id: str = "demo-agent"
    alphatrace_agent_metadata_uri: str = "ipfs://alphatrace-demo-agent"

    database_url: str = "sqlite:///./alphatrace.db"
    openai_api_key: str = ""
    llm_provider: str = "mock"
    report_storage: str = "database"
    submit_to_chain: bool = False

    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

