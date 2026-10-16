from __future__ import annotations

from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the local simulation lab."""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="SENTINEL_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Sentinel UAS Assurance Lab"
    environment: str = "local-lab"

    observer_token: str = "observer-local-token"
    operator_token: str = "operator-local-token"
    auditor_token: str = "auditor-local-token"
    maintainer_token: str = "maintainer-local-token"

    geofence_min_x_m: float = -500.0
    geofence_max_x_m: float = 500.0
    geofence_min_y_m: float = -500.0
    geofence_max_y_m: float = 500.0
    restricted_min_x_m: float = 100.0
    restricted_max_x_m: float = 180.0
    restricted_min_y_m: float = -50.0
    restricted_max_y_m: float = 50.0

    max_altitude_m: float = 120.0
    min_launch_battery_pct: float = 30.0
    critical_battery_pct: float = 12.0
    min_launch_link_quality_pct: float = 55.0
    degraded_link_quality_pct: float = 30.0
    max_telemetry_age_seconds: int = 30
    max_clock_skew_seconds: int = 5
    max_command_ttl_seconds: int = 30
    battery_use_per_minute_pct: float = 0.35


DEFAULT_SETTINGS = Settings()
