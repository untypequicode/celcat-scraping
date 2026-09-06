"""Orchestration : résolution des paramètres, récupération Celcat, cache."""

import datetime as dt
import hashlib
import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .celcat.client import fetch_all_events
from .celcat.converter import build_ics
from .core.cache import ics_cache
from .core.config import Settings
from .core.exceptions import CelcatAuthError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ResolvedRequest:
    base_url: str
    group: str
    cookie: str
    start: dt.date
    end: dt.date
    calendar_name: str


def resolve_request(
    *,
    group: Optional[str],
    start: Optional[dt.date],
    end: Optional[dt.date],
    base_url: Optional[str],
    cookie: Optional[str],
    calendar_name: Optional[str],
    settings: Settings,
) -> ResolvedRequest:
    """Applique les valeurs par défaut et valide les paramètres d'une requête.

    Lève `ValueError` pour un paramètre invalide/manquant, et
    `CelcatAuthError` si aucun cookie de session n'est disponible.
    """
    resolved_group = group or settings.celcat_default_group
    if not resolved_group:
        raise ValueError(
            "Le paramètre 'group' est requis (aucun CELCAT_DEFAULT_GROUP configuré)."
        )

    resolved_cookie = cookie or settings.celcat_cookie
    if not resolved_cookie:
        raise CelcatAuthError(
            "Aucun cookie de session Celcat fourni. Passe le paramètre 'cookie' "
            "dans l'URL ou configure CELCAT_COOKIE côté serveur."
        )

    resolved_start = start or dt.date.today()
    resolved_end = end or (
        resolved_start + dt.timedelta(days=settings.default_range_days)
    )
    if resolved_end < resolved_start:
        raise ValueError("Le paramètre 'end' doit être postérieur ou égal à 'start'.")

    return ResolvedRequest(
        base_url=(base_url or settings.celcat_base_url).rstrip("/"),
        group=resolved_group,
        cookie=resolved_cookie,
        start=resolved_start,
        end=resolved_end,
        calendar_name=calendar_name or resolved_group,
    )


def _cache_key(
    base_url: str, group: str, start: dt.date, end: dt.date, cookie: str
) -> str:
    cookie_hash = hashlib.sha256(cookie.encode("utf-8")).hexdigest()[:16]
    return f"{base_url}|{group}|{start.isoformat()}|{end.isoformat()}|{cookie_hash}"


def generate_calendar_ics(
    *,
    base_url: str,
    group: str,
    start: dt.date,
    end: dt.date,
    cookie: str,
    calendar_name: str,
    settings: Settings,
    use_cache: bool = True,
) -> Tuple[bytes, List[str]]:
    """Récupère les événements Celcat et renvoie (contenu_ics, lignes_de_log)."""
    cache_key = _cache_key(base_url, group, start, end, cookie)

    if use_cache and settings.cache_ttl_seconds > 0:
        cached = ics_cache.get(cache_key)
        if cached is not None:
            logger.info("Cache hit pour group=%s start=%s end=%s", group, start, end)
            return cached

    events, fetch_log = fetch_all_events(
        base_url=base_url,
        group=group,
        start=start,
        end=end,
        cookie_header=cookie,
        sleep_between_requests=settings.request_sleep_seconds,
        timeout=settings.request_timeout_seconds,
    )
    logger.info(
        "%d événement(s) unique(s) récupéré(s) pour group=%s", len(events), group
    )

    cal, build_log = build_ics(events, calendar_name=calendar_name)
    ics_bytes = cal.to_ical()
    log_lines = fetch_log + build_log

    if use_cache and settings.cache_ttl_seconds > 0:
        ics_cache.set(cache_key, (ics_bytes, log_lines), settings.cache_ttl_seconds)

    return ics_bytes, log_lines
