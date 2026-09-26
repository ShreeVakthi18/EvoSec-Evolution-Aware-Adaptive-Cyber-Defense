"""
Centralized configuration for EAACD.

All tunables that were previously hard-coded in main.py are now sourced
from environment variables (with safe defaults), so the same codebase can
run in dev/staging/prod without code changes. See .env.example for the
full list of supported variables.
"""
from __future__ import annotations

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App / runtime ---
    app_env: str = Field(default="development", description="development | staging | production")
    debug: bool = Field(default=False, description="Enable verbose error responses. Must be False in prod.")
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000)

    # --- CORS ---
    # Comma-separated list of allowed origins. "*" only permitted outside production.
    cors_allow_origins: str = Field(default="http://localhost:8000")

    # --- Risk engine thresholds (preserves original EAACD scoring behavior) ---
    risk_suspicious_threshold: int = Field(default=3, ge=0)
    risk_attacker_threshold: int = Field(default=6, ge=0)
    risk_critical_endpoint_weight: int = Field(default=2, ge=0)
    risk_destructive_method_weight: int = Field(default=1, ge=0)
    risk_high_volume_weight: int = Field(default=1, ge=0)
    risk_high_volume_request_count: int = Field(default=10, ge=1)
    risk_admin_without_login_weight: int = Field(default=2, ge=0)
    critical_endpoint_min_requests: int = Field(default=3, ge=1)

    # --- Adaptive friction ---
    suspicious_response_delay_seconds: float = Field(default=1.0, ge=0.0)

    # --- Behavioral state bounds (prevents unbounded memory growth) ---
    max_tracked_users: int = Field(default=10_000, ge=1)
    max_history_per_user: int = Field(default=500, ge=1)
    user_idle_ttl_seconds: int = Field(default=3600, ge=1)

    # --- Request hardening ---
    max_request_body_bytes: int = Field(default=1_000_000, ge=1024)

    # --- Logging ---
    log_level: str = Field(default="INFO")
    log_json: bool = Field(default=True, description="Emit structured JSON logs")

    @field_validator("app_env")
    @classmethod
    def _validate_env(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"app_env must be one of {allowed}")
        return v

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def cors_origins_list(self) -> list[str]:
        origins = [o.strip() for o in self.cors_allow_origins.split(",") if o.strip()]
        if self.is_production and "*" in origins:
            # Never allow wildcard CORS in production; fail safe to same-origin only.
            return []
        return origins


settings = Settings()
