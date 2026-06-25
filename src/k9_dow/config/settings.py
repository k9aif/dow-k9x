# SPDX-License-Identifier: Apache-2.0

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

_BASE_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _BASE_DIR.parent.parent.parent  # src/k9_dow/config -> project root


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


class Settings:
    ENV = _env("K9_DOW_ENV", "local")
    ACTIVE_LLM = _env("K9_DOW_ACTIVE_LLM", "ollama")

    OLLAMA_HOST = _env("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL = _env("OLLAMA_MODEL", "granite3.3:8b")

    POSTGRES_HOST = _env("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(_env("POSTGRES_PORT", "5432"))
    POSTGRES_DB = _env("POSTGRES_DB", "dow")
    POSTGRES_USER = _env("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = _env("POSTGRES_PASSWORD", "")

    NEO4J_URI = _env("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = _env("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = _env("NEO4J_PASSWORD", "")

    KAFKA_BOOTSTRAP_SERVERS = _env("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

    S3_ENDPOINT_URL = _env("S3_ENDPOINT_URL", "http://localhost:9000")
    S3_ACCESS_KEY = _env("S3_ACCESS_KEY", "")
    S3_SECRET_KEY = _env("S3_SECRET_KEY", "")

    DOCLING_ENDPOINT = _env("DOCLING_ENDPOINT", "http://localhost:5001/v1/parse")

    OUTPUT_DIR = _PROJECT_ROOT / "output_reports"
    CONFIG_DIR = _BASE_DIR

    REQUIRE_HIL_AFTER_STAGE2 = _env("K9_DOW_REQUIRE_HIL_AFTER_STAGE2", "false").lower() == "true"

    @classmethod
    def load_yaml(cls, filename: str) -> dict:
        path = cls.CONFIG_DIR / filename
        if not path.exists():
            return {}
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    @classmethod
    def routing_rules(cls) -> dict:
        return cls.load_yaml("routing_rules.yaml")

    @classmethod
    def stage_catalog(cls) -> dict:
        return cls.load_yaml("stage_catalog.yaml")

    @classmethod
    def load_prompt(cls, filename: str) -> str:
        path = cls.CONFIG_DIR / "prompts" / filename
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8").strip()

    @classmethod
    def common_grounding_rules(cls) -> str:
        return cls.load_prompt("common_grounding_rules.md")

    @classmethod
    def governance_rules(cls) -> str:
        return cls.load_prompt("governance_rules.md")


settings = Settings()
