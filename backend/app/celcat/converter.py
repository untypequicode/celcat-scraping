"""Conversion des événements JSON Celcat en calendrier iCalendar.

Le champ "description" (ou "notes"/"modules" selon l'instance) renvoyé par
Celcat contient un bloc pseudo-HTML pré-formaté combinant toutes les
informations utiles (catégorie, titre, groupes, enseignant(s), salle,
semaines, remarques), séparées par des `<br/>` doubles entre blocs et des
`<br/>` simples entre éléments d'un même bloc.

Ce module regroupe tout le pipeline de conversion :
    JSON Celcat -> parse_celcat_blob -> event_from_json -> build_ics
"""

import datetime as dt
import hashlib
import html
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from icalendar import Calendar, Event

logger = logging.getLogger(__name__)

# Un <br/> entouré de retours à la ligne (ligne vide avant/après) sépare les
# grands blocs d'information ; un <br/> "collé" (sans \n autour) sépare les
# éléments à l'intérieur d'un même bloc (ex: plusieurs groupes sur une ligne).
_BLOCK_SEP_RE = re.compile(r"\n+\s*<br\s*/?>\s*\n+", re.IGNORECASE)
_ITEM_SEP_RE = re.compile(r"\s*<br\s*/?>\s*", re.IGNORECASE)


def parse_celcat_blob(raw: str) -> Dict[str, Any]:
    """
    Décompose le bloc pseudo-HTML renvoyé par Celcat en ses composantes.

    Structure observée (dans cet ordre, séparé par des doubles <br/>) :
        0. Catégorie / type d'événement (ex: "Cours", "TD Machine")
        1. Titre (module ou intitulé de l'événement)
        2. Groupe(s) concerné(s)          (séparés par un simple <br/>)
        3. Enseignant(s)                  (séparés par un simple <br/>)
        4. Salle
        5. Semaines (ex: "36-43,45-48")
        6. Remarques libres (séparées par des retours à la ligne littéraux)

    Tous les blocs sont optionnels au-delà du 2e : un événement peut très
    bien s'arrêter après la salle ou les semaines, sans remarques.
    """
    if not raw:
        return {}

    text = html.unescape(raw).strip()
    blocks = [b.strip() for b in _BLOCK_SEP_RE.split(text)]

    def split_items(block: str) -> List[str]:
        return [i.strip() for i in _ITEM_SEP_RE.split(block) if i.strip()]

    result: Dict[str, Any] = {
        "category": blocks[0] if len(blocks) > 0 else "",
        "title": blocks[1] if len(blocks) > 1 else "",
        "groups": split_items(blocks[2]) if len(blocks) > 2 else [],
        "teachers": split_items(blocks[3]) if len(blocks) > 3 else [],
        "room": blocks[4] if len(blocks) > 4 else "",
        "weeks": blocks[5] if len(blocks) > 5 else "",
        "notes": [],
    }

    if len(blocks) > 6:
        notes_raw = "\n".join(blocks[6:])
        result["notes"] = [n.strip() for n in notes_raw.split("\n") if n.strip()]

    return result


def _first_present(ev: Dict[str, Any], *keys: str) -> Optional[Any]:
    for k in keys:
        if k in ev and ev[k]:
            return ev[k]
    return None


def _join_list(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(v) for v in value if v)
    return str(value)


def _parse_dt(value: str) -> dt.datetime:
    """Parse les timestamps Celcat (format ISO 8601, avec ou sans fuseau)."""
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def event_key(ev: Dict[str, Any]) -> str:
    """Clé unique pour dédoublonner un événement (id natif si présent, sinon hash)."""
    if ev.get("id"):
        return str(ev["id"])
    raw = f"{ev.get('start')}|{ev.get('end')}|{ev.get('description') or ev.get('modules')}"
    return hashlib.sha1(raw.encode("utf-8", errors="ignore")).hexdigest()


def event_from_json(ev: Dict[str, Any]) -> Tuple[Optional[Event], Optional[str]]:
    """
    Construit un événement icalendar.Event à partir d'un dict JSON Celcat.

    Retourne (event, None) en cas de succès, ou (None, raison) si l'événement
    est ignoré — la raison est destinée au log.
    """
    start_raw = ev.get("start")
    end_raw = ev.get("end")
    if not start_raw or not end_raw:
        return None, f"start/end manquant (start={start_raw!r}, end={end_raw!r})"

    try:
        start = _parse_dt(start_raw)
        end = _parse_dt(end_raw)
    except ValueError as exc:
        return None, f"date illisible (start={start_raw!r}, end={end_raw!r}): {exc}"

    parsed = parse_celcat_blob(
        _first_present(ev, "description", "notes", "modules") or ""
    )

    category = parsed.get("category") or _first_present(ev, "eventCategory") or ""
    title = parsed.get("title") or category or "Cours"
    groups = parsed.get("groups") or []
    teachers = parsed.get("teachers") or []
    room_from_blob = parsed.get("room") or ""
    weeks = parsed.get("weeks") or ""
    notes = parsed.get("notes") or []

    # Salle : on préfère un champ JSON dédié plus propre s'il existe,
    # sinon on retombe sur la salle extraite du bloc pseudo-HTML.
    location = (
        _join_list(_first_present(ev, "sites", "rooms", "room")) or room_from_blob
    )

    description_lines = []
    if category and category != title:
        description_lines.append(f"Type: {category}")
    if teachers:
        description_lines.append("Enseignant(s): " + ", ".join(teachers))
    if groups:
        description_lines.append("Groupe(s): " + ", ".join(groups))
    if room_from_blob and room_from_blob != location:
        description_lines.append(f"Salle: {room_from_blob}")
    if weeks:
        description_lines.append(f"Semaines: {weeks}")
    if notes:
        description_lines.append("Remarques: " + " | ".join(notes))
    if ev.get("department"):
        description_lines.append(f"Département: {_join_list(ev.get('department'))}")

    cal_event = Event()
    cal_event.add("summary", title)
    cal_event.add("dtstart", start)
    cal_event.add("dtend", end)
    cal_event.add("dtstamp", dt.datetime.now(dt.timezone.utc))
    cal_event.add("uid", f"{event_key(ev)}@celcat-to-ics")
    if location:
        cal_event.add("location", location)
    if description_lines:
        cal_event.add("description", "\n".join(description_lines))

    return cal_event, None


def build_ics(
    events: List[Dict[str, Any]], calendar_name: str
) -> Tuple[Calendar, List[str]]:
    """Convertit une liste d'événements JSON Celcat en calendrier ICS.

    Retourne (calendrier, lignes_de_log) — lignes_de_log liste les
    événements ignorés (dates manquantes ou illisibles) et pourquoi.
    """
    cal = Calendar()
    cal.add("prodid", "-//celcat-to-ics//FR")
    cal.add("version", "2.0")
    cal.add("x-wr-calname", calendar_name)
    cal.add("x-wr-timezone", "Europe/Paris")

    log_lines: List[str] = []
    skipped = 0
    for ev in events:
        cal_event, reason = event_from_json(ev)
        if cal_event is None:
            skipped += 1
            log_lines.append(
                f"IGNORÉ id={ev.get('id')!r} raison={reason} "
                f"raw={ {k: v for k, v in ev.items() if k in ('id', 'start', 'end', 'description', 'notes', 'modules', 'eventCategory')}!r}"
            )
            continue
        cal.add_component(cal_event)

    if skipped:
        logger.warning(
            "%d événement(s) ignoré(s) lors de la génération de l'ICS.", skipped
        )

    return cal, log_lines
