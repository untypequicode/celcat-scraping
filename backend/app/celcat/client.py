"""Client HTTP pour récupérer les événements d'un calendrier Celcat.

L'instance Celcat exige une authentification SSO (Shibboleth/SAML), même pour
un simple groupe. Ce module n'automatise PAS le login : il réutilise un
cookie de session déjà authentifié, récupéré manuellement depuis un
navigateur (cf. README du dossier `backend/`).
"""

import datetime as dt
import logging
import time
import urllib.parse
from typing import Any, Dict, Iterator, List, Tuple

import requests

from ..core.exceptions import CelcatAuthError, CelcatError
from .converter import event_key

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; celcat-to-ics/1.0)",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
}

# Correspondance entre le type de ressource Celcat (paramètre "et" de l'URL
# du calendrier, ex: ?et=group&fid0=...) et le code numérique "resType"
# attendu par l'endpoint interne GetCalendarData.
#
# Valeur confirmée via les DevTools du navigateur : group = 103.
# Les valeurs room/module sont déduites par convention (103/104/105) et
# n'ont pas encore été vérifiées sur l'instance u-bordeaux.fr : si une
# recherche par matière ou par salle renvoie une liste vide alors que le
# lien Celcat correspondant affiche bien des cours, corrige les valeurs
# ci-dessous en les relevant depuis l'onglet Réseau (requête
# GetCalendarData, champ "resType") sur le lien concerné.
RESOURCE_TYPE_CODES = {
    "group": "103",
    "room": "104",
    "module": "105",
}


def _get_session(
    base_url: str, cookie_header: str, resource_type: str, resource_id: str
) -> requests.Session:
    """Construit une session `requests` réutilisant un cookie déjà authentifié."""
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    session.headers["Cookie"] = cookie_header.strip()
    session.headers["Origin"] = base_url.split("/calendar")[0]
    session.headers["Referer"] = (
        f"{base_url}/cal?vt=agendaWeek&et={resource_type}&fid0={urllib.parse.quote(resource_id)}"
    )
    return session


def _daterange_weeks(start: dt.date, end: dt.date) -> Iterator[Tuple[dt.date, dt.date]]:
    """Découpe [start, end] en tranches de 7 jours."""
    current = start
    while current <= end:
        week_end = min(current + dt.timedelta(days=6), end)
        yield current, week_end
        current = week_end + dt.timedelta(days=1)


def _fetch_week(
    session: requests.Session,
    base_url: str,
    resource_type: str,
    resource_id: str,
    start: dt.date,
    end: dt.date,
    timeout: float,
) -> List[Dict[str, Any]]:
    """Appelle l'endpoint Celcat pour une semaine donnée."""
    url = f"{base_url}/Home/GetCalendarData"
    payload = {
        "start": start.isoformat(),
        "end": (end + dt.timedelta(days=1)).isoformat(),  # borne exclusive côté Celcat
        "resType": RESOURCE_TYPE_CODES[resource_type],
        "calView": "agendaWeek",
        "federationIds[]": resource_id,
        "colourScheme": "3",
    }

    resp = session.post(url, data=payload, timeout=timeout)

    if resp.status_code in (401, 403):
        raise CelcatAuthError(
            "Accès refusé (401/403). Le cookie de session est probablement "
            "expiré ou invalide : récupère-en un nouveau depuis le navigateur."
        )
    resp.raise_for_status()

    if not resp.text.strip():
        raise CelcatAuthError(
            "Réponse vide (corps vide, statut 200). C'est typiquement le "
            "signe que le cookie de session est expiré ou invalide."
        )

    try:
        data = resp.json()
    except ValueError as exc:
        raise CelcatError(
            f"Réponse non-JSON reçue pour la semaine {start} -> {end}. "
            f"Extrait de la réponse: {resp.text[:300]!r}"
        ) from exc

    if isinstance(data, dict) and "events" in data:
        return data["events"]
    if isinstance(data, list):
        return data
    return []


def fetch_all_events(
    base_url: str,
    resource_type: str,
    resource_id: str,
    start: dt.date,
    end: dt.date,
    cookie_header: str,
    sleep_between_requests: float = 0.4,
    timeout: float = 20.0,
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Boucle sur toutes les semaines entre start et end et agrège les events.

    `resource_type` doit être l'une des clés de `RESOURCE_TYPE_CODES`
    ("group", "room" ou "module").

    Retourne (events, log_lines) — log_lines contient les erreurs par semaine
    (une semaine en erreur n'interrompt pas la récupération des autres,
    sauf en cas d'erreur d'authentification qui est immédiatement remontée).
    """
    if not cookie_header:
        raise CelcatAuthError(
            "Aucun cookie de session Celcat fourni (ni en paramètre, ni en "
            "configuration serveur)."
        )

    if resource_type not in RESOURCE_TYPE_CODES:
        raise CelcatError(
            f"Type de ressource inconnu: {resource_type!r}. "
            f"Valeurs acceptées: {', '.join(RESOURCE_TYPE_CODES)}."
        )

    session = _get_session(base_url, cookie_header, resource_type, resource_id)

    all_events: Dict[str, Dict[str, Any]] = {}
    log_lines: List[str] = []

    weeks = list(_daterange_weeks(start, end))
    for i, (week_start, week_end) in enumerate(weeks, start=1):
        logger.info(
            "[%d/%d] Récupération %s -> %s", i, len(weeks), week_start, week_end
        )
        try:
            events = _fetch_week(
                session,
                base_url,
                resource_type,
                resource_id,
                week_start,
                week_end,
                timeout,
            )
        except CelcatAuthError:
            # Un cookie invalide reste invalide pour toutes les autres
            # semaines : inutile de continuer à boucler.
            raise
        except CelcatError as exc:
            msg = f"ERREUR semaine {week_start} -> {week_end}: {exc}"
            logger.warning(msg)
            log_lines.append(msg)
            continue

        for ev in events:
            all_events[event_key(ev)] = ev

        if sleep_between_requests and i < len(weeks):
            time.sleep(sleep_between_requests)

    return list(all_events.values()), log_lines
