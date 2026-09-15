"""Configuration de l'application, chargée depuis les variables d'environnement.

Toutes les valeurs peuvent être définies dans un fichier `.env` placé à la
racine du dossier `backend/` (voir `.env.example`), ou directement comme
variables d'environnement (pratique pour Docker).
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # URL de base de l'instance Celcat (sans slash final), utilisée si le
    # paramètre `base_url` n'est pas fourni dans l'appel à l'API.
    celcat_base_url: str = Field(
        default="https://celcat.u-bordeaux.fr/calendar",
        description="URL de base de l'instance Celcat par défaut.",
    )

    # Cookie de session Celcat par défaut (récupéré manuellement depuis un
    # navigateur, cf. README). Utilisé si le paramètre `cookie` n'est pas
    # fourni dans l'appel à l'API. Permet d'exposer une URL de calendrier
    # "prête à l'emploi" sans avoir à transmettre le cookie à chaque appel.
    celcat_cookie: Optional[str] = Field(
        default=None,
        description="Cookie de session Celcat par défaut.",
    )

    # Groupe par défaut si non fourni dans la requête.
    celcat_default_group: Optional[str] = Field(default=None)

    # Nombre de jours par défaut couverts si `start`/`end` ne sont pas fournis.
    default_range_days: int = Field(default=90, ge=1)

    # Pause (en secondes) entre deux requêtes semaine par semaine vers Celcat.
    request_sleep_seconds: float = Field(default=0.4, ge=0)

    # Durée de vie du cache en mémoire (en secondes) pour éviter de
    # re-scraper Celcat à chaque appel identique. 0 désactive le cache.
    cache_ttl_seconds: int = Field(default=300, ge=0)

    # Origines autorisées pour CORS (séparées par des virgules), utile si le
    # frontend appelle l'API directement depuis le navigateur.
    cors_origins: str = Field(default="*")

    # Timeout HTTP (en secondes) pour chaque requête vers Celcat.
    request_timeout_seconds: float = Field(default=20.0, ge=1)

    @property
    def cors_origins_list(self) -> List[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
