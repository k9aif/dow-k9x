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


def build_info() -> dict:
    """What is running: VERSION from the repo; the commit and build date baked into the image by
    build-run.sh (DAS_COMMIT / DAS_BUILT; the image has no .git), or read from git in a checkout;
    and the installed K9-AIF framework version."""
    import subprocess
    from importlib.metadata import PackageNotFoundError, version as pkg_version
    ver_file = _PROJECT_ROOT / "VERSION"
    version = ver_file.read_text().strip() if ver_file.exists() else "dev"
    commit = _env("DAS_COMMIT").strip()
    built = _env("DAS_BUILT").strip()
    if not commit or commit == "unknown":
        try:
            commit = subprocess.run(["git", "-C", str(_PROJECT_ROOT), "rev-parse", "--short", "HEAD"],
                                    capture_output=True, text=True, timeout=3).stdout.strip()
        except Exception:
            commit = ""
    try:
        k9aif = pkg_version("k9-aif")
    except PackageNotFoundError:
        k9aif = "not installed"
    return {"version": version, "commit": commit or "unknown",
            "built": built if built and built != "unknown" else "local run", "k9_aif": k9aif}


class Settings:
    ENV = _env("K9_DOW_ENV", "local")
    ACTIVE_LLM = _env("K9_DOW_ACTIVE_LLM", "ollama")

    OLLAMA_HOST = _env("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL = _env("OLLAMA_MODEL", "qwen3.8:27b")  # same default as config.yaml
    # Context window for every agent model call (.env), one value for all agent
    # aliases so the model never reloads between steps. Deployment setting:
    # size it to the GPU (PowerAI's 5090: 32768 or 65536), not to the design.
    OLLAMA_NUM_CTX = int(_env("OLLAMA_NUM_CTX", "32768"))
    OLLAMA_DISPLAY_NAME = _env("OLLAMA_DISPLAY_NAME", "")

    # Knowledge-corpus disclosure -- surfaced in every generated ICD (see
    # icd_composer.py) so a reviewer knows whether DoDAF views were enriched
    # against real reference material or reflect only the input document.
    KNOWLEDGE_CORPUS_LABEL = _env("KNOWLEDGE_CORPUS_LABEL", "None")

    POSTGRES_HOST = _env("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(_env("POSTGRES_PORT", "5432"))
    POSTGRES_DB = _env("POSTGRES_DB", "dow")
    POSTGRES_USER = _env("POSTGRES_USER", "postgres")
    # Actual deployed env var is K9_PG_PASSWORD (see RHEL/das-pod.yaml);
    # POSTGRES_PASSWORD kept as a fallback for .env.example's naming.
    POSTGRES_PASSWORD = _env("K9_PG_PASSWORD", _env("POSTGRES_PASSWORD", ""))

    NEO4J_URI = _env("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = _env("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = _env("NEO4J_PASSWORD", "")

    KAFKA_BOOTSTRAP_SERVERS = _env("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

    S3_ENDPOINT_URL = _env("S3_ENDPOINT_URL", "http://localhost:9000")
    S3_ACCESS_KEY = _env("S3_ACCESS_KEY", "")
    S3_SECRET_KEY = _env("S3_SECRET_KEY", "")

    DOCLING_ENDPOINT = _env("DOCLING_ENDPOINT", "http://localhost:5001/v1/convert/file")

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
